import aiosqlite
from aiogram.utils.keyboard import InlineKeyboardBuilder

from constants import DB_NAME
from quiz_data_file import quiz_data
from aiogram import types


def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()

    for option in answer_options:
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data="right_answer" if option == right_answer else "wrong_answer")
        )

    builder.adjust(1)
    return builder.as_markup()


async def get_question(message, user_id):
    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(user_id)
    correct_index = quiz_data[current_question_index]['correct_option']
    opts = quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)


async def clean_answers(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('DELETE FROM quiz_answers WHERE user_id = (?)', (user_id,))
        # Сохраняем изменения
        await db.commit()


async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    await update_quiz_index(user_id, current_question_index)
    await clean_answers(user_id)
    await get_question(message, user_id)


async def end_quiz(callback: types.CallbackQuery):
    await callback.message.answer("Это был последний вопрос. Квиз завершен!")
    result = await get_statistics(callback.from_user.id)
    await callback.message.answer(
        f"Ваш результат: {result[0]} из {result[1]} ({round(result[0] / result[1] if result[1] > 0 else 1, 1) * 100}%)")


async def get_statistics(user_id):
    # Подключаемся к базе данных
    async with aiosqlite.connect(DB_NAME) as db:
        # Получаем запись для заданного пользователя
        async with db.execute('SELECT sum(answered) AS answered, '
                              'count(answered) AS count_of_questions '
                              'FROM quiz_answers '
                              'WHERE user_id = (?)', (user_id,)) as cursor:
            # Возвращаем результат
            results = await cursor.fetchone()
            if results is not None:
                return results
            return 0, 0


async def get_quiz_index(user_id):
    # Подключаемся к базе данных
    async with aiosqlite.connect(DB_NAME) as db:
        # Получаем запись для заданного пользователя
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id,)) as cursor:
            # Возвращаем результат
            results = await cursor.fetchone()

            if results is not None:
                return results[0]
            return 0


async def update_quiz_index(user_id, index):
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index) VALUES (?, ?)', (user_id, index))
        # Сохраняем изменения
        await db.commit()


async def add_quiz_answer(user_id, index, answered: bool = False):
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    answered_int = 1 if answered else 0

    async with aiosqlite.connect(DB_NAME) as db:
        # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
        await db.execute(
            'INSERT OR REPLACE INTO quiz_answers (id ,user_id, question_index, answered) VALUES (?, ?, ?, ?)',
            (str(user_id) + "_" + str(index), user_id, index, answered_int))
        # Сохраняем изменения
        await db.commit()
