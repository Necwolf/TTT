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

@app.route('/tally-webhook', methods=['POST'])
def tally_webhook():
    raw_data = request.json
    # print("Tally webhook received:", raw_data)

    cleaned_data = clean_json(raw_data)
    print("Cleaned webhook data:", cleaned_data)

    # Можна також тут зберегти cleaned_data у файл, базу або надіслати далі

    return jsonify({"status": "ok"}), 200

