from flask import Flask, request, jsonify
import os
from threading import Thread
import telebot

TOKEN = '1402083780:AAFI3e8sgo6C1VL71LOi0Wf3MzLXJex6YUY'
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

iduser_test = "188539449"



@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)

    print("--- PROCESSING UPDATE ---")
    print(update)

    def process():
        print("START HANDLER CALL ATTEMPT")
        bot.process_new_updates([update])

    Thread(target=process).start()  # Асинхронная обработка

    return "!", 200


@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://ttt-1-rpmm.onrender.com/' + TOKEN)
    return "!", 200



@app.route('/tally-webhook', methods=['POST'])
def tally_webhook():
    raw_data = request.json
    # print("RAW:", raw_data)

    flat_data = flatten_fields(raw_data)
    print("CLEANED:", flat_data)
    name = flat_data.get('👤CONTACT PERSON "Товари":')
    print(name)
    bot.send_message(iduser_test, name)

    return jsonify({"status": "ok"}), 200
def clean_json(obj):
    if isinstance(obj, dict):
        if 'value' in obj and obj['value'] is None:
            return None
        if 'value' in obj and 'options' in obj:
            id_to_text = {opt['id']: opt['text'] for opt in obj['options'] if 'id' in opt and 'text' in opt}
            if isinstance(obj['value'], list):
                obj['value'] = [id_to_text.get(v, v) for v in obj['value']]
            elif isinstance(obj['value'], str):
                obj['value'] = id_to_text.get(obj['value'], obj['value'])
            obj.pop('options', None)

        return {
            k: v_cleaned
            for k, v in obj.items()
            if (v_cleaned := clean_json(v)) is not None
        }

    elif isinstance(obj, list):
        return [item for item in (clean_json(i) for i in obj) if item is not None]

    return obj
def flatten_fields(data):
    """
    Получает полный JSON от Tally, возвращает словарь: label => value
    """
    result = {}

    if not isinstance(data, dict):
        return result

    fields = data.get("data", {}).get("fields", [])
    for field in fields:
        if field.get("value") is None:
            continue  # пропускаем пустые

        label = field.get("label")
        if not label:
            continue  # без label — пропускаем

        # Подстановка из options
        value = field.get("value")
        options = field.get("options", [])

        if options:
            id_to_text = {opt["id"]: opt["text"] for opt in options if "id" in opt and "text" in opt}
            if isinstance(value, list):
                value = [id_to_text.get(v, v) for v in value]
            elif isinstance(value, str):
                value = id_to_text.get(value, value)

        # Преобразование массива в строку, если нужно
        if isinstance(value, list):
            value = ", ".join(str(v) for v in value)

        result[label] = value

    return result
@bot.message_handler(commands=['start'])
def start(message):
    print("START HANDLER TRIGGERED")
    bot.reply_to(message, 'Hello, ' + message.from_user.first_name)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    bot.reply_to(message, message.text)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)), threaded=True)


