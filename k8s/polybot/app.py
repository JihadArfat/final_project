import flask
from flask import request, jsonify
import os
from bot import ObjectDetectionBot
import logging
from loguru import logger
import base64

app = flask.Flask(__name__)

# Retrieve the TELEGRAM_TOKEN from Kubernetes secret
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_APP_URL = os.environ.get('TELEGRAM_APP_URL')

# Retrieve the certificate data from the Kubernetes secret
cert_data_base64 = os.getenv('bot-certificate')

# Check if TELEGRAM_TOKEN exists
if not TELEGRAM_TOKEN:
    logger.error("TELEGRAM_TOKEN not found in environment variables")
    # Handle the situation when TELEGRAM_TOKEN is not found, e.g., set a default value or raise an exception
    # Example:
    # raise ValueError("TELEGRAM_TOKEN not found in environment variables")
else:
    TELEGRAM_TOKEN = TELEGRAM_TOKEN.strip()  # Remove leading/trailing whitespace if necessary

# Check if CERT_DATA_BASE64 exists
if not cert_data_base64:
    logger.error("CERT_DATA_BASE64 not found in environment variables")
    # Handle the situation when CERT_DATA_BASE64 is not found
    # Example:
    # raise ValueError("CERT_DATA_BASE64 not found in environment variables")

# Decode the base64-encoded certificate data
cert_data = base64.b64decode(cert_data_base64)

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
