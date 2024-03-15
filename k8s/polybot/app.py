import flask
from flask import request, jsonify
import os
from bot import ObjectDetectionBot
import logging
from loguru import logger
import base64

app = flask.Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Retrieve the TELEGRAM_TOKEN from Kubernetes secret
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_APP_URL = os.environ.get('TELEGRAM_APP_URL')

# Read the certificate file from its mounted path
cert_path = '/etc/ssl/certs/tls.crt'

# Check if TELEGRAM_TOKEN exists
if not TELEGRAM_TOKEN:
    logger.error("TELEGRAM_TOKEN not found in environment variables")
    # Handle the situation when TELEGRAM_TOKEN is not found, e.g., set a default value or raise an exception
    # Example:
    # raise ValueError("TELEGRAM_TOKEN not found in environment variables")
else:
    TELEGRAM_TOKEN = TELEGRAM_TOKEN.strip()  # Remove leading/trailing whitespace if necessary

# Check if the certificate file exists
if os.path.exists(cert_path):
    logger.info("Certificate file found.")
    # Initialize ObjectDetectionBot instance
    bot_instance = ObjectDetectionBot()
    bot_instance.set_tokens_from_flask(TELEGRAM_TOKEN, TELEGRAM_APP_URL, cert_path)
else:
    logger.error(f"Certificate file not found at path: {cert_path}")

app.config['DEBUG'] = True

@app.route('/', methods=['GET'])
def index():
    return 'Ok'


@app.route(f'/{TELEGRAM_TOKEN}/', methods=['POST'])
def webhook():
    try:
        req = request.get_json()
        logger.info(f"Incoming request: {req}")

        if 'message' in req:
            bot_instance.handle_message(req['message'])
        else:
            logger.warning("Received request with no 'message' field.")

        return 'Ok'
    except Exception as e:
        logger.error(f"Error handling webhook request: {e}")
        return 'Error', 500

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
