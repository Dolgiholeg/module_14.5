from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

from crud_functions import *


api = ""
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()
    balance = 1000

kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
button = KeyboardButton(text='Рассчитать')
button1 = KeyboardButton(text='Информация')
button2 = KeyboardButton(text='Купить')
button3 = InlineKeyboardButton(text='Регистрация')
kb.add(button, button1, button2, button3)

@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.', reply_markup=kb)


start_menu1 = InlineKeyboardMarkup(resize_keyboard=True, row_width=4)
button1 = InlineKeyboardButton(text='Product1', callback_data='product_buying')
button2 = InlineKeyboardButton(text='Product2', callback_data='product_buying')
button3 = InlineKeyboardButton(text='Product3', callback_data='product_buying')
button4 = InlineKeyboardButton(text='Product4', callback_data='product_buying')
start_menu1.add(button1, button2, button3, button4)

start_menu = InlineKeyboardMarkup(resize_keyboard=True, row_width=3)
button = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button2 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')

start_menu.add(button, button2)

@dp.message_handler(text='Купить')
async def get_buying_list(message):
    items = get_all_products()
    number = 1
    for i in range(4):
        await message.answer(f"Название: {items[i][1]} | Описание: {items[i][2]} | Цена: {items[i][3]}")
        with open(f'foto/{number}.png', 'rb')as img:
            await message.answer_photo(img)
        number += 1
    await message.answer('Выберите продукт для покупки:', reply_markup=start_menu1)

@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию:!', reply_markup=start_menu)

@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('расчета килокалорий для оптимального похудения или сохранения нормального веса = '
                              '(10 x вес (кг) + 6.25 x рост (см) – 5 x возраст (г) + 5) x A')
    await call.answer()

@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer("Введите свой возраст:")
    await UserState.age.set()

@dp.message_handler(state = UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer("Введите свой рост:")
    await UserState.growth.set()

@dp.message_handler(state = UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer("Введите свой вес:")
    await UserState.weight.set()

@dp.message_handler(state = UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    Result = 10 * int(data.get('weight')) + 6.25 * int(data.get('growth')) - 5 * int(data.get('age')) + 5
    await message.answer(f"Ваша норма калорий: {Result}")
    await state.finish()

@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer("Вы успешно приобрели продукт!")
    await UserState.age.set()

@dp.message_handler(text='Регистрация')
async def sing_up(message):
    await message.answer("Введите имя пользователя (только латинский алфавит):")
    await RegistrationState.username.set()

@dp.message_handler(state = RegistrationState.username)
async def set_username(message, state):
    check_username = is_included(message.text)
    if check_username is True:
        await message.answer("Пользователь существует, введите другое имя")
        await RegistrationState.username.set()
    else:
        await state.update_data(username=message.text)
        data = await state.get_data()
        await message.answer("Введите свой email:")
        await RegistrationState.email.set()

@dp.message_handler(state = RegistrationState.email)
async def set_email(message, state):
    await state.update_data(email=message.text)
    data = await state.get_data()
    await message.answer("Введите свой возраст:")
    await RegistrationState.age.set()

@dp.message_handler(state = RegistrationState.age)
async def set_email(message, state):
    await state.update_data(age=message.text)
    data = await state.get_data()
    add_user(data['username'], data['email'], data['age'])
    await state.finish()
    await message.answer('Регистрация прошла успешно', reply_markup=kb)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)