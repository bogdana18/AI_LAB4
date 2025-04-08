import asyncio
import aiohttp
import logging

from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram import Router
from handlers.media import media

from config import BOT_TOKEN, OPEN_WEATHER_MAP
from db import add_order, get_orders_by_user

# FSM стани
class WeatherState(StatesGroup):
    waiting_for_city = State()

class OrderState(StatesGroup):
    waiting_for_product_name = State()
    waiting_for_quantity = State()

# Логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ініціалізація бота та диспетчера
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()
dp.include_router(router)

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Вітаю! Я бот для замовлення продукції Рошен. Для допомоги введіть /help")

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="/start"), KeyboardButton(text="/info")],
        [KeyboardButton(text="/weather"), KeyboardButton(text="/menu")],
        [KeyboardButton(text="/inline_menu")]
    ])
    await message.answer("Оберіть дію:", reply_markup=keyboard)

@router.message(Command("info"))
async def cmd_info(message: types.Message):
    await message.answer("Цей бот допоможе ознайомитися з продукцією Рошен та зробити замовлення!")

@router.message(Command("inline_menu"))
async def cmd_menu(message: types.Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Каталог", callback_data="catalog")],
        [InlineKeyboardButton(text="Зробити замовлення", callback_data="order")],
        [InlineKeyboardButton(text="Мої замовлення", callback_data="my_orders")]
    ])
    await message.answer("Оберіть дію:", reply_markup=keyboard)

@router.message(Command("menu"))
async def cmd_inline_menu(message: types.Message):
    inline_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Поділитися посиланням", url="https://roshen.com/ua")],
        [InlineKeyboardButton(text="Отримати курс валют", callback_data="get_rate")]
    ])
    await message.answer("Оберіть опцію:", reply_markup=inline_kb)

@router.callback_query(lambda c: c.data == "get_rate")
async def process_callback_get_rate(callback_query: types.CallbackQuery):
    await callback_query.message.answer("USD: 39.5 грн, EUR: 42.0 грн (умовно)")
    await callback_query.answer()

@router.message(Command("weather"))
async def cmd_weather(message: types.Message, state: FSMContext):
    await message.answer("Введіть назву міста, для якого хочете дізнатися погоду:")
    await state.set_state(WeatherState.waiting_for_city)

@router.message(F.content_type.in_({"photo", "document", "audio", "video"}))
async def handle_photo(message: types.Message):
    await media(message)

@router.message(WeatherState.waiting_for_city)
async def process_city_input(message: types.Message, state: FSMContext):
    city = message.text.strip()
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPEN_WEATHER_MAP}&units=metric&lang=ua"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                temp = data["main"]["temp"]
                description = data["weather"][0]["description"]
                await message.answer(f"Погода у місті <b>{city}</b>:\nТемпература: {temp}°C\nОпис: {description}")
            else:
                await message.answer("Не вдалося отримати дані про погоду. Перевірте назву міста.")
    await state.clear()

@router.callback_query(lambda c: c.data == "order")
async def callback_make_order(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Введіть назву продукту:")
    await state.set_state(OrderState.waiting_for_product_name)
    await callback_query.answer()

@router.message(OrderState.waiting_for_product_name)
async def process_product_name(message: types.Message, state: FSMContext):
    await state.update_data(product_name=message.text.strip())
    await message.answer("Введіть кількість (наприклад, 2):")
    await state.set_state(OrderState.waiting_for_quantity)

@router.message(OrderState.waiting_for_quantity)
async def process_quantity(message: types.Message, state: FSMContext):
    quantity_str = message.text.strip()
    if not quantity_str.isdigit():
        await message.answer("Кількість має бути числом! Спробуйте ще раз.")
        return
    quantity = int(quantity_str)
    data = await state.get_data()
    product_name = data.get("product_name")
    add_order(message.from_user.id, product_name, quantity)
    await message.answer(f"Замовлення створено: {product_name}, {quantity} шт")
    await state.clear()

@router.callback_query(lambda c: c.data == "my_orders")
async def cmd_my_orders(callback_query: types.CallbackQuery):
    orders = get_orders_by_user(callback_query.from_user.id)
    if not orders:
        await callback_query.message.answer("У вас немає активних замовлень.")
    else:
        text = "Ваші замовлення:\n" + "\n".join(f"{idx + 1}. {name} - {qty} шт" for idx, (name, qty) in enumerate(orders))
        await callback_query.message.answer(text)
    await callback_query.answer()

@router.message()
async def echo_message(message: types.Message):
    if message.text.lower() == "привіт":
        await message.answer(
            "Вітаю! Я бот для замовлення продукції Рошен.\n"
            "Ось список команд які я можу виконувати:\n"
            "/start - Почати роботу з ботом\n"
            "/help - Допомога\n"
            "/info - Інформація про бота\n"
            "/weather - Інформація про погоду"
        )
    else:
        await message.answer(f"Ви ввели повідомлення \"{message.text}\".\nМожливо, відповідь у /help")

async def main():
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.exception(f"Сталася помилка під час запуску бота: {e}")

if __name__ == "__main__":
    asyncio.run(main())
