from flask import Flask, request, jsonify

app = Flask(__name__)

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

@app.route('/tally-webhook', methods=['POST'])
def tally_webhook():
    raw_data = request.json
    print("RAW:", raw_data)

    flat_data = flatten_fields(raw_data)
    print("CLEANED:", flat_data)

    return jsonify({"status": "ok"}), 200
# def tally_webhook():
#     raw_data = request.json
#     # print("Tally webhook received:", raw_data)
#
#     cleaned_data = clean_json(raw_data)
#     print("Cleaned webhook data:", cleaned_data)
#
#     # Можна також тут зберегти cleaned_data у файл, базу або надіслати далі
#
#     return jsonify({"status": "ok"}), 200

