import asyncio
from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from app.utils import generate_pdf_from_data, generate_simple_pdf_from_data
from app.parser import extract_data_from_message
import logging
from urllib.parse import quote
import re

router = Router()
logger = logging.getLogger(__name__)


def travel_buttons():
    """Создает inline клавиатуру для сообщений о командировке"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📥 Підтвердити", callback_data="confirm_trip")],
            [
                InlineKeyboardButton(text="📄 PDF (детальний)", callback_data="send_pdf_detailed"),
                InlineKeyboardButton(text="📄 PDF (простий)", callback_data="send_pdf_simple")
            ],
            [InlineKeyboardButton(text="📤 Надіслати email", callback_data="send_email")]
        ]
    )


def gmail_mailto_button(email, subject, body):
    mailto = (
        f"mailto:{email}?subject={quote(subject)}&body={quote(body)}"
    )
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📧 Відкрити Gmail", url=mailto)]
        ]
    )


def gmail_web_url(email, subject, body):
    from urllib.parse import quote
    url = (
        f"https://mail.google.com/mail/?view=cm"
        f"&to={quote(email)}"
        f"&su={quote(subject)}"
        f"&body={quote(body)}"
    )
    return url


async def generate_pdf_async(data, template_name=None):
    loop = asyncio.get_event_loop()
    if template_name:
        return await loop.run_in_executor(None, generate_pdf_from_data, data, template_name)
    else:
        return await loop.run_in_executor(None, generate_simple_pdf_from_data, data)


@router.callback_query(lambda c: c.data == "confirm_trip")
async def handle_confirm(callback: types.CallbackQuery):
    text = callback.message.text or callback.message.caption or ""
    try:
        await callback.answer("✅ Відрядження підтверджено", show_alert=True)
    except Exception as e:
        logger.warning(f"callback.answer failed: {e}")
    try:
        await callback.message.edit_reply_markup()
    except Exception as e:
        logger.warning(f"edit_reply_markup failed: {e}")
    # Извлечь ФИО из сообщения
    fio_match = re.search(r"<b>([^<]+)</b>", text)
    fio = fio_match.group(1) if fio_match else ""
    subject = f"{fio} тест из телеграм"
    email = "reusn92@gmail.com"
    gmail_url = gmail_web_url(email, subject, text)
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📧 Відкрити Gmail", url=gmail_url)]
        ]
    )
    await callback.message.answer(
        "Натисніть кнопку нижче, щоб відкрити Gmail з підготовленим листом:",
        reply_markup=markup
    )
    print("CONFIRMATION TRIGGERED\n", text)


@router.callback_query(lambda c: c.data == "send_pdf_detailed")
async def handle_detailed_pdf(callback: types.CallbackQuery):
    """Обработчик генерации детального PDF"""
    try:
        text = callback.message.text
        data = extract_data_from_message(text)
        pdf_path = await generate_pdf_async(data, "travel_enhanced.html")

        await callback.message.answer_document(
            FSInputFile(pdf_path),
            caption="📝 Згенеровано детальний PDF звіт про відрядження"
        )
        await callback.answer("✅ Детальний PDF згенеровано")

    except Exception as e:
        await callback.answer("❌ Помилка при генерації PDF", show_alert=True)
        logger.error(f"Error generating detailed PDF: {e}")


@router.callback_query(lambda c: c.data == "send_pdf_simple")
async def handle_simple_pdf(callback: types.CallbackQuery):
    """Обработчик генерации простого PDF"""
    try:
        text = callback.message.text
        data = extract_data_from_message(text)
        pdf_path = await generate_pdf_async(data)

        await callback.message.answer_document(
            FSInputFile(pdf_path),
            caption="📝 Згенеровано простий PDF звіт про відрядження"
        )
        await callback.answer("✅ Простий PDF згенеровано")

    except Exception as e:
        await callback.answer("❌ Помилка при генерації PDF", show_alert=True)
        logger.error(f"Error generating simple PDF: {e}")


@router.callback_query(lambda c: c.data == "send_email")
async def handle_email(callback: types.CallbackQuery):
    """Обработчик отправки email (пока заглушка)"""
    try:
        text = callback.message.text
        data = extract_data_from_message(text)
        pdf_path = await generate_pdf_async(data, "travel_enhanced.html")

        await callback.message.answer_document(
            FSInputFile(pdf_path),
            caption="📧 Підготовлено для відправки email"
        )
        await callback.answer("✅ Документ підготовлено для email")

    except Exception as e:
        await callback.answer("❌ Помилка при підготовці email", show_alert=True)
        logger.error(f"Error preparing email: {e}")