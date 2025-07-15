import json
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import uuid
from datetime import datetime
import tempfile


LOCALIZATION = {
    "trip": "🚗 Відрядження",
    "name": "Імʼя:",
    "surname": "Прізвище:",
    "email": "Електронна адреса:",
    "from_city": "Місто виїзду:",
    "to_city": "Місто надання послуг:",
    "from_date": "Дата виїзду:",
    "to_date": "Дата повернення:",
    "from_time": "Година виїзду:",
    "to_time": "Година повернення:",
    "project": "Проєкт:",
    "contract": "№ Договору / Вид надання послуг:",
    "housing": "За проживання:",
    "transport": "За проїзд:",
    "purpose": "Мета поїздки",
    "agenda": "Адженда",
    "invitation": "Запрошення",
    "confirm": "Підтвердження (Вказані дані є коректними)",
    "confirmed": "✅ Дані підтверджено",
}


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
    L = LOCALIZATION
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
    agenda_files = extract_files(L["agenda"])
    invite_files = extract_files(L["invitation"])
    message = f"{L['trip']}\n\n"
    message += f"👤 <b>{data.get(L['name'], '')} {data.get(L['surname'], '')}</b>\n"
    message += f"📧 {data.get(L['email'], '')}\n"
    message += f"📍 Виїзд з: {data.get(L['from_city'], '')} → {data.get(L['to_city'], '')}\n"
    message += f"📅 Дата: {data.get(L['from_date'], '')} — {data.get(L['to_date'], '')}\n"
    message += f"🕓 Час: {data.get(L['from_time'], '')} → {data.get(L['to_time'], '')}\n\n"
    message += f"🧾 Проєкт: {data.get(L['project'], '')}\n"
    message += f"📄 Договір: {data.get(L['contract'], '')}\n\n"
    message += f"�� Проживання: {data.get(L['housing'], '')}\n"
    message += f"🚌 Проїзд: {data.get(L['transport'], '')}\n\n"
    message += f"🎯 Мета: {data.get(L['purpose'], '')}\n"
    def render_file_list(files, label):
        out = f"\n📎 <b>{label}:</b>\n"
        for idx, file in enumerate(files, 1):
            name = file.get("name", f"файл {idx}")
            url = file.get("url")
            if url:
                out += f'🔗 <a href="{url}">{name}</a>\n'
        return out
    if agenda_files:
        message += render_file_list(agenda_files, L["agenda"])
    if invite_files:
        message += render_file_list(invite_files, L["invitation"])
    if data.get(L["confirm"]):
        message += L["confirmed"]
    return message.strip()


def generate_pdf_from_data(data: dict, template_name: str = "travel_enhanced.html") -> str:
    """
    Генерирует PDF из данных формы, используя улучшенный шаблон
    """
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template(template_name)

    # Функция для обработки файлов
    def format_files(field_name):
        files = []
        value = data.get(field_name, "")
        if isinstance(value, str) and value:
            try:
                parsed = json.loads(value.replace("'", '"'))
                if isinstance(parsed, dict):
                    files.append(parsed)
                elif isinstance(parsed, list):
                    files.extend(parsed)
            except json.JSONDecodeError:
                pass
        elif isinstance(value, dict):
            files.append(value)
        elif isinstance(value, list):
            files.extend(value)

        # Форматирование списка файлов для отображения
        if not files:
            return "-"

        file_list = []
        for file in files:
            name = file.get("name", "Файл")
            url = file.get("url", "")
            if url:
                # Сокращение длинных URL для лучшего отображения
                short_url = url[:50] + "..." if len(url) > 50 else url
                file_list.append(f'<a href="{url}" target="_blank">{name} ({short_url})</a>')
            else:
                file_list.append(name)

        return "<br>".join(file_list) if file_list else "-"

    # Функция для генерации номера запроса
    def generate_req_number():
        now = datetime.now()
        return f"REQ-{now.strftime('%d')}/{now.strftime('%y')}"

    # Функция для форматирования ответов Да/Нет
    def format_yes_no(value):
        if isinstance(value, str):
            value = value.lower()
            if value in ['так', 'yes', 'true', '1', 'да']:
                return "Так"
            elif value in ['ні', 'no', 'false', '0', 'нет']:
                return "Ні"
        return value if value else "Ні"

    # Подготовка данных для шаблона
    template_data = {
        "date_info": datetime.now().strftime("%d.%m.%Y"),
        "req_number": generate_req_number(),
        "executor_name": f"{data.get('Імʼя:', '')} {data.get('Прізвище:', '')}".strip(),
        "email": data.get("Електронна адреса:", ""),
        "contract_info": data.get("№ Договору / Вид надання послуг:", ""),
        "project_name": data.get("Проєкт:", ""),
        "service_purpose": data.get("Мета поїздки", "Надання послуг поза основним місцем ведення діяльності."),
        "departure_city": data.get("Місто виїзду:", ""),
        "service_city": data.get("Місто надання послуг:", ""),
        "departure_date": data.get("Дата виїзду:", ""),
        "departure_time": data.get("Година виїзду:", ""),
        "return_date": data.get("Дата повернення:", ""),
        "return_time": data.get("Година повернення:", ""),
        "transport_compensation": format_yes_no(data.get("За проїзд:", "")),
        "accommodation_compensation": format_yes_no(data.get("За проживання:", "")),
        "invitation_files": format_files("Запрошення"),
        "agenda_files": format_files("Адженда"),
    }

    # Рендеринг HTML
    html_out = template.render(template_data)

    # Генерация PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        HTML(string=html_out).write_pdf(tmp.name)
        return tmp.name


def generate_simple_pdf_from_data(data: dict) -> str:
    """
    Оригинальная функция для генерации простого PDF (для обратной совместимости)
    """
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("travel.html")

    html_out = template.render({
        "first_name": data.get("Імʼя:", ""),
        "last_name": data.get("Прізвище:", ""),
        "from_city": data.get("Місто виїзду:", ""),
        "to_city": data.get("Місто надання послуг:", ""),
        "from_date": data.get("Дата виїзду:", ""),
        "to_date": data.get("Дата повернення:", ""),
        "from_time": data.get("Година виїзду:", ""),
        "to_time": data.get("Година повернення:", ""),
        "email": data.get("Електронна адреса:", ""),
        "project": data.get("Проєкт:", ""),
        "contract": data.get("№ Договору / Вид надання послуг:", ""),
        "housing": data.get("За проживання:", ""),
        "transport": data.get("За проїзд:", ""),
        "purpose": data.get("Мета поїздки", "")
    })

    filename = f"/tmp/travel_{uuid.uuid4().hex}.pdf"
    HTML(string=html_out).write_pdf(filename)
    return filename