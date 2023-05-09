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

from tensorflow.keras.models import load_model

bot = telebot.TeleBot("6248512780:AAHL0E69kmNatnoU-DBMZMJ_xBYM8C0WEUA")

@bot.message_handler(commands=['start'])
def send_welcome(message):
	bot.reply_to(message, "Ciao, questo bot viene utilizzato per prevedere tramite un modello di Machine Learning il prezzo di una determinata azione :)")

@bot.message_handler(commands=['help'])
def send_welcome(message):
	bot.reply_to(message, "Per visualizzare il grafico di una determinata azione scrivi /view")



@bot.message_handler(commands=['view'])
def send_welcome(message):
    bot.send_message(chat_id=message.chat.id, text="Inserisci un'azione da visualizzare:")
    bot.register_next_step_handler(message, select_date_range)

def select_date_range(message):
    ticker = message.text.upper()
    df = yf.download(ticker)

    years = df.index.year.unique()
    year_buttons = [types.KeyboardButton(str(year)) for year in years]
    year_markup = types.ReplyKeyboardMarkup(resize_keyboard=True).add(*year_buttons)
    bot.send_message(chat_id=message.chat.id, text="Seleziona l'anno di inizio:", reply_markup=year_markup)

    bot.register_next_step_handler(message, select_start_month, ticker, df)

def select_start_month(message, ticker, df):
    selected_year = int(message.text)

    months = [i.strftime('%B') for i in pd.date_range(start=f'{selected_year}-01-01', end=f'{selected_year}-12-01', freq='MS')]
    month_buttons = [types.KeyboardButton(month) for month in months]
    month_markup = types.ReplyKeyboardMarkup(resize_keyboard=True).add(*month_buttons)
    bot.send_message(chat_id=message.chat.id, text='Seleziona il mese di inizio:', reply_markup=month_markup)

    bot.register_next_step_handler(message, select_end_year, ticker, df, selected_year)

def select_end_year(message, ticker, df, selected_start_year):
    selected_start_month = message.text
    selected_start_date = datetime.strptime(f'{selected_start_year}-{selected_start_month}-01', '%Y-%B-%d')

    years = df.loc[selected_start_date:].index.year.unique()
    year_buttons = [types.KeyboardButton(str(year)) for year in years]
    year_markup = types.ReplyKeyboardMarkup(resize_keyboard=True).add(*year_buttons)
    bot.send_message(chat_id=message.chat.id, text="Seleziona l'anno di fine:", reply_markup=year_markup)

    bot.register_next_step_handler(message, select_end_month, ticker, df, selected_start_date)

def select_end_month(message, ticker, df, selected_start_date):
    selected_end_year = int(message.text)

    months = [i.strftime('%B') for i in pd.date_range(start=f'{selected_end_year}-01-01', end=f'{selected_end_year}-12-01', freq='MS') if i >= selected_start_date]
    month_buttons = [types.KeyboardButton(month) for month in months]
    month_markup = types.ReplyKeyboardMarkup(resize_keyboard=True).add(*month_buttons)
    bot.send_message(chat_id=message.chat.id, text='Seleziona il mese di fine:', reply_markup=month_markup)

    bot.register_next_step_handler(message, generate_plot, ticker, df, selected_start_date, selected_end_year)

def generate_plot(message, ticker, df, selected_start_date, selected_end_year):
    selected_end_month = message.text
    selected_end_date = datetime.strptime(f'{selected_end_year}-{selected_end_month}-01', '%Y-%B-%d')



    df = yf.download(ticker, start=selected_start_date, end=selected_end_date)

    # Crea il grafico dello storico considerando solo la colonna close
    plt.figure(figsize=(16,8))
    plt.title('Close Price History')
    plt.plot(df['Close'])
    plt.xlabel('Date', fontsize=18)
    plt.ylabel('Close Price USD ($)', fontsize=18) 

    # Converte il grafico in un'immagine e la salva come buffer
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # Invia il grafico come foto
    bot.send_photo(chat_id=message.chat.id, photo=buf)

@bot.message_handler(func=lambda message: True)
def echo_all(message):
	bot.reply_to(message, message.text)

bot.infinity_polling()
