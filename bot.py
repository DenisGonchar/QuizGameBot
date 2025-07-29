import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import F
from dotenv import load_dotenv
import os

import Data.quiz_bot_db as quiz_bot_db
import Data.quiz_data as quiz_data

logging.basicConfig(level=logging.INFO)

load_dotenv()

API_TOKEN = os.getenv('API_KEY') 
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

full_quiz = quiz_data.quiz_data

user_correct = {}

# Хэндлер команд
@dp.message(Command('start'))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text='Начать игру!'))
    builder.add(types.KeyboardButton(text='Последний результат'))
    builder.add(types.KeyboardButton(text='Помощь'))
    builder.adjust(1)

    await message.answer("Добро пожаловать в квиз!",
        reply_markup=builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
    )
    
@dp.message(F.text == 'Начать игру!')
@dp.message(Command('quiz'))
async def cmd_quiz(message: types.Message):
    await message.answer("Начинаем квиз!")
    await new_quiz(message)

@dp.message(F.text == 'Последний результат')
@dp.message(Command('stats'))
async def cmd_stats(message: types.Message):
    correct, total = await quiz_bot_db.get_result(message.from_user.id)
    await message.answer(f'Ваши результаты:\nПравильных ответов: {correct}\nВсего вопросов: {total}')
    
@dp.message(F.text == 'Помощь')
@dp.message(Command('help'))
async def cmd_help(message: types.Message):
    help_text = (
        "Добро пожаловать в квиз!\n"
        "Чтобы начать игру, нажмите 'Начать игру! или /quiz'\n"
        "Вы можете проверить свои результаты, нажав 'Последний результат или /stats'.\n"
        "Если вам нужна помощь, нажмите 'Помощь' или /help.\n"
        "Удачи!"
    )
    await message.answer(help_text)

# Функционал кнопок
# - Колбек кнопок
@dp.callback_query(F.data.split('|', 1)[0] == "right_answer")
async def right_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id = callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    option_text = callback.data.split('|', 1)[1]
    await callback.message.answer(f'Вы выбрали: {option_text}')
    await callback.message.answer('Вывод: Верно!')
    
    user_id = callback.from_user.id
    user_correct[user_id] = user_correct.get(user_id, 0) + 1
    
    current_question_index = await quiz_bot_db.get_quiz_data(user_id)
    current_question_index += 1
    
    await quiz_bot_db.update_quiz_index(user_id, current_question_index)
    
    if current_question_index < len(full_quiz):
        await get_question(callback.message, user_id)
    else:
        await quiz_bot_db.save_result(user_id, user_correct.get(user_id, 0), len(full_quiz))
        await callback.message.answer('Это последний вопрос! Спасибо за участие в квизе! \n'
                                      f'Ваш результат: {user_correct.get(user_id, 0)} из {len(full_quiz)}')
        
# - Колбек кнопок
@dp.callback_query(F.data.split('|', 1)[0] == 'wrong_answer')
async def wrong_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    user_id = callback.from_user.id
    
    option_text = callback.data.split('|', 1)[1]
    await callback.message.answer(f'Вы выбрали: {option_text}')
    
    current_question_index = await quiz_bot_db.get_quiz_data(user_id)
    corrent_option = full_quiz[current_question_index]['correct_option']
    
    await callback.message.answer(f'Вывод: Неправильно. \nПравильный ответ: {full_quiz[current_question_index]["options"][corrent_option]}')
    
    current_question_index += 1
    await quiz_bot_db.update_quiz_index(user_id, current_question_index)
    
    if current_question_index < len(full_quiz):
        await get_question(callback.message, user_id)
    else:
        await quiz_bot_db.save_result(user_id, user_correct.get(user_id, 0), len(full_quiz))
        await callback.message.answer('Это последний вопрос! Спасибо за участие в квизе!\n'
                                      f'Ваш результат: {user_correct.get(user_id, 0)} из {len(full_quiz)}')

    
#Функции
async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    user_correct[user_id] = 0
    
    await quiz_bot_db.update_quiz_index(user_id, current_question_index)
    await get_question(message, user_id)


async def get_question(message, user_id):
    current_question_index = await quiz_bot_db.get_quiz_data(user_id)
    
    current_index = full_quiz[current_question_index]['correct_option']
    options = full_quiz[current_question_index]['options']
    
    kb = generate_options_keyboard(options, options[current_index])
    await message.answer(f'------------------------------')
    await message.answer(f'Вопрос: {full_quiz[current_question_index]["question"]}', reply_markup=kb)


def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()
    
    for option in answer_options:
        answer_type = 'right_answer' if option == right_answer else 'wrong_answer'
        data = f'{answer_type}|{option}'
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data=data
            ))
    
    builder.adjust(1)
    return builder.as_markup()


async def main():
    await quiz_bot_db.create_table()
    await dp.start_polling(bot)
    
if __name__ == "__main__":
    asyncio.run(main())