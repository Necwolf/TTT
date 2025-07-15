import unittest
from app.parser import extract_data_from_message

class TestParser(unittest.TestCase):
    def test_extract_data_from_message_full(self):
        text = (
            "👤 Іван Петренко\n"
            "📧 ivan@example.com\n"
            "📍 Виїзд з: Київ → Львів\n"
            "📅 Дата: 01.07.2024—05.07.2024\n"
            "🕓 Час: 08:00→20:00\n"
            "🧾 Проєкт: Проект X\n"
            "📄 Договір: 123/2024\n"
            "🏨 Проживання: так\n"
            "🚌 Проїзд: ні\n"
            "🎯 Мета: Відрядження на конференцію\n"
        )
        data = extract_data_from_message(text)
        self.assertEqual(data["Імʼя:"], "Іван")
        self.assertEqual(data["Прізвище:"], "Петренко")
        self.assertEqual(data["Електронна адреса:"], "ivan@example.com")
        self.assertEqual(data["Місто виїзду:"], "Київ")
        self.assertEqual(data["Місто надання послуг:"], "Львів")
        self.assertEqual(data["Дата виїзду:"], "01.07.2024")
        self.assertEqual(data["Дата повернення:"], "05.07.2024")
        self.assertEqual(data["Година виїзду:"], "08:00")
        self.assertEqual(data["Година повернення:"], "20:00")
        self.assertEqual(data["Проєкт:"], "Проект X")
        self.assertEqual(data["№ Договору / Вид надання послуг:"], "123/2024")
        self.assertEqual(data["За проживання:"], "так")
        self.assertEqual(data["За проїзд:"], "ні")
        self.assertEqual(data["Мета поїздки"], "Відрядження на конференцію")

    def test_extract_data_from_message_partial(self):
        text = "👤 Олена Ковальчук\n📧 \n📍 Виїзд з: Одеса\n"
        data = extract_data_from_message(text)
        self.assertEqual(data["Імʼя:"], "Олена")
        self.assertEqual(data["Прізвище:"], "Ковальчук")
        self.assertEqual(data["Електронна адреса:"], "")
        self.assertEqual(data["Місто виїзду:"], "Одеса")
        self.assertEqual(data["Місто надання послуг:"], "")

if __name__ == "__main__":
    unittest.main() 