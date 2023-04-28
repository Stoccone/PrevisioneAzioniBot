import telebot

bot = telebot.TeleBot("6248512780:AAHL0E69kmNatnoU-DBMZMJ_xBYM8C0WEUA")

@bot.message_handler(commands=['start'])
def send_welcome(message):
	bot.reply_to(message, "Ciao, cosa vuoi fare?")
	# Aspetta l'input dell'utente
	bot.register_next_step_handler(message, handle_input)
# Gestisce l'input dell'utente
def handle_input(message):
    # Memorizza l'input dell'utente
    input_text = message.text
    bot.reply_to(message, "Ok allora: " + input_text)

@bot.message_handler(commands=['help'])
def send_welcome(message):
	bot.reply_to(message, "Ci siamo :)")

	
@bot.message_handler(commands=['kill'])
def handle_stop(message):
    # Interrompe il polling del bot
	bot.reply_to(message, "Hai terminato questo bot :(")
	bot.stop_polling()


@bot.message_handler(func=lambda message: True)
 # Invia un messaggio di errore quando il bot riceve un comando non valido
def echo_all(message):
	bot.reply_to(message, "Mi dispiace, non ho capito il comando che hai inviato.")

bot.infinity_polling()


