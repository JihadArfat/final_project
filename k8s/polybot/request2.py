import telebot

# Replace 'YOUR_BOT_TOKEN' with your actual bot token obtained from BotFather
bot = telebot.TeleBot('6920865650:AAFlBnucpRzJhexXQQSEdYaZ50EFiU60vn4')

# Example of sending a message to a specific chat ID
chat_id = '6247081496'  # Replace with the chat ID where you want to send the message
message_text = 'Hello, this is a test message from Telebot!'
bot.send_message(chat_id, message_text)

# Example of sending a photo to a specific chat ID
photo_path = 'path/to/your/photo.jpg'  # Replace with the path to your photo
with open(photo_path, 'rb') as photo:
    bot.send_photo(chat_id, photo)

# You can perform various other actions supported by the Telegram Bot API using Telebot
# For example, sending files, stickers, handling callbacks, etc.

# Start the bot's pooling to continuously check for updates
# bot.infinity_polling()

