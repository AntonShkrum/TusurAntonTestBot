# -*- coding: cp1251 -*-
from ctypes import resize
from tkinter import Message
import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup

HOST = "https://timetable.tusur.ru/"
URL = 'https://timetable.tusur.ru/faculties/'
HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.35'
    }

def get_html(url, params=''):
    r = requests.get(url, headers = HEADERS, params=params)
    return r

def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    par = []
    global m
    from datetime import datetime, timedelta 
    now = datetime.now()
    sep = datetime(now.year if now.month >= 9 else now.year - 1, 9, 1)
    d1 = sep - timedelta(days=sep.weekday())
    d2 = now - timedelta(days=now.weekday())
    parity = ((d2 - d1).days // 7) % 2
    week = format("even" if parity else "odd")
    for n in range(0, 7):
        items = soup.find(class_="table table-bordered table-condensed hidden-xs hidden-sm table-lessons " + week).find_all('td', class_='lesson_cell day_'+ str(n)+' current_day')
        for item in items:
            if item.find('h4') is not None:
                par.append(
                    {
                    'lessons_nazvinie':item.find('div', class_='modal-header').find('h4').get_text(' ', strip=True),
                    'lessons_time':item.find('div', class_='modal-content').find('p').find_next('p').find_next('p').get_text(' ', strip=True),
                    'lessons_vid':item.find('div', class_='modal-content').find('p').get_text(' ', strip=True),
                    'lessons_mesto':item.find('div', class_='modal-content').find('p').find_next('p').find_next('p').find_next('p').get_text(' ', strip=True),
                    'lessons_teacher':item.find('div', class_='modal-content').find('p').find_next('p').find_next('p').find_next('p').find_next('p').get_text(' ', strip=True),
                    'lessons_group':item.find('div', class_='modal-content').find('p').find_next('p').find_next('p').find_next('p').find_next('p').find_next('p').get_text(' ', strip=True),
                    }
                )
                m+=1
    return par, m

def out(par, m):
    with open(r"test.txt", "w") as file:
        for n in range(0, m):
            for value in list(par[n].values()):
                file.write(value + '\n')
            file.write('\n')

#Ботинок
bot = telebot.TeleBot('5699590709:AAGDo97tyzkTgG-l7nF6Nomnft9EHlcNF0g')
group = ''
facultet = ''
m = 0

markup = types.ReplyKeyboardMarkup(resize_keyboard = True, row_width=2) 
start = types.KeyboardButton('/start') 
raspisanie = types.KeyboardButton('/raspisanie')
avtomat = types.KeyboardButton('/avtomat') 
zachet = types.KeyboardButton('/zachet') 
settings = types.KeyboardButton('/settings') 
instruction = types.KeyboardButton('/instruction') 
markup.add(start, raspisanie, avtomat, zachet, settings, instruction)


@bot.message_handler(commands=['start'])
def start(message):
    mess = f'Привет, <b>{message.from_user.first_name}</b>'
    bot.send_message(message.chat.id, mess, parse_mode='html', reply_markup=markup)
    bot.send_message(message.chat.id, f'Я бот ТУСУРа! У меня есть несколько функций, которые могут быть для тебя полезными. Первая функция - /raspisanie, эта команда покажет тебе расписание на сегодня. Для начала работы с этой командой необходимо настроить группу и факультет через команду    /settings.', parse_mode='html')
    bot.send_message(message.chat.id, f'Также ты можешь узнать как получить зачет или автомат через команды: /zachet, /avtomat. Если ты только поступил в ТУСУР, ты можешь посмотреть на инструкцию для первокурсников нажав на /instruction.', parse_mode='html')

@bot.message_handler(commands=['instruction'])
def instruction(message):
    photo = open('instrukt.png', 'rb')
    bot.send_photo(message.chat.id, photo)


@bot.message_handler(commands=['settings'])
def settings(message):
    bot.send_message(message.chat.id, f'Введи факультет(в формате "rtf, fvs, fet, ef, yuf, zivf, rkf, fsu, fit, gf, fb"): ', parse_mode='html')
    bot.register_next_step_handler(message, get_FACULTET)

def get_FACULTET(message):
    global facultet
    facultet = message.text
    bot.send_message(message.chat.id, f'Введи номер группы(в формате "111-1, v-11b, 111-m"): ', parse_mode='html')
    bot.register_next_step_handler(message, get_GROUP)

def get_GROUP(message):
    global group
    group = message.text
    bot.send_message(message.chat.id, f'Настройки успешно установлены. Если необходимо поменять настройки, введи /settings. Сейчас нажми на /raspisanie, чтобы увидеть твое расписание на сегодня.', parse_mode='html')


@bot.message_handler(commands=['raspisanie'])
def raspisanie(message):
    global group
    global facultet
    global m
    if get_html(URL+str(facultet)+'/groups/'+str(group)).status_code == 200:
        html = get_html(URL+str(facultet)+'/groups/'+str(group))
        par, m = get_content(html.text)
        if m > 0:
            out(par, m)
            with open(r"test.txt", "r") as file:
                mess = file.read()
            bot.send_message(message.chat.id, f'Твое расписание на сегодня: ', parse_mode='html')
            bot.send_message(message.chat.id, mess, parse_mode='html')
        else:
            bot.send_message(message.chat.id, f'Сегодня пар нет!', parse_mode='html')
    else:
        bot.send_message(message.chat.id, f'Настройки установлены неверно. Для смены настроек введи /settings', parse_mode='html')


@bot.message_handler(commands=['avtomat'])
def avtomat(message):
    bot.send_message(message.chat.id, f'«Автомат» как форма оценки знаний должен быть отмечен в «Положениях о зачётах и экзаменах» учебного учреждения, прописаны конкретные критерии, которым надо соответствовать, чтобы вам оценку ставили автоматически. Выполняете все требования — получаете «автомат» по учебной дисциплине.', parse_mode='html')

@bot.message_handler(commands=['zachet'])
def zachet(message):
    bot.send_message(message.chat.id, f'Зачёт можно получить автоматом, если сам преподаватель сочтёт это возможным. Официально ничего не закреплено, и в этом случае необходимо, чтобы преподаватель вас отметил для себя как старательного и добросовестного студента. Субъективное мнение будет играть весомую роль, порой даже большее, чем все учебные заслуги.', parse_mode='html')


bot.infinity_polling()



