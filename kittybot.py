import logging
import os
import requests

from dotenv import load_dotenv
from telebot import TeleBot, types

# Парсим файл .env
load_dotenv()

# Переменные окружения
BOT_TOKEN = os.getenv('TOKEN')
TELEGRAM_ID = os.getenv('CHAT_ID')
PRACTICUM_TOKEN = os.getenv('YANDEX_TOKEN')

# URLs-эндпоинты
CAT_API_URL = 'https://api.thecatapi.com/v1/images/search'
YANDEX_API_URL = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'

# Для работы с API Практикума
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
PAYLOAD = {'from_date': 0}

# Инициализация бота
bot = TeleBot(token=BOT_TOKEN)

# Настройки логгирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)


def get_new_img():
    """Получение рандомного изображения кота или собаки."""
    try:
        response = requests.get(CAT_API_URL)
        msg = bot.send_message(TELEGRAM_ID, 'Запрос фото с котиком...')
        logging.info(f'Статус запроса к API: {response.status_code}')
        bot.send_chat_action(TELEGRAM_ID, 'typing')
        bot.delete_message(TELEGRAM_ID, message_id=msg.message_id)
    except Exception as error:
        logging.error(f'Ошибка при запросе к API c котиками: {error}')
        bot.send_message(
            f'Ошибка при запросе к API c котиками: {error}'
        )
        msg = bot.send_message('Запрос фото с собачкой...')
        bot.send_chat_action(TELEGRAM_ID, 'typing')
        bot.delete_message(TELEGRAM_ID, message_id=msg.message_id)
        logging.info('Бот отправляет запрос на API с фото собак.')
        new_url = 'https://api.thedogapi.com/v1/images/search'
        response = requests.get(new_url)

    response = response.json()
    random_cat = response[0].get('url')
    return random_cat


def get_homework_status():
    """Получение статуса крайней домашней работы."""
    try:
        response = requests.get(
            YANDEX_API_URL, headers=HEADERS, params=PAYLOAD
        )
        logging.info(f'Статус запроса к API: {response.status_code}')
        msg = bot.send_message(
            TELEGRAM_ID, 'Запрос к API Практикума...'
        )
        bot.send_chat_action(TELEGRAM_ID, 'typing')
        bot.delete_message(
            TELEGRAM_ID, message_id=msg.message_id
        )
    except Exception as error:
        logging.error(
            f'Ошибка при запросе к API Практикума: {error}'
            )
        bot.send_message(
            f'Ошибка при запросе к API Практикума: {error}'
        )
        return

    result_flag = None
    response: dict = response.json()
    get_homeworks = response.get('homeworks')
    if not get_homeworks:
        return 'Нет информации о домашних работах.'
    result = get_homeworks[0].get('status')

    if result == 'approved':
        result_flag = 'Работа проверена: ревьюеру всё понравилось. Ура!'
    elif result == 'reviewing':
        result_flag = 'Работа взята на проверку ревьюером.'
    else:
        result_flag = 'Работа проверена: у ревьюера есть замечания.'
    return result_flag


@bot.message_handler(commands=['newcat'])
def new_cat(message):
    """Обработчик команды /newcat."""
    bot.send_photo(TELEGRAM_ID, get_new_img())
    logging.info('Вызвана команда /newcat')


@bot.message_handler(commands=['get_homework'])
def homework(message):
    """Обработчик команды /get_homework."""
    bot.send_message(TELEGRAM_ID, get_homework_status())
    logging.info('Вызвана команда /get_homework')


@bot.message_handler(commands=['start'])
def wake_up(message):
    """Обработчик команды /start."""
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )
    keyboard.row(
        types.KeyboardButton('/get_homework'),
        types.KeyboardButton('/newcat'),
    )
    bot.send_message(
        TELEGRAM_ID,
        'Привет!',
        reply_markup=keyboard
        )


@bot.message_handler(content_types=['text'])
def say_hi(message):
    """Обработчик текста."""
    bot.send_message(TELEGRAM_ID, 'Привет, я KittyBot!')
    logging.info('Бот отправил сообщение.')


def main():
    """Основная функция бота."""
    logging.info('Старт бота.')
    bot.polling()


if __name__ == '__main__':
    main()
    logging.info('Бот отключен пользователем.')
