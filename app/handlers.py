from aiogram import Dispatcher, types

def register_handlers(dp: Dispatcher):
    @dp.message(commands=["start"])
    async def start_handler(message: types.Message):
        print(">>> START HANDLER TRIGGERED")
        await message.reply(f"Hello, {message.from_user.first_name}")

    @dp.message()
    async def echo_handler(message: types.Message):
        print(">>> ECHO HANDLER TRIGGERED")
        await message.reply(message.text)
