from aiogram import Dispatcher, types
from aiogram.filters import Command

def register_handlers(dp: Dispatcher):
    @dp.message(Command("start"))
    async def start_handler(message: types.Message):
        print(">>> START HANDLER TRIGGERED")
        await message.reply(f"Hello, {message.from_user.first_name}")

    @dp.message()
    async def echo_handler(message: types.Message):
        print(">>> ECHO HANDLER TRIGGERED")
        await message.reply(message.text)
