import telebot

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
bot_token = "6920865650:AAFlBnucpRzJhexXQQSEdYaZ50EFiU60vn4"

# Initialize the bot
bot = telebot.TeleBot(token=bot_token)

# Replace 'PHOTO_URL' with the URL of the photo you want to send
photo_url = "https://jihadar.s3.us-west-1.amazonaws.com/dogs2.jpg"

# Replace 'CHAT_ID' with the chat ID of your bot (you can get it from the webhook request)
chat_id = "6247081496"

# Send the photo
bot.send_photo(chat_id=chat_id, photo=photo_url)
