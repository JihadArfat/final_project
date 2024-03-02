import requests

TELEGRAM_TOKEN = '6920865650:AAFlBnucpRzJhexXQQSEdYaZ50EFiU60vn4'
TELEGRAM_APP_URL = 'https://polybotjihad.devops-int-college.com/'


webhook_url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={TELEGRAM_APP_URL}'


response = requests.post(webhook_url)

if response.status_code == 200:
    print('Webhook set successfully!')
else:
    print(f'Failed to set the webhook. Status code: {response.status_code}')

