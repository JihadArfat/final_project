import telebot
from loguru import logger
import os
import boto3
import uuid
import time
import requests
from botocore.exceptions import NoCredentialsError
import json
import tempfile

class Bot:
    def __init__(self, token, telegram_chat_url, cert_data):
        cert_path = "/etc/ssl/certs/tls.crt"
        self.telegram_bot_client = telebot.TeleBot(token, certificate=cert_path)
        self.telegram_bot_client.remove_webhook()
        time.sleep(0.5)
        self.telegram_bot_client.set_webhook(url=f'{telegram_chat_url}/{token}/', timeout=60)
        logger.info(f'Telegram Bot information\n\n{self.telegram_bot_client.get_me()}')
        logger.info(f'Certificate data: {cert_data}')

    def send_text(self, chat_id, text):
        self.telegram_bot_client.send_message(chat_id, text)

    def send_text_with_quote(self, chat_id, text, quoted_msg_id):
        self.telegram_bot_client.send_message(chat_id, text, reply_to_message_id=quoted_msg_id)

    def is_current_msg_photo(self, msg):
        return 'photo' in msg

    def download_user_photo(self, msg):
        if not self.is_current_msg_photo(msg):
            raise RuntimeError(f'Message content of type \'photo\' expected')

        file_info = self.telegram_bot_client.get_file(msg['photo'][-1]['file_id'])
        data = self.telegram_bot_client.download_file(file_info.file_path)
        folder_name = file_info.file_path.split('/')[0]

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        with open(file_info.file_path, 'wb') as photo:
            photo.write(data)

        return file_info.file_path

    def send_photo(self, chat_id, img_path):
        if not os.path.exists(img_path):
            raise RuntimeError("Image path doesn't exist")

        self.telegram_bot_client.send_photo(
            chat_id,
            telebot.types.InputFile(img_path)
        )

    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')
        self.send_text(msg['chat']['id'], f'Your original message: {msg["text"]}')

class ObjectDetectionBot:
    def __init__(self):
        self.dynamodb_client = boto3.client('dynamodb', region_name='us-west-1')
        self.telegram_bot_client = None
        self.telegram_token = None
        self.telegram_app_url = None
        self.cert_path = None

    def set_tokens_from_flask(self, telegram_token, telegram_app_url, cert_path):
        self.telegram_token = telegram_token
        self.telegram_app_url = telegram_app_url
        self.cert_path = cert_path

        if self.telegram_token is None or self.telegram_app_url is None or self.cert_path is None:
            raise ValueError("TELEGRAM_TOKEN or TELEGRAM_APP_URL values are not defined or empty")

        self.setup_bot()

    def setup_bot(self):
        if self.cert_path is None:
            raise ValueError("Certificate file path is not provided.")

        self.telegram_bot_client = telebot.TeleBot(self.telegram_token)
        self.telegram_bot_client.remove_webhook()
        time.sleep(0.5)
        self.telegram_bot_client.set_webhook(url=f'{self.telegram_app_url}/{self.telegram_token}/', certificate=open(self.cert_path, 'rb'), timeout=60)
        logger.info(f'Telegram Bot information\n\n{self.telegram_bot_client.get_me()}')

    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')

        if self.is_current_msg_photo(msg):
            logger.info("Received a photo message.")
            photo_path = self.download_user_photo(msg)
            logger.info(f"Downloaded photo to: {photo_path}")

            if photo_path:
                # Upload the photo to S3
                img_name = self.upload_to_s3(photo_path, 'jihadar')
                logger.info(f"Uploaded photo to S3 with name: {img_name}")

                # Send a job to the SQS queue
                self.send_sqs_message(str(msg['chat']['id']), img_name)
                logger.info("Sent message to SQS queue.")

                # Send message to the Telegram end-user
                self.send_text(msg['chat']['id'], 'Your image is being processed. please dont wait...')
                logger.info("Sent message to Telegram user.")

    def is_current_msg_photo(self, msg):
        return 'photo' in msg

    def download_user_photo(self, msg):
        if not self.is_current_msg_photo(msg):
            raise RuntimeError(f'Message content of type \'photo\' expected')

        file_info = self.telegram_bot_client.get_file(msg['photo'][-1]['file_id'])
        data = self.telegram_bot_client.download_file(file_info.file_path)

        photo_path = os.path.join(os.getcwd(), file_info.file_path.split('/')[-1])

        with open(photo_path, 'wb') as photo:
            photo.write(data)

        return photo_path

    def upload_to_s3(self, photo_path, bucket_name):
        s3 = boto3.client('s3')
        try:
            with open(photo_path, 'rb') as photo_file:
                s3_key = os.path.basename(photo_path)
                s3.upload_fileobj(photo_file, bucket_name, s3_key)
                return s3_key
        except Exception as e:
            logger.error(f"Error uploading image to S3: {str(e)}")
            return None

    def send_sqs_message(self, chat_id, img_name):
        region = 'us-west-1'
        sqs = boto3.client('sqs', region_name=region)
        queue_url = 'https://sqs.us-west-1.amazonaws.com/352708296901/jihad'

        message_body = {
            'chat_id': chat_id,
            'img_name': img_name
        }

        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message_body),
            MessageAttributes={
                'PhotoPath': {
                    'DataType': 'String',
                    'StringValue': chat_id
                },
                'S3Key': {
                    'DataType': 'String',
                    'StringValue': img_name
                }
            }
        )

    def retrieve_results_from_dynamodb(self, chat_id):
        try:
            response = self.dynamodb_client.get_item(
                TableName='jihad',
                Key={
                    'chat_id': {'S': chat_id}

                }
            )

            # Check if the item was found
            if 'Item' in response:
               item = response['Item']
               # Extract relevant information from the DynamoDB item
               original_image_path = item.get('OriginalImagePath', {}).get('S', '')
               predicted_image_path = item.get('PredictedImagePath', {}).get('S', '')
               labels = item.get('Labels', {}).get('S', '[]')
               labels = json.loads(labels)

               # Return the retrieved results, including labels
               return {
                   'original_image_path': original_image_path,
                   'predicted_image_path': predicted_image_path,
                   'labels': labels
                }
            else:
                return None  # Item not found

        except NoCredentialsError:
            return {'error': 'AWS credentials not available or not valid.'}

    def send_text(self, chat_id, text):
        self.telegram_bot_client.send_message(chat_id, text)

