from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from app.utils import generate_pdf_from_data, generate_simple_pdf_from_data
from app.parser import extract_data_from_message

router = Router()


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


@router.callback_query(lambda c: c.data == "confirm_trip")
async def handle_confirm(callback: types.CallbackQuery):
    """Обработчик подтверждения командировки"""
    text = callback.message.text or callback.message.caption
    await callback.answer("✅ Відрядження підтверджено", show_alert=True)
    await callback.message.edit_reply_markup()  # Убираем кнопки
    print("CONFIRMATION TRIGGERED\n", text)


@router.callback_query(lambda c: c.data == "send_pdf_detailed")
async def handle_detailed_pdf(callback: types.CallbackQuery):
    """Обработчик генерации детального PDF"""
    try:
        text = callback.message.text
        data = extract_data_from_message(text)

        # Генерируем детальный PDF с новым шаблоном
        pdf_path = generate_pdf_from_data(data, "travel_enhanced.html")

        await callback.message.answer_document(
            FSInputFile(pdf_path),
            caption="📝 Згенеровано детальний PDF звіт про відрядження"
        )
        await callback.answer("✅ Детальний PDF згенеровано")

    except Exception as e:
        await callback.answer("❌ Помилка при генерації PDF", show_alert=True)
        print(f"Error generating detailed PDF: {e}")


@router.callback_query(lambda c: c.data == "send_pdf_simple")
async def handle_simple_pdf(callback: types.CallbackQuery):
    """Обработчик генерации простого PDF"""
    try:
        text = callback.message.text
        data = extract_data_from_message(text)

        # Генерируем простой PDF со старым шаблоном
        pdf_path = generate_simple_pdf_from_data(data)

        await callback.message.answer_document(
            FSInputFile(pdf_path),
            caption="📝 Згенеровано простий PDF звіт про відрядження"
        )
        await callback.answer("✅ Простий PDF згенеровано")

    except Exception as e:
        await callback.answer("❌ Помилка при генерації PDF", show_alert=True)
        print(f"Error generating simple PDF: {e}")


@router.callback_query(lambda c: c.data == "send_email")
async def handle_email(callback: types.CallbackQuery):
    """Обработчик отправки email (пока заглушка)"""
    try:
        text = callback.message.text
        data = extract_data_from_message(text)

        # Пока просто генерируем PDF как и раньше
        pdf_path = generate_pdf_from_data(data)

        await callback.message.answer_document(
            FSInputFile(pdf_path),
            caption="📧 Підготовлено для відправки email"
        )
        await callback.answer("✅ Документ підготовлено для email")

    except Exception as e:
        await callback.answer("❌ Помилка при підготовці email", show_alert=True)
        print(f"Error preparing email: {e}")