import telebot

bot = telebot.TeleBot("6248512780:AAHL0E69kmNatnoU-DBMZMJ_xBYM8C0WEUA")

@bot.message_handler(commands=['start'])
def send_welcome(message):
	bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler(commands=['help'])
def send_welcome(message):
	bot.reply_to(message, "PORCODIO")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
	bot.reply_to(message, message.text)

bot.infinity_polling()