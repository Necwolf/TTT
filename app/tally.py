from fastapi import Request
from app.bot import bot
from app.utils import flatten_fields, format_travel_message

iduser_test = "188539449"

async def tally_webhook(request: Request):
    raw_data = await request.json()
    flat_data = flatten_fields(raw_data)
    print("CLEANED:", flat_data)

    name = flat_data.get('👤CONTACT PERSON "Товари":')
    print(name)

    await bot.send_message(chat_id=iduser_test, text=name or "No name provided")
    return {"status": "ok"}


async def tally_webhook_trip(request: Request):
    raw_data = await request.json()
    # print("RAW DATA:", raw_data)
    flat_data = flatten_fields(raw_data)
    print("CLEANED:", flat_data)

    message = format_travel_message(flat_data)
    await bot.send_message(chat_id=iduser_test, text=message, parse_mode="HTML", disable_web_page_preview=True)
    # await bot.send_message(chat_id=iduser_test, text="info delivered")
    return {"status": "ok"}
