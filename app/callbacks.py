from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

def travel_buttons():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📥 Підтвердити", callback_data="confirm_trip")],
            [InlineKeyboardButton(text="📤 Надіслати email", callback_data="send_email")]
        ]
    )

@router.callback_query(lambda c: c.data == "confirm_trip")
async def handle_confirm(callback: types.CallbackQuery):
    text = callback.message.text or callback.message.caption
    await callback.answer("✅ Відрядження підтверджено", show_alert=True)
    await callback.message.edit_reply_markup()  # Прибираємо кнопки
    print("CONFIRMATION TRIGGERED\n", text)

@router.callback_query(lambda c: c.data == "send_email")
async def handle_email(callback: types.CallbackQuery):
    text = callback.message.text or callback.message.caption
    await callback.answer("📤 Формується email + PDF", show_alert=True)
    print("EMAIL TRIGGERED\n", text)
