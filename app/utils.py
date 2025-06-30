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
    def extract_files(field_name):
        result = []
        value = data.get(field_name)
        if isinstance(value, str):
            try:
                parsed = json.loads(value.replace("'", '"'))
                if isinstance(parsed, dict):
                    result.append(parsed)
                elif isinstance(parsed, list):
                    result.extend(parsed)
            except json.JSONDecodeError:
                pass
        elif isinstance(value, dict):
            result.append(value)
        elif isinstance(value, list):
            result.extend(value)
        return result

    agenda_files = extract_files("Адженда")
    invite_files = extract_files("Запрошення")

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

    def render_file_list(files, label):
        out = f"\n📎 <b>{label}:</b>\n"
        for file in files:
            name = file.get("name", "файл")
            url = file.get("url")
            if url:
                out += f'🔗 <a href="{url}">{name}</a>\n'
        return out

    if agenda_files:
        message += render_file_list(agenda_files, "Адженда")
    if invite_files:
        message += render_file_list(invite_files, "Запрошення")

    if data.get("Підтвердження (Вказані дані є коректними)"):
        message += "✅ Дані підтверджено"

    return message.strip()
