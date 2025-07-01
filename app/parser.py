# app/parser.py
import re

def extract_data_from_message(text: str) -> dict:
    data = {}

    def find(label, separator=":"):
        pattern = rf"{re.escape(label)}{separator}?(.*?)\n"
        match = re.search(pattern, text)
        return match.group(1).strip() if match else ""

    # 👤 Імʼя Прізвище
    name_match = re.search(r"👤\s+([\wА-Яа-яІіЇїЄєҐґ'’\-]+)\s+([\wА-Яа-яІіЇїЄєҐґ'’\-]+)", text)
    if name_match:
        data["Імʼя:"] = name_match.group(1)
        data["Прізвище:"] = name_match.group(2)
    else:
        data["Імʼя:"] = ""
        data["Прізвище:"] = ""

    data["Електронна адреса:"] = find("📧")

    route = find("📍 Виїзд з")
    if "→" in route:
        cities = route.split("→")
        data["Місто виїзду:"] = cities[0].strip()
        data["Місто надання послуг:"] = cities[1].strip()
    else:
        data["Місто виїзду:"] = route
        data["Місто надання послуг:"] = ""

    dates = find("📅 Дата").split("—")
    data["Дата виїзду:"] = dates[0].strip() if len(dates) > 0 else ""
    data["Дата повернення:"] = dates[1].strip() if len(dates) > 1 else ""

    times = find("🕓 Час").split("→")
    data["Година виїзду:"] = times[0].strip() if len(times) > 0 else ""
    data["Година повернення:"] = times[1].strip() if len(times) > 1 else ""

    data["Проєкт:"] = find("🧾 Проєкт")
    data["№ Договору / Вид надання послуг:"] = find("📄 Договір")
    data["За проживання:"] = find("🏨 Проживання")
    data["За проїзд:"] = find("🚌 Проїзд")
    data["Мета поїздки"] = find("🎯 Мета")

    return data