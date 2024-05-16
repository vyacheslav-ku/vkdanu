from aiogram.types import InputFile, URLInputFile

from database import pool, execute_update_query, execute_select_query
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import types
from database import quiz_data
import os


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
    current_question_index, score = await get_quiz_index(user_id)
    print(current_question_index)
    question = await get_question1(current_question_index)
    if not question:
        return False
    correct_index = question['correct_option']
    opts = question['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{question['question']}", reply_markup=kb)
    return True

# async def get_question(message, user_id):
#     # Получение текущего вопроса из словаря состояний пользователя
#     current_question_index, score = await get_quiz_index(user_id)
#     print(current_question_index)
#     question = get_question1(current_question_index)
#     correct_index = quiz_data[current_question_index]['correct_option']
#     opts = quiz_data[current_question_index]['options']
#     kb = generate_options_keyboard(opts, opts[correct_index])
#     await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)



async def send_image1(message: types.Message):
    try:
        IMAGE_FILENAME = os.getenv("IMAGE_FILENAME", "")
        photo = URLInputFile(
            IMAGE_FILENAME,
            filename="python-quiez.png"
        )
        await message.answer_photo(photo=photo)
    except Exception as e:
        print(str(e))


async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    await update_quiz_index(user_id, current_question_index, 0)
    await get_question(message, user_id)


async def get_quiz_index(user_id):
    get_user_index = f"""
        DECLARE $user_id AS Uint64;

        SELECT question_index, score
        FROM `quiz_state`
        WHERE user_id == $user_id;
    """
    results = execute_select_query(pool, get_user_index, user_id=user_id)

    if len(results) == 0:
        return 0, 0
    question_index = 0
    score = 0
    if results[0]["question_index"] is not None:
        question_index = results[0]["question_index"]
    if results[0]["score"] is not None:
        score = results[0]["score"]
    return question_index, score


async def update_quiz_index(user_id, question_index, score):
    set_quiz_state = f"""
        DECLARE $user_id AS Uint64;
        DECLARE $question_index AS Uint64;
        DECLARE $score AS Uint64;

        UPSERT INTO `quiz_state` (`user_id`, `question_index`, `score`)
        VALUES ($user_id, $question_index, $score);
    """

    execute_update_query(
        pool,
        set_quiz_state,
        user_id=user_id,
        question_index=question_index,
        score=score
    )


async def get_question1(question_index: int = 0):
    get_user_index = f"""
            DECLARE $question_index AS Uint64;

            SELECT question, options ,correct_option
            FROM `quiz_data`
            WHERE question_index == $question_index;
        """
    results = execute_select_query(pool,
                                   get_user_index,
                                   question_index=question_index,
                                   )

    if len(results) == 0:
        return False
    results[0]["options"] = str(results[0]["options"]).split(",")

    return results[0]
