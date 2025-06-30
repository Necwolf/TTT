import json

def flatten_fields(data):
    result = {}
    if not isinstance(data, dict):
        return result

    fields = data.get("data", {}).get("fields", [])
    for field in fields:
        if field.get("value") is None:
            continue

        label = field.get("label")
        if not label:
            continue

        value = field.get("value")
        options = field.get("options", [])

        if options:
            id_to_text = {opt["id"]: opt["text"] for opt in options if "id" in opt and "text" in opt}
            if isinstance(value, list):
                value = [id_to_text.get(v, v) for v in value]
            elif isinstance(value, str):
                value = id_to_text.get(value, value)

        if isinstance(value, list):
            value = ", ".join(str(v) for v in value)

        result[label] = value
    return result

def format_travel_message(data: dict) -> str:
    agenda = data.get("Адженда", {})
    if isinstance(agenda, str):
        # Пробуем заменить одинарные кавычки на двойные, чтобы распарсить как JSON
        try:
            agenda = json.loads(agenda.replace("'", '"'))
        except json.JSONDecodeError:
            agenda = {}

    agenda_url = agenda.get("url", "")

    try:
        message = f"""🚗 Відрядження

👤 <b>{data.get('Імʼя:', '')} {data.get('Прізвище:', '')}</b>
📧 {data.get('Електронна адреса:', '')}
📍 Виїзд з: {data.get('Місто виїзду:', '')} → {data.get('Місто надання послуг:', '')}
📅 Дата: {data.get('Дата виїзду:', '')} — {data.get('Дата повернення:', '')}
🕓 Час: {data.get('Година виїзду:', '')} → {data.get('Година повернення:', '')}

🧾 Проєкт: {data.get('Проєкт:', '')}
📄 Договір: {data.get('№ Договору / Вид надання послуг:', '')}

🏨 Проживання: {data.get('За проживання:', '')}
🚌 Проїзд: {data.get('За проїзд:', '')}

🎯 Мета: {data.get('Мета поїздки', '')}
"""
        if agenda_url:
            message += f'📎 <a href="{agenda_url}">Адженда (PDF)</a>\n'

        if data.get("Підтвердження (Вказані дані є коректними)"):
            message += "✅ Дані підтверджено"

        return message.strip()
    except Exception as e:
        return f"⚠ Помилка при форматуванні повідомлення: {str(e)}"