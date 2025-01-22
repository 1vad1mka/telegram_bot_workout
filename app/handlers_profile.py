import emoji
from aiogram import Router
from aiogram.types import Message, BufferedInputFile, InputFile
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode
from functions_bot import get_calories_workout, calculcate_calories_threshhold,\
    calculcate_water_norm, calculcate_calories, check_calories, check_activity, check_weight,\
    check_height, check_age, check_str, check_water, check_food_weight, check_workout_time,\
    format_table, plot_cumulative_progress, get_workout_recommendation, translate_text
from datetime import datetime
import io

users_data = {}
history_data = {}
active_profile_id = None

router = Router()

class Profile(StatesGroup):
    name = State()
    country = State()
    city = State()
    age = State()
    sex = State()
    weight = State()
    height = State()
    activity_level = State()
    calories_goal = State()

# Функция, которая создает клавиатуру
def make_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)

# Ручка для просмотра профилей
@router.message(Command('profiles_list'))
async def profiles_list(message: Message):
    await message.reply(f"Данные о созданных профилях:\n {users_data}")

# Для установки активного профиля
@router.message(Command('set_active_profile'))
async def set_active_profile(message: Message):
    global active_profile_id
    user_id = message.text
    # Проверяем, существует ли профиль
    if message.text not in users_data.keys():
        await message.reply(f"Профиля с id {user_id} не существует!")

    active_profile_id = user_id
    await message.reply(f"Профиль с id {user_id} был установлен в качестве активного.")

# Отмена ввода данных и сброс состояний
@router.message(Command('cancel'))
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.reply("Ввод данных отменен.")

@router.message(Command('set_profile'))
async def set_profile(message: Message, state: FSMContext):
    await message.reply("Как вас зовут?")
    await state.set_state(Profile.name)

@router.message(Profile.name)
async def process_name(message: Message, state: FSMContext):
    # Проверяем введенные данные
    if not check_str(message):
        await message.reply("Пожалуйста, введите данные корректного формата")
        return

    await state.update_data(name=message.text)
    await message.reply("Пожалуйста, укажите страну проживания.")
    await state.set_state(Profile.country)

@router.message(Profile.country)
async def process_country(message: Message, state: FSMContext):
    # Проверяем введенные данные
    if not check_str(message):
        await message.reply("Пожалуйста, введите данные корректного формата")
        return

    await state.update_data(country=message.text)
    await message.reply("Из какого вы города?")
    await state.set_state(Profile.city)

@router.message(Profile.city)
async def process_city(message: Message, state: FSMContext):
    # Проверяем введенные данные
    if not check_str(message):
        await message.reply("Пожалуйста, введите данные корректного формата")
        return

    await state.update_data(city=message.text)
    await message.reply("Введите, пожалуйста ваш возраст.")
    await state.set_state(Profile.age)

@router.message(Profile.age)
async def process_age(message: Message, state: FSMContext):
    # Обрабатываем возраст
    if not check_age(message):
        await message.reply("Пожалуйста, введите данные корректного формата")
        return

    await state.update_data(age=float(message.text))
    # Переходим к выбору пола
    await message.answer(
        text="Выберите пол:",
        reply_markup=make_row_keyboard(['Мужской', 'Женский'])
    )
    # Статус обработки пола
    await state.set_state(Profile.sex)

@router.message(Profile.sex)
async def process_sex(message: Message, state: FSMContext):
    await state.update_data(sex=message.text)
    await message.reply("Введите, пожалуйста ваш вес в кг.")
    await state.set_state(Profile.weight)

@router.message(Profile.weight)
async def process_weight(message: Message, state: FSMContext):
    # Проверяем вес
    if not check_weight(message):
        await message.reply("Пожалуйста, введите данные корректного формата")
        return

    await state.update_data(weight=float(message.text))
    await message.reply("Введите ваш рост в см")
    await state.set_state(Profile.height)

@router.message(Profile.height)
async def process_height(message: Message, state: FSMContext):
    # Проверяем рост
    if not check_height(message):
        await message.reply("Пожалуйста, введите данные корректного формата")
        return

    await state.update_data(height=float(message.text))
    await message.reply("Введите уровень вашей физической активности (минут в день)")
    await state.set_state(Profile.activity_level)

@router.message(Profile.activity_level)
async def process_activity_level(message: Message, state: FSMContext):
    if not check_activity(message):
        await message.reply("Пожалуйста, введите данные корректного формата")
        return

    await state.update_data(activity_level=float(message.text))
    await message.reply("Введите лимит калорий, которого вы хотите придерживаться.")
    await state.set_state(Profile.calories_goal)

@router.message(Profile.calories_goal)
async def process_calories_goal(message: Message, state: FSMContext):
    if not check_calories(message):
        await message.reply("Пожалуйста, введите данные корректного формата")
        return

    await state.update_data(calories_goal=float(message.text))

    # Сохраняем профиль пользователя в словарь
    user_id = message.from_user.id
    users_data[user_id] = await state.get_data()

    # Рассчитываем для пользователя нормы калорий и норму потребления воды
    city, age, sex, weight, height, activity_level = users_data[user_id]['city'], float(users_data[user_id]['age']), users_data[user_id]['sex'], float(users_data[user_id]['weight']), float(users_data[user_id]['height']), float(users_data[user_id]['activity_level'])
    normal_calories = calculcate_calories_threshhold(age, sex, weight, height, activity_level)
    normal_water = await calculcate_water_norm(weight, activity_level, city)
    # Добавляем рассчитанные значения в профиль пользователя
    users_data[user_id]['normal_calories'], users_data[user_id]['normal_water'] = normal_calories, normal_water
    # Добавляем в профиль пока что пустые словари для сбора логов
    users_data[user_id]['water_history'] = []
    users_data[user_id]['calories_history'] = []
    users_data[user_id]['workout_history'] = []
    # Добавляем историю
    history_data[user_id] = {}
    history_data[user_id]['food_history'] = []
    history_data[user_id]['water_history'] = []
    history_data[user_id]['workout_history'] = []

    await message.reply(f"Профиль успешно создан {emoji.emojize(':heavy_check_mark:', language='alias')}")
    global active_profile_id
    active_profile_id = user_id
    await state.clear()


# Хэндлеры для логирования пока что здесь же
# Возможно, потом их придется скинуть в другой файл
class WaterLogging(StatesGroup):
    water_volume = State()

@router.message(Command('log_water'))
async def log_water(message: Message, state: FSMContext):
    await message.reply(f"Сколько воды вы выпили в мл? {emoji.emojize(':droplet:', language='alias')}")
    await state.set_state(WaterLogging.water_volume)

@router.message(WaterLogging.water_volume)
async def process_water(message: Message, state: FSMContext):
    # Проверяем введенные данные
    if not check_water(message):
        await message.reply("Пожалуйста, введите данные корректного формата")
        return

    # Добавляем выпитую воду в историю
    await state.update_data(water_volume=message.text)
    results = await state.get_data()
    water_volume = float(results['water_volume'])
    # Добавляем текущую дату
    users_data[active_profile_id]['water_history'].append(water_volume)
    # Добавляем воду в историю
    drink_date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    history_data[active_profile_id]['water_history'].append([drink_date, water_volume])
    # Считаем результирующую воду
    all_water = sum(users_data[active_profile_id]['water_history'])
    water_norm = users_data[active_profile_id]['normal_water']
    # Записываем ответ пользователю
    response =\
    f'''
    Прогресс по норме воды: {all_water} / {water_norm}  {emoji.emojize(':droplet:', language='alias')}
    '''
    await message.reply(response)
    await state.clear()

# Хэндлеры для логгирования еды
class FoodLogging(StatesGroup):
    food_name = State()
    food_weight = State()
    food_calories = None

@router.message(Command('log_food'))
async def log_food(message: Message, state: FSMContext):
    await message.reply(f"Что вы съели? {emoji.emojize(':green_apple:', language='alias')}")
    await state.set_state(FoodLogging.food_name)

@router.message(FoodLogging.food_name)
async def process_name(message: Message, state: FSMContext):
    # Переводим на английский и отправляем запрос
    food_name = message.text
    food_name_eng = translate_text(food_name, language='en')
    calories = await calculcate_calories(food_name_eng )
    # Если вернуло None, То нужно
    if not calories:
        await message.reply("Блюдо, которое вы указали не найдено. Попробуйте еще раз.\
                            Возможно, вы ввели название еды не на английском.")
        return

    # Если калории возвращены, то сохраняем
    calories = float(calories)
    await state.update_data(food_name=food_name)
    await state.update_data(food_calories=calories)
    await message.reply("Укажите вес съеденного в граммах")
    await state.set_state(FoodLogging.food_weight)

@router.message(FoodLogging.food_weight)
async def process_food_weight(message: Message, state: FSMContext):
    if not check_food_weight(message.text):
        await message.reply("Пожалйуста, проверьте формат ввода веса.")
        return

    try:
        weight = float(message.text)
    except:
        await message.reply("Пожалйуста, проверьте формат ввода веса.")
        return

    # Добавляем вес продукта
    await state.update_data(food_weight=weight)

    # Рассчитываем итоговые калории согласно весу
    state_data = await state.get_data()
    calories, food_name, food_weight  = state_data['food_calories'], state_data['food_name'], state_data['food_weight']
    weight_coef = weight / 100
    final_calories = calories * weight_coef
    # Записываем калории в профиль
    users_data[active_profile_id]['calories_history'].append(final_calories)
    # Записываем калории в историю
    eat_date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    history_temp = [eat_date, food_name, food_weight, calories]
    history_data[active_profile_id]['food_history'].append(history_temp)
    await message.reply(f'Продукт {food_name} был успешно записан с итоговыми калориями {final_calories}.\nТекущий прогресс: {sum(users_data[active_profile_id]['calories_history'])} / {users_data[active_profile_id]['calories_goal']} {emoji.emojize(':bar_chart:', language='alias')}')
    await state.clear()

# Класс для состояний логгирования тренировок
class WorkoutState(StatesGroup):
    workout_name = State()
    workout_time = State()
    workout_calories = None

# Логируем тренировки
@router.message(Command('log_workout'))
async def log_workout(message: Message, state: FSMContext):
    await message.reply("Каким видом активности вы занимались? ")
    await state.set_state(WorkoutState.workout_name)

@router.message(WorkoutState.workout_name)
async def process_name(message: Message, state: FSMContext):
    activity_name = message.text
    activity_name_eng = translate_text(activity_name)
    workout_calories = await get_calories_workout(activity=activity_name_eng)

    if not workout_calories:
        await message.reply('Данные о калориях не были извлечены. Возможно, вы ввели данные в неправильном формате.')
        return

    await state.update_data(workout_name=activity_name)
    await state.update_data(workout_calories=workout_calories)
    await message.reply('Сколько вы занимались такой активностью? Введите время в минутах.')
    await state.set_state(WorkoutState.workout_time)


@router.message(WorkoutState.workout_time)
async def process_time(message: Message, state: FSMContext):
    activity_time = message.text

    if not check_workout_time(activity_time):
        await message.reply("Введенные данные некорректного формата. Пожалуйста, исправьте запрос.")
        return
    try:
        activity_time = float(activity_time)
    except:
        await message.reply("Введенные данные некорректного формата. Пожалуйста, исправьте запрос.")

    # Зафиксируем получанное время
    await state.update_data(workout_time=activity_time)

    # Высчитываем, сколько калорий сожгла активность
    data_temp = await state.get_data()
    activity_time_coef = activity_time / 60
    workout_name, workout_time, workout_calories = data_temp['workout_name'], float(data_temp['workout_time']), float(data_temp['workout_calories'])
    overall_calories_burnt = workout_calories * activity_time_coef
    # Сохраняем общие калории в лог
    users_data[active_profile_id]['workout_history'].append(overall_calories_burnt)
    # Записываем в общую историю
    workout_date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    history_temp = [workout_date, workout_name, workout_time, overall_calories_burnt]
    history_data[active_profile_id]['workout_history'].append(history_temp)
    # Отправляем ответ пользователю
    await message.reply(f"Ваша активность '{workout_name}' сожгла {overall_calories_burnt} калорий! Результаты записаны! Хорошая работа! {emoji.emojize(':weight_lifter:', language='alias')}")
    await state.clear()

# Хэндлер для просмотра результатов
@router.message(Command('see_progress'))
async def see_progress(message: Message):
    if (not active_profile_id):
        await message.reply("Вначале нужно установить активный профиль!")

    # Записываем ожидаемые значения
    water_norm, calories_norm, calories_goal =\
        users_data[active_profile_id]['normal_water'], users_data[active_profile_id]['normal_calories'],  users_data[active_profile_id]['calories_goal']
    # Записываем фактические значения
    calories_total, water_total, workout_total =\
        sum(users_data[active_profile_id]['calories_history']), sum(users_data[active_profile_id]['water_history']), sum(users_data[active_profile_id]['workout_history'])

    response =\
    f'''
    Текущий прогресс {emoji.emojize(':bar_chart:', language='alias')}:
        {emoji.emojize(':cup_with_straw:', language='alias')} Вода: {water_total} / {round(water_norm)} мил
        {emoji.emojize(':memo:', language='alias')} Калории: {calories_total}/{calories_goal} (норма калорий: {round(calories_norm)}
        {emoji.emojize(':weight_lifter:', language='alias')} Сожженные калории: {round(workout_total)}
        {emoji.emojize(':chart_with_upwards_trend:', language='alias')} Goal по калориям после workout: {round(calories_goal + workout_total)}
    '''

    await message.answer(response)

# Хэндлер для ресета результатов в активном профиле.
@router.message(Command('reset_progress'))
async def reset_progress(message: Message):
    global users_data
    users_data[active_profile_id]['water_history'] = []
    users_data[active_profile_id]['calories_history'] = []
    users_data[active_profile_id]['workout_history'] = []
    await message.reply(f'Прогресс был успешно стерт {emoji.emojize(':scissors:', language='alias')}')

# Хэндлеры для просмотра истории еды
@router.message(Command('see_history_food'))
async def see_history_food(message: Message):
    data = history_data[active_profile_id]['food_history']

    if not data:
        await message.reply(f'История пока что пуста {emoji.emojize(':white_frowning_face:', language='alias')}')

    columns = ['Дата', 'Имя продукта', 'Вес продукта', 'Калории']
    response = format_table(columns, data)
    await message.answer(response, parse_mode=ParseMode.HTML)

# Хэндлеры для просмотра истории воды
@router.message(Command('see_history_water'))
async def see_history_water(message: Message):
    data = history_data[active_profile_id]['water_history']

    if not data:
        await message.reply(f'История пока что пуста {emoji.emojize(':white_frowning_face:', language='alias')}')

    columns = ['Дата', 'Вода, мл']
    response = format_table(columns, data)
    await message.answer(response, parse_mode=ParseMode.HTML)

# Хэндлеры для просмотра истории тренировок
@router.message(Command('see_history_workout'))
async def see_history_workout(message: Message):
    data = history_data[active_profile_id]['workout_history']

    if not data:
        await message.reply(f'История пока что пуста {emoji.emojize(':white_frowning_face:', language='alias')}')

    columns = ['Дата', 'Тренировка', 'Время', 'Калорий сожжено']
    response = format_table(columns, data)
    await message.answer(response, parse_mode=ParseMode.HTML)

# Отправка графиков
@router.message(Command('progress_graph'))
async def progress_graph(message: Message):
    try:
        calories, water = users_data[active_profile_id]['calories_history'], users_data[active_profile_id]['water_history']
        calories_norm, calories_goal, water_norm = users_data[active_profile_id]['normal_calories'], users_data[active_profile_id]['calories_goal'], users_data[active_profile_id]['normal_water']
    except:
        await message.reply("Вначале нужно создать профиль!")
        return

    fig = plot_cumulative_progress(calories, water, calories_norm, calories_goal, water_norm)

    sns_figure = fig.get_figure()
    buf = io.BytesIO()
    sns_figure.savefig(buf, format='png')
    buf.seek(0)

    await message.answer("Начинаю отправку картинки")
    await message.answer_photo(BufferedInputFile(buf.read(), filename="my_image"))


# Рекомендации тренировок по мышцам
class WorkoutRecommendations(StatesGroup):
    muscle = State()


@router.message(Command('get_workout_recommendation'))
async def get_workout_muscle(message: Message, state: FSMContext):
    await message.reply("Какие мышцы вы хотите тренировать?")
    await state.set_state(WorkoutRecommendations.muscle)

@router.message(WorkoutRecommendations.muscle)
async def process_muscle(message: Message, state: FSMContext):
    muscle = message.text
    muscle_eng = translate_text(muscle)

    try:
        name, equipment, instructions = await get_workout_recommendation(muscle_eng)
    except:
        await message.reply("Что-то пошло не так. Попробуйте указать группу мышц по-другому.")
        return

    response =\
    f'''
    Рекомендуемая тренировка по мышцам '{muscle}':
    - {emoji.emojize(":point_right:", language='alias')} Название: {translate_text(name, language='ru')}
    - {emoji.emojize(":point_right:", language='alias')} Необходимое снаряжение: {translate_text(equipment, language='ru')}
    - {emoji.emojize(":point_right:", language='alias')} Инструкции:
      {translate_text(instructions, language='ru')}
    '''

    await message.answer(response)
    await state.clear()



