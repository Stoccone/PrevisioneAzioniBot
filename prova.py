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
from datetime import datetime, timedelta

bot = telebot.TeleBot("6248512780:AAHL0E69kmNatnoU-DBMZMJ_xBYM8C0WEUA")


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
        bot.reply_to(message, "Utilizzo del comando: /predict <ticker> <data_inizio> <data_fine> (formato data: 'YYYY-MM-DD')")
        return
    ticker = command_parts[1].upper()
    start_date = command_parts[2]
    end_date = command_parts[3]

    # Verifica se il ticker è valido
    if not is_valid_ticker(ticker):
        bot.reply_to(message, f"Ticker non valido: {ticker}")
        return

    # Verifica se le date sono valide
    try:
        start_date_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        bot.reply_to(message, "Formato data non valido, riprova.")
        return

    # Verifica se le date sono coerenti con la data odierna
    if start_date_dt > datetime.now() or end_date_dt > datetime.now():
        bot.reply_to(message, "Le date di previsione non possono essere successive alla data odierna, riprova.")
        return
    if end_date_dt < start_date_dt:
        bot.reply_to(message, "La data di fine previsione deve essere successiva alla data di inizio previsione, riprova.")
        return

    # Verifica se esistono dati storici per il ticker e il periodo selezionato
    data = yf.download(ticker, start=start_date, end=end_date, group_by='ticker')
    if data.empty:
        bot.reply_to(message, f"Non esistono dati storici per il ticker {ticker} nel periodo selezionato.")
        return

    return ticker, start_date, end_date

# Funzione per gestire il comando /start
@bot.message_handler(commands=['predict'])
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
        bot.send_message(message.chat.id, "Eccoti il grafico")
    except:
        bot.send_message(chat_id=message.chat.id, text="Si è verificato un errore durante la creazione del grafico. Assicurati che il simbolo dell'azione e le date selezionate siano corretti e riprova.")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
	bot.reply_to(message, message.text)

bot.infinity_polling()