import unittest
import os
from app.utils import generate_pdf_from_data, generate_simple_pdf_from_data

class TestPDFGeneration(unittest.TestCase):
    def setUp(self):
        self.data = {
            "Імʼя:": "Іван",
            "Прізвище:": "Петренко",
            "Електронна адреса:": "ivan@example.com",
            "Місто виїзду:": "Київ",
            "Місто надання послуг:": "Львів",
            "Дата виїзду:": "01.07.2024",
            "Дата повернення:": "05.07.2024",
            "Година виїзду:": "08:00",
            "Година повернення:": "20:00",
            "Проєкт:": "Проект X",
            "№ Договору / Вид надання послуг:": "123/2024",
            "За проживання:": "так",
            "За проїзд:": "ні",
            "Мета поїздки": "Відрядження на конференцію"
        }

    def test_generate_pdf_from_data(self):
        pdf_path = generate_pdf_from_data(self.data)
        self.assertTrue(os.path.exists(pdf_path))
        self.assertGreater(os.path.getsize(pdf_path), 0)
        os.remove(pdf_path)

    def test_generate_simple_pdf_from_data(self):
        pdf_path = generate_simple_pdf_from_data(self.data)
        self.assertTrue(os.path.exists(pdf_path))
        self.assertGreater(os.path.getsize(pdf_path), 0)
        os.remove(pdf_path)

if __name__ == "__main__":
    unittest.main() 