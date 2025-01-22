from dotenv import load_dotenv
import os

# Загрузка переменных окружения из .env файла
load_dotenv()

# Конфигурация бота
BOT_TOKEN = os.getenv('BOT_TOKEN')
API_WEATHER_TOKEN = os.getenv('API_WEATHER_TOKEN')
API_TOKEN_FOOD = os.getenv("API_TOKEN_FOOD")
API_key_workout = os.getenv("API_key_workout")