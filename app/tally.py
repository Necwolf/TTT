import logging
from fastapi import Request, HTTPException, status
from app.bot import bot
from app.utils import flatten_fields, format_travel_message
from app.callbacks import travel_buttons
from pydantic import BaseModel

logger = logging.getLogger(__name__)

iduser_test = "188539449"

class TallyWebhookData(BaseModel):
    # Определите необходимые поля, например:
    # contact_person: str | None = None
    # email: str | None = None
    # ...
    # Для универсальности можно оставить raw: dict
    raw: dict

async def tally_webhook(request: Request):
    try:
        raw_data = await request.json()
        flat_data = flatten_fields(raw_data)
        logger.info(f"CLEANED: {flat_data}")

        name = flat_data.get('👤CONTACT PERSON "Товари":')
        logger.info(name)

        await bot.send_message(chat_id=iduser_test, text=name or "No name provided")
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


async def tally_webhook_trip(request: Request):
    try:
        raw_data = await request.json()
        flat_data = flatten_fields(raw_data)
        logger.info(f"CLEANED: {flat_data}")

        message = format_travel_message(flat_data)
        await bot.send_message(
            chat_id=iduser_test,
            text=message,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=travel_buttons()
        )
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Webhook trip error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
