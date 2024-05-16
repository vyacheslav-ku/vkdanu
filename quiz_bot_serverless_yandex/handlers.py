from aiogram import types, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart, StateFilter, CommandObject, CREATOR
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from database import quiz_data
from service import generate_options_keyboard, get_question, new_quiz, get_quiz_index, update_quiz_index, \
    send_image1

router = Router()


@router.callback_query(F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    await callback.message.answer("Верно!")
    current_question_index, score = await get_quiz_index(callback.from_user.id)
    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    score += 1
    await update_quiz_index(callback.from_user.id, current_question_index, score)
    result = await get_question(callback.message, callback.from_user.id)
    if not result:
        await callback.message.answer(f"Это был последний вопрос. Квиз завершен! Оценка {score}")


@router.callback_query(F.data == "wrong_answer")
async def wrong_answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index, score = await get_quiz_index(callback.from_user.id)
    correct_option = quiz_data[current_question_index]['correct_option']

    await callback.message.answer(
        f"Неправильно. Правильный ответ: {quiz_data[current_question_index]['options'][correct_option]}")

    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index, score)

    result = await get_question(callback.message, callback.from_user.id)
    if not result:
        await callback.message.answer(f"Это был последний вопрос. Квиз завершен! Оценка {score}")


# Хэндлер на команду /start
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await send_image1(message)
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))


# Хэндлер на команду /quiz
@router.message(F.text == "Начать игру")
@router.message(Command("quiz"))
async def cmd_quiz(message: types.Message):

    await message.answer(f"Давайте начнем квиз!")
    await new_quiz(message)
