# app/parser.py
import re

def extract_data_from_message(text: str) -> dict:
    data = {}

    def find(key):
        pattern = rf"{re.escape(key)}\s*(.*)"
        match = re.search(pattern, text)
        return match.group(1).strip() if match else ""

    data["Імʼя:"] = find("👤 <b")  # спец обробка нижче
    data["Прізвище:"] = ""

    # Обробка імені/прізвища
    name_match = re.search(r"<b>(.*?)</b>", text)
    if name_match:
        full_name = name_match.group(1).strip()
        parts = full_name.split()
        if len(parts) == 2:
            data["Імʼя:"], data["Прізвище:"] = parts

    data["Електронна адреса:"] = find("📧")
    data["Місто виїзду:"] = find("📍 Виїзд з:")
    data["Місто надання послуг:"] = ""
    if "→" in data["Місто виїзду:"]:
        parts = data["Місто виїзду:"].split("→")
        data["Місто виїзду:"] = parts[0].strip()
        data["Місто надання послуг:"] = parts[1].strip()

    data["Дата виїзду:"] = find("📅 Дата:").split("—")[0].strip()
    data["Дата повернення:"] = find("📅 Дата:").split("—")[1].strip()
    data["Година виїзду:"] = find("🕓 Час:").split("→")[0].strip()
    data["Година повернення:"] = find("🕓 Час:").split("→")[1].strip()
    data["Проєкт:"] = find("🧾 Проєкт:")
    data["№ Договору / Вид надання послуг:"] = find("📄 Договір:")
    data["За проживання:"] = find("🏨 Проживання:")
    data["За проїзд:"] = find("🚌 Проїзд:")
    data["Мета поїздки"] = find("🎯 Мета:")

    return data
