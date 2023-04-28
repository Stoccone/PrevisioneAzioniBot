import telebot

bot = telebot.TeleBot("6248512780:AAHL0E69kmNatnoU-DBMZMJ_xBYM8C0WEUA")

@bot.message_handler(commands=['start'])
def send_welcome(message):
	bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler(commands=['help'])
def send_welcome(message):
	bot.reply_to(message, "Ci siamo :)")

@bot.message_handler(func=lambda message: True)
 # Invia un messaggio di errore quando il bot riceve un comando non valido
def echo_all(message):
	bot.reply_to(message, "Mi dispiace, non ho capito il comando che hai inviato.")

bot.infinity_polling()