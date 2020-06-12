# -*- coding: utf-8 -*-
from aiogram import Bot, Dispatcher, executor, filters, types
from aiogram.types import ParseMode

from db.db import get_exchange_rate, db_currency
from utils.utils import GetAndPreparedBanksData
from utils.views_utils import currency_rate_dict_to_str

API_TOKEN = 'BOT_TOKEN_HERE'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
# @dp.message_handler(filters.CommandStart())
async def start_command(message: types.Message):
    # So... At first I want to send something like this:
    # await message.reply("Do you want to see many pussies? Are you ready?")

    # fetching urls will take some time, so notify user that everything is OK
    await types.ChatActions.typing()

    await message.reply("Hi! I am currency bot.")

    await types.ChatActions.typing()

    await message.reply("Type /help to get all commands :)")
    # Good bots should send chat actions...
    # await types.ChatActions.upload_photo()


@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):

    await types.ChatActions.typing()
    commands = [
        '/help you can get a help :)',
        '/cer --> currencies exchange rate between yesterday and today',
        '/today --> currencies prices today',
        '/start --> Just for get bot greeting :)',
    ]
    await message.reply('\n'.join(commands))


@dp.message_handler(commands=['cer'])
async def currencies_exchange_rate(message: types.Message):
    await types.ChatActions.typing()
    conn = await db_currency()
    data = await get_exchange_rate(conn)
    await message.reply('{0}'.format(currency_rate_dict_to_str(data)))


@dp.message_handler(commands=['today'])
async def today_curr_exc_rate(message: types.Message):
    await types.ChatActions.typing()
    data = await GetAndPreparedBanksData().get_data_from_banks()
    await message.reply('{0}'.format(data))


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)