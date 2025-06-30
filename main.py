from fastapi import FastAPI, Request
from app.bot import bot, dp, TOKEN
from app.handlers import register_handlers
from app.tally import tally_webhook
from aiogram import types

app = FastAPI()

# Регистрация Telegram хендлеров
register_handlers(dp)

@app.post(f"/{TOKEN}")
async def telegram_webhook(request: Request):
    update = types.Update.model_validate(await request.json())
    await dp.feed_update(bot, update)
    return {"ok": True}

@app.post("/tally-webhook")
async def handle_tally_webhook(request: Request):
    return await tally_webhook(request)

@app.get("/")
async def root():
    await bot.delete_webhook()
    await bot.set_webhook(f"https://ttt-1-rpmm.onrender.com/{TOKEN}")
    return {"status": "webhook set"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
