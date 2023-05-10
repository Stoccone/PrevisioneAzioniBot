import telebot
import math
import pandas_datareader as web 
from io import BytesIO
import numpy as np 
import pandas as pd 
from sklearn.preprocessing import MinMaxScaler 
from keras.models import Sequential, load_model
from keras.layers import Dense, LSTM 
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import yfinance as yf
from telebot import types
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import datetime as dtt
from datetime import datetime, timedelta


bot = telebot.TeleBot("6101110999:AAFwCPBLiHm1v0ySn92aeNJqecHXh44ETg8") #t.me/ProgettoPrevisioneAzioniGPO_bot
scaler = MinMaxScaler(feature_range = (0,1)).fit(np.array([11.261428833007812, 73.4124984741211]).reshape(-1, 1))


@bot.message_handler(commands=['start'])
def send_welcome(message):
  bot.reply_to(message, "This bot uses an ML model in the field of stock prediction :)")


@bot.message_handler(commands=['help'])
def send_welcome(message):
	bot.reply_to(message, "/view <ticker> <start_date> <end_date> (date format: YYYY-MM-DD): view graph.\n/predict <ticker> <start_date> <end_date> (date format: YYYY-MM-DD): displays the prediction graph of the selected period and actual values.\n/predicttomorrow: view the graph of the past 2 months and the price prediction for the next stock exchange close.")


# Funzione per verificare se un ticker di azione è valido
def is_valid_ticker(ticker):
	try:
		yf.Ticker(ticker).info
		return True
	except:
		return False
    
    
def predict(message):
	# Esegue il parsing del comando per ottenere ticker e date
	command_parts = message.text.split()
	if len(command_parts) != 4 or command_parts[1] == "" or command_parts[2] == "" or command_parts[3] == "":
		bot.reply_to(message, "Command instructions: <ticker> <start_date> <end_date> (date format: YYYY-MM-DD)")
		return
	ticker = command_parts[1].upper()
	start_date = command_parts[2]
	end_date = command_parts[3]

	# Verifica se il ticker è valido
	if not is_valid_ticker(ticker):
		bot.reply_to(message, f"Ticker not valid: {ticker}")
		return

	# Verifica se le date sono valide
	try:
		start_date_dt = datetime.strptime(start_date, "%Y-%m-%d")
		end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")
	except ValueError:
		bot.reply_to(message, "Invalid date format, please try again")
		return

	# Verifica se le date sono coerenti con la data odierna
	if start_date_dt > datetime.now() or end_date_dt > datetime.now():
		bot.reply_to(message, "Forecast dates cannot be later than today's date, try again")
		return
	if end_date_dt < start_date_dt:
		bot.reply_to(message, "The forecast end date must be later than the forecast start date, try again")
		return

	# Verifica se esistono dati storici per il ticker e il periodo selezionato
	data = yf.download(ticker, start=start_date, end=end_date, group_by='ticker')
	if data.empty:
		bot.reply_to(message, f"There is no historical data for the ticker {ticker} in the selected period")
		return

	return ticker, start_date, end_date


# Funzione per gestire il comando /start
@bot.message_handler(commands=['view'])
def create_chart(message):
	# Esegue la funzione predict per ottenere le date
	dates = predict(message)
	if dates is None:
		return
	# Parsing delle date
	ticker, start_date, end_date = dates
	# Scarica i dati e crea il grafico
	try:
		data = yf.download(ticker, start=start_date, end=end_date)
		plt.figure(figsize=(16,8))
		plt.title('Close Price History')
		plt.plot(data['Close'])
		plt.xlabel('Date', fontsize=18)
		plt.ylabel('Close Price USD ($)', fontsize=18) 
		# Converte il grafico in un'immagine e la salva come buffer
		buf = BytesIO()
		plt.savefig(buf, format='png')
		buf.seek(0)
		# Invia il grafico come foto
		bot.send_photo(chat_id=message.chat.id, photo=buf)
		#bot.send_message(message.chat.id, "Ecco il grafico")
	except:
		bot.send_message(chat_id=message.chat.id, text="An error occurred while creating the chart. Make sure that the action symbol and the selected dates are correct and try again")


@bot.message_handler(commands=['predicttomorrow'])
def predict_stock_price(message):
	model = load_model("aapl_model.h5")
	# Prendi i dati degli ultimi 60 giorni per creare la sequenza temporale
	new_data = yf.download("AAPL", start=dtt.date.today() - dtt.timedelta(days=12*30), end=dtt.date.today().strftime("%Y-%m-%d")).filter(['Close'])
	scaled_data = scaler.transform(new_data)
	test_data = scaled_data
	x_test = []
	y_test = []
	for i in range(60, len(test_data)):
		x_test.append(test_data[i-60:i, 0]) 
		y_test.append(test_data[i, 0]) 
	x_test = np.array(x_test)
	x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1 ))
	model = load_model("aapl_model.h5")
	predictions = model.predict(x_test)
	predictions = scaler.inverse_transform(predictions)
	valid = new_data[60:].copy()
	valid['Predictions'] = predictions
	plt.figure(figsize=(16,8))
	#plt.title('Model')
	plt.xlabel('Date', fontsize=18)
	plt.ylabel('Close Price USD ($)', fontsize=18)
	plt.plot(valid[['Close', 'Predictions']])
	plt.legend(['Actual', 'Predictions'], loc='lower right')
	buf = BytesIO()
	plt.savefig(buf, format='png')
	buf.seek(0)
	bot.send_photo(chat_id=message.chat.id, photo=buf)
	last_60_days = new_data[-60:].values
	last_60_days_scaled = scaler.transform(last_60_days)
	x_test = np.array([last_60_days_scaled])
	x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))
	pred_price = model.predict(x_test)
	pred_price = scaler.inverse_transform(pred_price)
	bot.reply_to(message, f"The predicted price for AAPL is {pred_price[0][0]:.2f}")


@bot.message_handler(commands=['predict'])
def predizioneAndamento(message):
	# Esegue la funzione predict per ottenere le date
	dates = predict(message)
	if dates is None:
		return
	# Parsing delle date
	ticker, start_date, end_date = dates
	df = yf.download(ticker, start=start_date, end=end_date)
	if len(df) < 60:
		bot.reply_to(message, "You must select an interval with more than 60 working days")
	else: 
		dataset = df.filter(['Close']).values
		scaled_data = scaler.transform(dataset)
		test_data = scaled_data
		x_test = []
		y_test = []
		for i in range(60, len(test_data)):
				x_test.append(test_data[i-60:i, 0]) 
				y_test.append(test_data[i, 0]) 
		x_test = np.array(x_test)
		x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1 ))
		model = load_model("aapl_model.h5")
		predictions = model.predict(x_test)
		predictions = scaler.inverse_transform(predictions)
		valid = df[60:].copy()
		valid['Predictions'] = predictions
		plt.figure(figsize=(16,8))
		#plt.title('Model')
		plt.xlabel('Date', fontsize=18)
		plt.ylabel('Close Price USD ($)', fontsize=18)
		plt.plot(valid[['Close', 'Predictions']])
		plt.legend(['Actual', 'Predictions'], loc='lower right')
		buf = BytesIO()
		plt.savefig(buf, format='png')
		buf.seek(0)
		bot.send_photo(chat_id=message.chat.id, photo=buf)
               
# Impostazione dei comandi e delle descrizioni da mostrare come suggerimenti
commands = [
	telebot.types.BotCommand('help', 'view instructions'),
	telebot.types.BotCommand('view', 'view graph: <ticker> <start_date> <end_date> (date format: YYYY-MM-DD)'),
	telebot.types.BotCommand('predict', 'displays the prediction graph of the selected period and actual values: <ticker> <start_date> <end_date> (date format: YYYY-MM-DD)'),
	telebot.types.BotCommand('predicttomorrow', 'view the graph of the past 2 months and the price prediction for the next stock exchange close'),
]
bot.set_my_commands(commands)

bot.infinity_polling()
