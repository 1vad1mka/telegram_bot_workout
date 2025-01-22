from aiogram import Router, types
from aiogram.types import Message, ChatMemberUpdated
from aiogram.filters import Command
import emoji
from functions_bot import make_row_keyboard

router = Router()

@router.message(Command('start'))
async def start(message: Message):
    response =\
    f'''
    {emoji.emojize(":wave:", language='alias')}
    Добро пожаловать! Я бот, который помогает вести здоровый образ жизни!
    Я помогу вам с:
        {emoji.emojize(":point_right:", language='alias')} подсчетом калорий;
        {emoji.emojize(":point_right:", language='alias')} отслеживанием питьевого режима;
        {emoji.emojize(":point_right:", language='alias')} отслеживанием прогресса по вашим тренировкам и многое другое.         
    
    Вначале обязательно установи профиль!
    Если хочешь узнать список доступных команд, используй /help!
    Будь здоров! {emoji.emojize(":muscle:", language='alias')}
    '''

    await message.answer(
        text=response,
        reply_markup=make_row_keyboard(['/set_profile'])
    )

@router.message(Command('help'))
async def help(message: Message):
    response =\
    f'''
    Доступны следующие команды:
        {emoji.emojize(":point_right:", language='alias')} /start - общая информация
        {emoji.emojize(":point_right:", language='alias')} /help - основные команды
        {emoji.emojize(":point_right:", language='alias')} /set_profile - создание профиля
        {emoji.emojize(":point_right:", language='alias')} /cancel - отмена ввода при создании пользователя
        {emoji.emojize(":point_right:", language='alias')} /profiles_list - просмотр доступных профилей
        {emoji.emojize(":point_right:", language='alias')} /set_active_profile - установка активного профиля
        {emoji.emojize(":point_right:", language='alias')} /log_water - записывает выпитую воду в миллилитрах
        {emoji.emojize(":point_right:", language='alias')} /log_food - записывает калории
        {emoji.emojize(":point_right:", language='alias')} /log_workout - записывает тренировки
        {emoji.emojize(":point_right:", language='alias')} /see_progress - посмотреть свой прогресс
        {emoji.emojize(":point_right:", language='alias')} /reset_progress - обнулить прогресс
        {emoji.emojize(":point_right:", language='alias')} /see_history_food - посмотреть историю записи калорий
        {emoji.emojize(":point_right:", language='alias')} /see_history_water - посмотреть историю записи воды
        {emoji.emojize(":point_right:", language='alias')} /see_history_workout - посмотреть историю записи тренировок
        {emoji.emojize(":point_right:", language='alias')} /progress_graph - посмотреть графики прогресса по калориям и воде
        {emoji.emojize(":point_right:", language='alias')} /get_workout_recommendation - получить рекомендацию по тренировке группы мышц
    '''

    await message.reply(response)




