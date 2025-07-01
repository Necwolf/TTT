from fastapi import FastAPI, Request
from app.bot import bot, dp, TOKEN
from app.handlers import register_handlers
from app.tally import tally_webhook, tally_webhook_trip
from aiogram import types
from app.callbacks import router as cb_router
from fastapi import Request, APIRouter

app = FastAPI()

router = APIRouter()
# Регистрация Telegram хендлеров
register_handlers(dp)
dp.include_router(cb_router)

@app.post(f"/{TOKEN}")
async def telegram_webhook(request: Request):
    update = types.Update.model_validate(await request.json())
    await dp.feed_update(bot, update)
    return {"ok": True}

@router.api_route("/up", methods=["GET", "POST"])
async def up(request: Request):
    if request.method == "POST":
        # обробка POST
        return {"status": "POST accepted"}
    elif request.method == "GET":
        # обробка GET
        return {"status": "GET ok"}


@app.post("/tally-webhook")
async def handle_tally_webhook(request: Request):
    return await tally_webhook(request)

@app.post("/tally-webhook-trip")
async def handle_tally_webhook(request: Request):
    return await tally_webhook_trip(request)

@app.get("/")
async def root():
    await bot.delete_webhook()
    await bot.set_webhook(f"https://ttt-1-rpmm.onrender.com/{TOKEN}")
    return {"status": "webhook set"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
