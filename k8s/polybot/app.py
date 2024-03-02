import flask
from flask import request, jsonify
import os
from bot import ObjectDetectionBot
import logging
import boto3
import json
from loguru import logger
from botocore.exceptions import NoCredentialsError


app = flask.Flask(__name__)


# Create a Secrets Manager client for a specific region
secrets_manager_client = boto3.client('secretsmanager', region_name='us-west-1')

try:
    secret_name = 'TELEGRAM_TOKEN_Jihad'
    response = secrets_manager_client.get_secret_value(SecretId=secret_name)
    TELEGRAM_TOKEN = response['SecretString']
except Exception as e:
    logging.error(f"Error retrieving secret '{secret_name}': {str(e)}")


TELEGRAM_TOKEN = json.loads(TELEGRAM_TOKEN)['TELEGRAM_TOKEN']
TELEGRAM_APP_URL = os.environ.get('TELEGRAM_APP_URL')


# Initialize ObjectDetectionBot instance
bot_instance = ObjectDetectionBot()
bot_instance.set_tokens_from_flask(TELEGRAM_TOKEN, TELEGRAM_APP_URL)


@app.route('/', methods=['GET'])
def index():
    return 'Ok'


@app.route(f'/{TELEGRAM_TOKEN}/', methods=['POST'])
def webhook():
    req = request.get_json()
    bot_instance.handle_message(req['message'])
    return 'Ok'


@app.route(f'/results', methods=['GET'])
def results():
    chat_id = request.args.get('chatId')
    results = bot_instance.retrieve_results_from_dynamodb(chat_id)

    # Log the entire results dictionary for debugging
    logger.info(f"Results: {results}")

    if results:
        # Extract labels from the results
        labels = results.get('labels', [])

        # Prepare a summary of detected objects and their counts
        object_counts = {}
        for label in labels:
            class_name = label.get('class', 'Unknown')
            object_counts[class_name] = object_counts.get(class_name, 0) + 1

        # Prepare the response text
        response_text = "\n".join([f"{i + 1}- {class_name}: {count}" for i, (class_name, count) in enumerate(object_counts.items())])

        # You can use the 'send_text' method from your ObjectDetectionBot class
        bot_instance.send_text(chat_id, f"Object detected:\n{response_text}")

        return 'Ok'
    else:
        return 'No results found'


@app.route('/health')
def health_check():
    return 'OK', 200


@app.route('/loadTest/', methods=['POST'])
def load_test():
    req = request.get_json()
    bot.handle_message(req['message'])
    return 'Ok'


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8443)

