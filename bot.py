import telebot
import math
import pandas_datareader as web 
from io import BytesIO
import numpy as np 
import pandas as pd 
from sklearn.preprocessing import MinMaxScaler 
from keras.models import Sequential, load_model
from keras.layers import Dense, LSTM 
import matplotlib.pyplot as plt
import yfinance as yf

bot = telebot.TeleBot("6248512780:AAHL0E69kmNatnoU-DBMZMJ_xBYM8C0WEUA")

@bot.message_handler(commands=['start'])
def send_welcome(message):
	bot.reply_to(message, "Questo è un bot sperimentale che fa schifo")

@bot.message_handler(commands=['help'])
def send_welcome(message):
	bot.reply_to(message, "Scrivci /prevedi")

@bot.message_handler(commands=['prevedi'])

def send_welcome(message):
	data = yf.download("AAPL", start="2022-1-1", end="2022-7-7").filter(['Close'])
	dataset = data.values

	scaler = MinMaxScaler(feature_range= (0,1))
	scaled_data = scaler.fit_transform(dataset)
	test_data = scaled_data[len(dataset) - 60: , :]
	x_test = []
	y_test = dataset
	for i in range(60, len(test_data)) :
		x_test.append(test_data[i-60:i, 0])
	x_test = np.array(x_test)
	x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1 ))
	
	model = load_model("aapl_model.h5")
	predictions = model.predict(x_test)
	predictions = scaler.inverse_transform(predictions)

	valid = data
	valid['Predictions'] = predictions
	plt.figure(figsize=(16,8))
	plt.title('Model')
	plt.xlabel('Date', fontsize=18)
	plt.ylabel('Close Price USD ($)', fontsize=18)
	plt.plot (valid[['Close', 'Predictions']])
	plt.legend(['Val', 'Predictions'], loc='lower right')

	plt.savefig(buf, format='png')
	buf = BytesIO()
	buf.seek(0)
	plt.close()

	bot.send_photo(chat_id=message.chat.id, photo=buf)

	

@bot.message_handler(func=lambda message: True)
def echo_all(message):
	bot.reply_to(message, message.text)

bot.infinity_polling()
