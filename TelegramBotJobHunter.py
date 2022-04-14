import telebot
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from time import sleep


# УСТАНОВИТЕ GECKODRIVER С ОФИЦИАЛЬНОГО РЕПОЗИТОРИЯ GITHUB
# ДЛЯ РАБОТЫ НЕОБХОДИМ УСТАНОВЛЕННЫЙ FIREFOX BROWSER


def get_vacancy(request, special, message):
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    driver.get('https://hh.ru/search/vacancy/advanced')
    driver.find_element(By.XPATH, '''//*[@id="HH-React-Root"]/div/div/div/div[2]/div/div/button''').click()
    elements = driver.find_elements(By.CLASS_NAME, '''bloko-checkbox''')
    for element in elements:
        if element.text == special[0]:
            element.click()

    for i in range(4):
        try:
            driver.find_element(By.XPATH, '''/html/body/div[13]/div/div[1]/div[4]/div/span[2]/button''').click()
        except Exception as error:
            print('Произошла непредвиденная ошибка. Повторная попытка...', error, sep='\n')
        sleep(2)

    vacancies, links = [], []
    for i in range(3):
        try:
            driver.find_element(By.XPATH, '''//*[@id="advancedsearchmainfield"]''').send_keys(request)
            driver.find_element(By.XPATH, '''//*[@id="submit-bottom"]''').click()
            vacancies = driver.find_elements(By.CLASS_NAME, '''vacancy-serp-item''')
            vacancies = list(
                filter(lambda x: not x.text.startswith('Попробуйте другие варианты поискового запроса'), vacancies))
            links = driver.find_elements(By.CLASS_NAME, '''bloko-link''')
            links = list(filter(
                lambda x: x.get_attribute('href') and x.get_attribute('href').startswith('https://hh.ru/vacancy/'),
                links))
        except Exception as error:
            print('Произошла непредвиденная ошибка...', error)
        sleep(1)


    if len(vacancies) > 10 and len(links) > 10:
        for i in range(min(5, len(vacancies), len(links))):
            bot.send_message(message.chat.id, vacancies[i].text[:-30:] + '\n' + links[i].get_attribute('href'))
    else:
        bot.send_message(message.chat.id, 'Ваш запрос не дал результатов, пожалуйста, повторите ещё раз')
        driver.quit()


bot = telebot.TeleBot('5349273980:AAGmLHWGVKL0mm1tKiF9MZlsLYEFcccrcCY')
spec = ['']


@bot.message_handler(commands=['start'])
def start(message):
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(telebot.types.KeyboardButton('Найти специализацию!'))
    bot.send_message(message.chat.id, 'Привет, ищешь работу <3\nНажмите на кнопку', reply_markup=kb)


def specialization(message):
    global spec
    spec[0] = message.text.capitalize()
    bot.send_message(message.chat.id, 'Введите ваш запрос')
    bot.register_next_step_handler(message, finder)


def finder(message):
    bot.delete_message(message.chat.id, message.message_id - 1)
    bot.send_message(message.chat.id, '❤️ Подождите, ваш запрос обрабатывается...')
    get_vacancy(message.text, spec, message)


@bot.message_handler(content_types=['text'])
def text(message):
    if message.text == 'Найти специализацию!':
        bot.send_message(message.chat.id, 'Введите желаемую специализацию:',
                         reply_markup=telebot.types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, specialization)
    else:
        bot.send_message(message.chat.id, 'Вы написали: ' + message.text)


bot.polling(none_stop=True, interval=0)
