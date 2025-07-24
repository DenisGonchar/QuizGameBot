import aiosqlite
import asyncio

async def create_table():
    # Создаем соединение с базой данных (если она не существует, то она будет создана)
    async with aiosqlite.connect('quiz_bot.db') as db:
        # Выполняем SQL-запрос к базе данных
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (
            user_id INTEGER PRIMARY KEY,
            question_index TEXT,
            options TEXT,
            correct_option INTEGER
            )''')

        # Сохраняем изменения
        await db.commit()

async def update_quiz_index(user_id, index, options, correct_option):
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect('quiz_bot.db') as db:
        # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index, options, Correct_option) VALUES (?, ?, ?, ?)', (user_id, index, options, correct_option))
        # Сохраняем изменения
        await db.commit()
        
async def get_quiz_index(user_id):
     # Подключаемся к базе данных
     async with aiosqlite.connect('quiz_bot.db') as db:
        # Получаем запись для заданного пользователя
        async with db.execute('SELECT question_index, options, correct_option FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
            results = await cursor.fetchone()
            if results is not None:
                return results
            else:
                return 0

async def main():
    #await create_table()
    #await update_quiz_index(12345, 'Python?','dddd', 0)
    result = await get_quiz_index(12345)
    
    print(result)
    
    
if __name__ == "__main__":
    asyncio.run(main())
