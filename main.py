import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Body
from app.bot import bot, dp
from app.handlers import register_handlers
from app.tally import tally_webhook, tally_webhook_trip, TallyWebhookData
from aiogram import types
from app.callbacks import router as cb_router
from fastapi import Request, APIRouter
import logging
from fastapi.responses import JSONResponse

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

app = FastAPI()

router = APIRouter()
# Регистрация Telegram хендлеров
register_handlers(dp)
dp.include_router(cb_router)

logging.basicConfig(level=logging.INFO)

@app.post(f"/{TOKEN}")
async def telegram_webhook(request: Request):
    update = types.Update.model_validate(await request.json())
    await dp.feed_update(bot, update)
    return {"ok": True}

@router.api_route("/up", methods=["GET", "POST"])
async def up(request: Request):
    try:
        if request.method == "POST":
            return JSONResponse({"status": "POST accepted"}, status_code=200)
        elif request.method == "GET":
            return JSONResponse({"status": "GET ok"}, status_code=200)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/tally-webhook")
async def handle_tally_webhook(request: Request, data: TallyWebhookData = Body(...)):
    # Передаем data.raw вместо request.json()
    return await tally_webhook(request)

@app.post("/tally-webhook-trip")
async def handle_tally_webhook_trip(request: Request, data: TallyWebhookData = Body(...)):
    return await tally_webhook_trip(request)

@app.get("/")
async def root():
    try:
        await bot.delete_webhook()
        await bot.set_webhook(f"https://ttt-1-rpmm.onrender.com/{TOKEN}")
        return JSONResponse({"status": "webhook set"}, status_code=200)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
