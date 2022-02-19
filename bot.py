import logging
import os

import aiohttp
from aiogram import Bot, Dispatcher, executor, types

import food_data

BOT_API_TOKEN = os.getenv("BOT_API_TOKEN")

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=BOT_API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start", "help"])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply(
        "Hi! This bot will help you to calculate nutrients for food from FoodData Central system. "
        "To use it, simply send a message containing FDC ID of the food and the mass "
        "of the portion in grams. These two values must be separated by space, for example: "
        "`167725 200`",
    )


@dp.message_handler()
async def calculate_food_nutrients(message: types.Message):
    try:
        fdc_id, mass = message.text.split(" ")
        mass = float(mass)
    except ValueError:
        await message.answer(
            "Invalid format. Should be: `fds_id grams`. For example: `167725 200`",
        )
        return

    try:
        food_info = await food_data.calculate_food_nutrients(fdc_id, mass)
    except aiohttp.ClientResponseError as e:
        await message.answer(
            f"Got response with status code {e.status}. "
            f"Make sure you entered correct FDC ID."
        )
    except Exception as e:
        await message.answer(
            f"Got unexpected error: {repr(e)}. \nContact the developer: @a1d4r"
        )
    else:
        await message.answer(
            f"Food: {food_info.food}\n"
            f"Mass: {food_info.mass}\n"
            f"Energy, kcal: {food_info.energy}\n"
            f"Protein, g: {food_info.protein}\n"
            f"Carbohydrates, g: {food_info.carbohydrates}\n"
            f"Sugar, g: {food_info.sugar}\n"
            f"Fats, g: {food_info.fats}\n"
            f"Saturated fat, g: {food_info.saturated_fat}\n"
            f"Cholesterol, mg: {food_info.cholesterol}\n"
            f"Vitamin C, mg: {food_info.vitamin_c}\n"
            f"Fe, mg: {food_info.fe}\n"
            f"Ca, mg: {food_info.ca}\n"
            f"\nCSV (copy it and paste to Excel): \n{food_info}"
        )


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
