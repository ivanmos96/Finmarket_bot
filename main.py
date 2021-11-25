#библиотеки
import telebot
from telebot import types
#BeautifulSoup
import requests
from bs4 import BeautifulSoup
#Selenium
from selenium.webdriver.common.keys import Keys #модуль ввода данных
from selenium import webdriver #веб-драйвер
from webdriver_manager.chrome import ChromeDriverManager #Chrome - браузер
from selenium.webdriver.common.by import By
from time import sleep

driver = webdriver.Chrome(ChromeDriverManager().install())

# подключим токен
bot = telebot.TeleBot("2136961612:AAE-ybGpO5uVyj2nUlr7Fqy8plgUs7LFnzU")

# напишем, что делать нашему боту при команде старт
@bot.message_handler(commands=['start'])
def send_keyboard(message, text="Хочешь узнать о новостях с главной страницы Финмаркета? Выбери интересующие тебя новости!"):
    keyboard = types.ReplyKeyboardMarkup(row_width=2)  # наша клавиатура
    itembtn1 = types.KeyboardButton('Главные новости (новость + ссылка)') # создадим кнопку
    itembtn2 = types.KeyboardButton('Поиск новостей по запросу (за текущий год)')
    itembtn3 = types.KeyboardButton('Российские фондовые индексы RTS/MOEX')
    itembtn4 = types.KeyboardButton("Курс евро за год")
    itembtn5 = types.KeyboardButton('Курс доллара за год')
    itembtn6 = types.KeyboardButton('На сегодня пока всё.')
    keyboard.add(itembtn1, itembtn2) # добавим кнопки 1 и 2 на первый ряд
    keyboard.add(itembtn3, itembtn4, itembtn5, itembtn6)

    # пришлем это все сообщением и запишем выбранный вариант
    msg = bot.send_message(message.from_user.id,
                     text=text, reply_markup=keyboard)

    # отправим этот вариант в функцию, которая его обработает
    bot.register_next_step_handler(msg, callback_worker)

# парсинг новостей с главной страницы
def parcing_main():
    # формат ссылки страницы
    url = 'http://www.finmarket.ru/news/?nt=0&pg=1'
    # получим html код страницы
    response = requests.get(url)
    # html дерево
    tree = BeautifulSoup(response.content, 'html.parser')
    n = tree.find('div', {'class': "center_column"})
    # находим данные заголовок новости и дата
    news = n.find_all('div', {'class': "title"})
    dates = n.find_all('span', {'class': "date"})
    # список куда будем записывать данные
    parced_data = []
    # итерируемся по датам
    for i in range(len(dates)):
        # добавляем данные в наш список
        parced_data.extend({ news[i].text + '\n' +
            'http://www.finmarket.ru' + (news[i].a.get('href'))
        })
    parced_data_string = '\n // \n'.join(parced_data)
    print (parced_data)
    return (parced_data_string)

#парсинг новостей по запросу (за прошедший год)
def parcing_search(msg):
    print(msg.text)
    a = msg.text
    bot.send_message(msg.chat.id, 'Запомнил ваш запрос, на него потребуется время, выполняю...')
    driver.get('http://www.finmarket.ru')
    sleep(1)
    selector = 'body > div.content > div.head_menu > div.top_menu_left > a.top_menu_txt.blue2'
    #element = find_element_by_css_selector("element_css_selector")
    #element = driver.find_element(By.CSS_SELECTOR, "element_css_selector")
    #ss = driver.find_element_by_css_selector(selector)
    ss = driver.find_element(By.CSS_SELECTOR, selector)
    ss.click()
    sleep(1)
    selector = 'body > div.content > div.head_logo > div.socnet_box > a:nth-child(1)'
    ss = driver.find_element(By.CSS_SELECTOR, selector)
    ss.click()
    sleep(1)
    search = driver.find_element(By.CSS_SELECTOR,'body > div.content > div.main >' \
                                                 'div.left_wide > div.center_column' \
                                                 '> div:nth-child(1) > div > form >' \
                                                 'table:nth-child(1) > tbody > tr >' \
                                                 'td:nth-child(2) > input')
    search.click()
    search_term = a
    search.send_keys(search_term)
    # находим кнопку с начальной датой
    date = driver.find_element(By.CSS_SELECTOR,'body > div.content > div.main >' \
                                               'div.left_wide > div.center_column >' \
                                               'div:nth-child(1) > div > form > table:nth-child(2) >' \
                                               'tbody > tr:nth-child(1) > td:nth-child(5) > table >' \
                                               'tbody > tr > td:nth-child(2) > input')
    # удаляем последнюю цифру даты в ячейке
    date.send_keys(Keys.BACK_SPACE)
    date.send_keys(Keys.NUMPAD0)  # даты за 2020 годы нам хватит вполне, поэтому заменим дату начала с 2021 на 2020
    # нажимаем Показать, чтобы поиск новостей запустился
    show = driver.find_element(By.CSS_SELECTOR,'body > div.content > div.main > div.left_wide >' \
                                               'div.center_column > div:nth-child(1) > div > form >' \
                                               'table:nth-child(2) > tbody > tr:nth-child(2) > td >' \
                                               'input[type=image]:nth-child(1)')
    show.click()
    sleep(1)
    print(driver.current_url)
    url = driver.current_url
    # получим html код страницы
    response = requests.get(url)
    # html дерево
    tree = BeautifulSoup(response.content, 'html.parser')
    n = tree.find('div', {'class': "center_column"})
    # находим данные заголовок новости и дата
    news = n.find_all('div', {'class': "title"})
    dates = n.find_all('span', {'class': "date"})
    # список куда будем записывать данные
    parced_data = []
    # итерируемся по датам
    for i in range(len(dates)):
        # добавляем данные в наш список
        parced_data.extend({ news[i].text + '\n' +
            'http://www.finmarket.ru' + (news[i].a.get('href'))
        })
    parced_data_string = '\n // \n'.join(parced_data)
    print (parced_data)
    if parced_data_string == '':
        send_keyboard(msg, 'По вашему запросу ничего не найдено. Что нибудь еще?')
    else:
        send_keyboard(msg, parced_data_string)
        send_keyboard(msg, 'Прислал Вам новости по запросу. Что нибудь еще?')
    return (parced_data_string)

# привязываем функции к кнопкам на клавиатуре
def callback_worker(call):

    # парсинг новостей с главной страницы
    if call.text == "Главные новости (новость + ссылка)":
        msg = bot.send_message(call.chat.id, 'Сейчас пришлю список главных новостей в чат...')
        try:
            msg2 = bot.send_message(call.chat.id, parcing_main())
            send_keyboard(call, 'Прислал Вам новости с главной страницы! Что нибудь еще?')
        except:
            send_keyboard(call, "Возникла ошибка при парсинге данных. Что нибудь ещё?")

    #парсинг новостей по запросу (за прошедший год)
    elif call.text == "Поиск новостей по запросу (за текущий год)":
        try:
            msg = bot.send_message(call.chat.id, 'Напишите запрос для поиска в чат. Выполню его менее чем за минуту...')
            bot.register_next_step_handler(msg, parcing_search)
        except:
            bot.send_message(call.chat.id, 'С Вашим запросом произошла ошибка. Попробуйте позже.')
            send_keyboard(call, "Чем еще могу помочь?")

    #курс доллара
    elif call.text == "Курс доллара за год":
        bot.send_message(call.chat.id, 'USD/RUB:')
        bot.send_photo(call.chat.id, 'https://gr04.finmarket.ru/Charts/CurrencyDynamic.aspx?src=10148&ft=52148&per=2')
        send_keyboard(call, "Курс выведен успешно. Что нибудь еще?")

    #курс евро
    elif call.text == "Курс евро за год":
        bot.send_message(call.chat.id, 'EUR/RUB:')
        bot.send_photo(call.chat.id, 'https://gr04.finmarket.ru/Charts/CurrencyDynamic.aspx?src=10148&ft=52170&per=2')
        send_keyboard(call, "Курс выведен успешно. Что нибудь еще?")

    #Российские фондовые индексы RTS/MOEX
    elif call.text == "Российские фондовые индексы RTS/MOEX":
        bot.send_message(call.chat.id, 'Динамика индекса RTS (по натуральному логарифму):')
        bot.send_photo(call.chat.id, 'https://gr04.finmarket.ru/charts/IndicatorIndexes.aspx?sec=66&ft=3099')
        bot.send_message(call.chat.id, 'Динамика индекса ММВБ (по натуральному логарифму):')
        bot.send_photo(call.chat.id, 'https://gr04.finmarket.ru/charts/IndicatorIndexes.aspx?sec=66&ft=6039')
        send_keyboard(call, "Динамика индексов выведена. Что нибудь еще?")

    #прощание
    elif call.text == "На сегодня пока всё.":
        bot.send_message(call.chat.id, 'До новых встреч! Если понадоблюсь - введите /start')

@bot.message_handler(content_types=['text'])
def handle_docs_audio(message):
    send_keyboard(message, text="Пожалуйста, выберите один из пунктов меню:")

#непрерывная работа
bot.polling(none_stop=True)

