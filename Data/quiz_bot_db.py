import aiosqlite

DB_NAME = 'quiz_bot.db'

async def create_table():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (user_id INTEGER PRIMARY KEY, question_index INTEGER)''')
        await db.execute('''CREATE TABLE IF NOT EXISTS results (user_id INTEGER PRIMARY KEY, correct INTEGER, total INTEGER)''')
        await db.commit()

async def get_quiz_data(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0

async def update_quiz_index(user_id, index):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index) VALUES (?, ?)', (user_id, index))
        await db.commit()

async def save_result(user_id, correct, total):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR REPLACE INTO results (user_id, correct, total) VALUES (?, ?, ?)', (user_id, correct, total))
        await db.commit()
        
async def get_result(user_id: int):
    async with aiosqlite.connect('quiz_bot.db') as db:
        async with db.execute("SELECT correct, total FROM results WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row is not None:
                return row
            else:
                return (0, 0)