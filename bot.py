import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command

logging.basicConfig(level=logging.INFO)

API_TOKEN = '7992897063:AAFhpgQyVNCD58uOKwEVGswf1P-22yvjST0'
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Логика обработки команды /start
    await message.answer("Привет! Я бот для проведения квиза. Введите /quiz, чтобы начать.")

# Хэндлер на команду /quiz
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    # Логика начала квиза
    await message.answer("Давайте начнем квиз! Первый вопрос: ...")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())