import aiohttp
from aiogram import types
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from deep_translator import GoogleTranslator
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import API_WEATHER_TOKEN, API_TOKEN_FOOD, API_key_workout

# Функция для отправки API по погоде
async def get_coordinates(city_name, token=API_WEATHER_TOKEN):
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit={1}&appid={token}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response_data = await response.json()
    except Exception:
        return None
    else:
        return response_data

async def get_current_weather(lat, lon, token=API_WEATHER_TOKEN, units='metric'):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={token}&units={units}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response_data = await response.json()
    except Exception:
        return None
    else:
        return response_data

# Функция для отправки асинхронных API-запросов
async def API_request_weather(API_key, city_name):
  # Получаем информацию о координатах
  response = await get_coordinates(city_name, token=API_key)

  if response is None:
      return False

  try:
    name, lat, lon = response[0]['name'], response[0]['lat'], response[0]['lon']
  except:
      return False

  # Получаем информацию о погоде
  response = await get_current_weather(lat, lon, API_key)

  if response is None:
      return False

  temperature = response['main']['temp']

  return temperature

# Функция для отправки API по калории
async def get_calories(query, API_key=API_TOKEN_FOOD):
    api_url = 'https://api.calorieninjas.com/v1/nutrition?query='

    async with aiohttp.ClientSession() as session:  # Создаем асинхронную сессию
        async with session.get(api_url + query, headers={'X-Api-Key': API_key}) as response:
            if response.status == 200:
                response_json = await response.json()
            else:
                return None
    try:
        return response_json['items'][0]['calories']
    except:
        return None


async def get_calories_workout(activity, API_token=API_key_workout):
    api_url = 'https://api.api-ninjas.com/v1/caloriesburned?activity={}'.format(activity)

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url, headers={'X-Api-Key': API_token}) as response:
            if response.status == 200:
                response = await response.json()
                try:
                    return response[0]['calories_per_hour']
                except:
                    return None
            else:
                print("Error:", response.status, await response.text())
                return None

async def get_workout_recommendation(query, API_token=API_key_workout):
    api_url = 'https://api.api-ninjas.com/v1/exercises?muscle={}'.format(query)

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url, headers={'X-Api-Key': API_token}) as response:
            if response.status == 200:
                response = await response.json()
                try:
                    name, equipment, instructions = response[0]['name'], response[0]['equipment'], response[0]['instructions']
                    return name, equipment, instructions
                except:
                    return None
            else:
                print("Error:", response.status, await response.text())
                return None


def calculate_activity_coef(activity):
    """
    Функция, которая расчитывает коэффициент нагрузки
    1,2 – минимальный (сидячая работа, отсутствие физических нагрузок);
    1,375 – низкий (тренировки не менее 20 мин 1-3 раза в неделю);
    1,55 – умеренный (тренировки 30-60 мин 3-4 раза в неделю);
    1,7 – высокий (тренировки 30-60 мин 5-7 раза в неделю; тяжелая физическая работа);
    1,9 – экстремальный (несколько интенсивных тренировок в день 6-7 раз в неделю; очень трудоемкая работа).
    """
    if activity <= 10:
        return 1
    elif activity <= 30:
        return 1.2
    elif activity <= 60:
        return 1.375
    elif activity <= 120:
        return 1.55
    elif activity <= 180:
        return 1.7
    else:
        return 1.9

# Функция, которая расчитывает калорийность по формуле Харрисона-Бенедикта
def calculcate_calories_threshhold(age, sex, weight, height, activity_level):
    if sex.lower()[0] == 'м':
        normal_calories = 66.5 + (13.75 * weight) + (5.003 * height) - (6.775 * age)
    else:
        normal_calories = 655.1 + (9.563 * weight) + (1.85 * height) - (4.676 * age)

    normal_calories *= calculate_activity_coef(activity_level)

    return  normal_calories

async def calculcate_water_norm(weight, activity_level, city):
    # Расчитываем норму воды без учета погоды
    activity_level_coef = activity_level / 30
    water_norm = weight*30 + activity_level_coef*500
    # Пытаемся получить температуру и понять и учесть её
    temperature = await API_request_weather(API_WEATHER_TOKEN, city)

    if not temperature:
        return water_norm
    if (25 <= temperature <= 30):
        water_norm += 500
    elif (temperature > 30):
        water_norm += 1000

    return  water_norm

async def calculcate_calories(query):
    calories = await get_calories(query, API_key=API_TOKEN_FOOD)
    return  calories

def create_keyboard(commands: list):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*commands)
    return keyboard

def make_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)

def format_table(columns, data):
    # Проверяем, есть ли данные
    if not data:
        return None

    # Определяем ширину столбцов
    column_widths = [max(len(str(item)) for item in [col] + [row[i] for row in data]) for i, col in enumerate(columns)]

    # Формируем строку с заголовками
    header = " | ".join(f"{columns[i]:<{column_widths[i]}}" for i in range(len(columns)))
    separator = "-+-".join('-' * width for width in column_widths)

    # Формируем строки с данными
    rows = "\n".join(" | ".join(f"{str(row[i]):<{column_widths[i]}}" for i in range(len(columns))) for row in data)

    # Собираем итоговый вывод
    table = '<pre>\n' + f"{header}\n{separator}\n{rows}" + '\n</pre>'
    return table

# Функция для валидации строковых типов
def check_str(string_element):
    return (string_element.text.isalpha())

# Функция для валидация возраста
def check_age(age):
    return (age.text.isdigit() and (0 < int(age.text) <= 120))

# Функция для валидации веса
def check_weight(weight):
    return (weight.text.isdigit() and (0 < float(weight.text) <= 645))

# Функция для валидации роста см
def check_height(height):
    return (height.text.isdigit() and (100 <= float(height.text) <= 350))

# Функция для валидации активности
def check_activity(activity):
    return (activity.text.isdigit() and (0 <= float(activity.text) <= 1440))

# Функция для валидации калорий
def check_calories(calories):
    return (calories.text.isdigit() and (500 < float(calories.text) <= 15000))

def check_water(water):
    return (water.text.isdigit()) and (0 < float(water.text) < 10000)

def check_food_weight(weight):
    weight = weight.replace(',', '.')
    return weight.isdigit()

def check_workout_time(time):
    time = time.replace(',', '.')
    return time.isdigit() and (float(time))

def plot_cumulative_progress(calories, water, calorie_limit, calorie_goal, water_limit):
    # Находим максимальную длину среди входных списков
    max_length = max(len(calories), len(water))

    # Дополняем списки до одинаковой длины (в данном случае - до max_length)
    calories = np.pad(calories, (0, max_length - len(calories)), constant_values=0)
    water = np.pad(water, (0, max_length - len(water)), constant_values=0)

    # Кумулятивная сумма
    cumulative_calories = np.cumsum(calories)
    cumulative_water = np.cumsum(water)

    # Создание DataFrame для удобства работы с Seaborn
    df = pd.DataFrame({
        'День': list(range(max_length)),
        'Калории': cumulative_calories,
        'Вода': cumulative_water
    })

    # Создание графиков
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))

    # Добавление графика для калорий
    sns.lineplot(data=df, x='День', y='Калории', marker='o', color='blue', label='Калории', ax=ax1)
    ax1.axhline(y=calorie_limit, color='red', linestyle='--', label='Граница калорий')
    ax1.axhline(y=calorie_goal, color='pink', linestyle='--', label='Goal калорий')
    ax1.set_title('Кумулятивный прогресс по калориям')
    ax1.set_xlabel('День')
    ax1.set_ylabel('Калории')
    ax1.legend(title='Легенда')
    ax1.grid(alpha=0.4)

    # Добавление графика для воды
    sns.lineplot(data=df, x='День', y='Вода', marker='o', color='green', label='Вода', ax=ax2)
    ax2.axhline(y=water_limit, color='red', linestyle='--', label='Goal по воде')
    ax2.set_title('Кумулятивный прогресс по воде')
    ax2.set_xlabel('День')
    ax2.set_ylabel('Вода (мл)')
    ax2.legend(title='Легенда')
    ax2.grid(alpha=0.4)

    # Возвращение объекта фигуры
    fig.tight_layout()  # Автоматическая настройка отступов
    plt.close(fig)  # Закрываем текущее окно, чтобы не отображать его сразу
    return fig


# Функция, которая переводит текст
def translate_text(text, language='en'):
    # Переводим текст на английский
    translated = GoogleTranslator(source='auto', target=language).translate(text)
    return translated