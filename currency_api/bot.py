# -*- coding: utf-8 -*-
from aiogram import Bot, Dispatcher, executor, filters, types
from aiogram.types import ParseMode

API_TOKEN = 'BOT_TOKEN_HERE'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
# @dp.message_handler(filters.CommandStart())
async def send_welcome(message: types.Message):
    # So... At first I want to send something like this:
    await message.reply("Do you want to see many pussies? Are you ready?")

    # fetching urls will take some time, so notify user that everything is OK
    await types.ChatActions.typing()

    # Good bots should send chat actions...
    await types.ChatActions.upload_photo()

    # TODO FINISH
