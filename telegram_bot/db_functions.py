import aiosqlite

from constants import DB_NAME


async def create_table():
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Создаем таблицу
        await db.execute(
            '''CREATE TABLE IF NOT EXISTS quiz_state (user_id INTEGER PRIMARY KEY, question_index INTEGER)''')
        # await db.execute(
        #     '''CREATE TABLE IF NOT EXISTS quiz_answers (user_id INTEGER PRIMARY KEY, question_index INTEGER PRIMARY KEY, answered INTEGER)''')
        await db.execute(
            '''CREATE TABLE IF NOT EXISTS quiz_answers (id VARCHAR PRIMARY KEY , user_id INTEGER , question_index INTEGER, answered INTEGER)''')
        # Сохраняем изменения
        await db.commit()
