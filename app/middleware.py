from aiogram import BaseMiddleware
from aiogram.types import Message
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)

class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict):
        logging.info(f"Получено сообщение: {event.text}")
        return await handler(event, data)
