import json
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import uuid
from datetime import datetime


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
        for idx, file in enumerate(files, 1):
            name = file.get("name", f"файл {idx}")
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


def generate_pdf_from_data(data: dict, template_name: str = "travel_enhanced.html") -> str:
    """
    Генерирует PDF из данных формы, используя улучшенный шаблон

    Args:
        data: Словарь с данными из формы
        template_name: Имя шаблона (по умолчанию "travel_enhanced.html")

    Returns:
        str: Путь к сгенерированному PDF файлу
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
                file_list.append(f'<a href="{url}" target="_blank">{name}</a>')
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
        # Заголовок
        "date_info": datetime.now().strftime("%d.%m.%Y"),
        "req_number": generate_req_number(),

        # Данные о исполнителе
        "executor_name": f"{data.get('Імʼя:', '')} {data.get('Прізвище:', '')}".strip(),
        "email": data.get("Електронна адреса:", ""),
        "contract_info": data.get("№ Договору / Вид надання послуг:", ""),
        "project_name": data.get("Проєкт:", ""),

        # Данные о поездке
        "service_purpose": data.get("Мета поїздки", "Надання послуг поза основним місцем ведення діяльності."),
        "departure_city": data.get("Місто виїзду:", ""),
        "service_city": data.get("Місто надання послуг:", ""),

        # Даты и время
        "departure_date": data.get("Дата виїзду:", ""),
        "departure_time": data.get("Година виїзду:", ""),
        "return_date": data.get("Дата повернення:", ""),
        "return_time": data.get("Година повернення:", ""),

        # Возмещение
        "transport_compensation": format_yes_no(data.get("За проїзд:", "")),
        "accommodation_compensation": format_yes_no(data.get("За проживання:", "")),

        # Файлы
        "invitation_files": format_files("Запрошення"),
        "agenda_files": format_files("Адженда"),
    }

    # Рендеринг HTML
    html_out = template.render(template_data)

    # Генерация PDF
    filename = f"/tmp/travel_enhanced_{uuid.uuid4().hex}.pdf"
    HTML(string=html_out).write_pdf(filename)
    return filename


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