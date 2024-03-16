import time
from pathlib import Path
from detect import run
import yaml
from loguru import logger
import os
import boto3
import json
import requests
import uuid

images_bucket = os.environ['BUCKET_NAME']
queue_name = os.environ['SQS_QUEUE_NAME']
region_name = 'us-west-1'

sqs_client = boto3.client('sqs', region_name=region_name)
s3_client = boto3.client('s3', region_name=region_name)
dynamodb = boto3.resource('dynamodb', region_name=region_name)
dynamodb_table_name = 'jihad'
table = dynamodb.Table(dynamodb_table_name)

with open("data/coco128.yaml", "r") as stream:
    names = yaml.safe_load(stream)['names']


def cleanup(original_img_path, prediction_id):
    # Add cleanup logic here
    pass


def consume():
    while True:
        response = sqs_client.receive_message(QueueUrl=queue_name, MaxNumberOfMessages=1, WaitTimeSeconds=5)

        if 'Messages' in response:
            message = response['Messages'][0]['Body']
            receipt_handle = response['Messages'][0]['ReceiptHandle']

            # Initialize variables outside the try block
            original_img_path = None
            prediction_id = None

            try:
                # Attempt to load the JSON data from the message
                msg_data = json.loads(message)

                message_id = response['Messages'][0]['MessageId']
                unique_identifier = str(uuid.uuid4())
                prediction_id = f"{message_id}/{unique_identifier}"

                logger.info(f'prediction: {prediction_id}. start processing')

                # Extract information from the message
                img_name = msg_data['img_name']
                chat_id = msg_data['chat_id']

                # Download the image from S3
                logger.info('Downloading image from S3...')
                original_img_path = download_image_from_s3(img_name)

                logger.info(f'prediction: {prediction_id}/{original_img_path}. Download img completed')

            except json.decoder.JSONDecodeError as e:
                logger.error(f"Error decoding JSON message: {e}")
                logger.error(f"Invalid JSON message content: {message}")
                # Log the entire traceback for better debugging
                logger.error("", exc_info=True)

            except Exception as e:
                logger.error(f"An error occurred: {e}")
                # Log the entire traceback for better debugging
                logger.error("", exc_info=True)

            finally:
                # Delete the message from the queue as the job is considered as DONE
                sqs_client.delete_message(QueueUrl=queue_name, ReceiptHandle=receipt_handle)

                # Move any cleanup logic here that should execute regardless of success or failure
                cleanup(original_img_path, prediction_id)

                if prediction_id:
                    try:
                        # Predicts the objects in the image only if prediction_id is not None
                        logger.info('Running object detection...')
                        run(
                            weights='yolov5s.pt',
                            data='data/coco128.yaml',
                            source=original_img_path,
                            project='static/data',
                            name=prediction_id,
                            save_txt=True
                        )

                        logger.info(f'prediction: {prediction_id}/{original_img_path}. done')

                        # Uploads the predicted image to S3
                        predicted_img_path = upload_predicted_image_to_s3(prediction_id, original_img_path)

                        # Parse prediction labels and create a summary
                        labels = parse_prediction_labels(prediction_id, original_img_path)

                        logger.info(f'prediction: {prediction_id}/{original_img_path}. prediction summary:\n\n{labels}')

                        # Store the prediction_summary in a DynamoDB table
                        store_prediction_summary_in_dynamodb(prediction_id, original_img_path, predicted_img_path, labels, chat_id)

                        # Perform a GET request to Polybot to `/results` endpoint
                        send_get_request_to_polybot(prediction_id, chat_id)
                    except Exception as e:
                        logger.error(f"An error occurred during object detection: {e}")
                        # Log the entire traceback for better debugging
                        logger.error("", exc_info=True)


def download_image_from_s3(img_name):
    response = s3_client.get_object(Bucket=images_bucket, Key=img_name)
    image_data = response['Body'].read()

    # Save the image locally for processing
    local_img_path = f'/tmp/{img_name}'
    with open(local_img_path, 'wb') as f:
        f.write(image_data)

    return local_img_path


def upload_predicted_image_to_s3(prediction_id, original_img_path):
    predicted_img_path = f'static/data/{prediction_id}/{original_img_path.split("/")[-1]}'

    # Read the predicted image
    with open(original_img_path, 'rb') as f:
        predicted_image_data = f.read()

    # Upload the predicted image to S3
    s3_client.put_object(Bucket=images_bucket, Key=predicted_img_path, Body=predicted_image_data)

    return predicted_img_path


def parse_prediction_labels(prediction_id, original_img_path):
    pred_summary_path = Path(f'static/data/{prediction_id}/labels/{original_img_path.split("/")[-1].split(".")[0]}.txt')

    if pred_summary_path.exists():
        with open(pred_summary_path) as f:
            labels = f.read().splitlines()
            labels = [line.split(' ') for line in labels]
            labels = [{
                'class': names[int(l[0])],
                'cx': float(l[1]),
                'cy': float(l[2]),
                'width': float(l[3]),
                'height': float(l[4]),
            } for l in labels]

        return labels
    else:
        return []


def store_prediction_summary_in_dynamodb(prediction_id, original_img_path, predicted_img_path, labels, chat_id):
    table.put_item(
        Item={
            'chat_id': chat_id,
            'PredictionId': prediction_id,
            'OriginalImagePath': original_img_path,
            'PredictedImagePath': predicted_img_path,
            'Labels': json.dumps(labels),
            'Timestamp': str(int(time.time()))
        }
    )


def send_get_request_to_polybot(prediction_id, chat_id):
    polybot_endpoint = 'polybotjihad.devops-int-college.com'
    polybot_url = f'https://{polybot_endpoint}/results?predictionId={prediction_id}&chatId={chat_id}'

    # Use requests library to make a GET request
    response = requests.get(polybot_url)

    # Optionally, log the response
    logger.info(f"Polybot response: {response.text}")


if __name__ == "__main__":
    consume()
