from aiogram import Dispatcher, types
from aiogram.filters import Command
import logging

logger = logging.getLogger(__name__)

def register_handlers(dp: Dispatcher):
    @dp.message(Command("start"))
    async def start_handler(message: types.Message):
        logger.info(">>> START HANDLER TRIGGERED")
        await message.reply(f"Hello, {message.from_user.first_name}")

    @dp.message()
    async def echo_handler(message: types.Message):
        logger.info(">>> ECHO HANDLER TRIGGERED")
        await message.reply(message.text)
