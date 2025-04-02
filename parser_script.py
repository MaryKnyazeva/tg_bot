import time
import google_colab_selenium as gs
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

from docx import Document
from docx.shared import Inches
from docx.oxml.ns import qn
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import requests
from io import BytesIO
import re

import json


# Инициализация драйвера с параметрами
options = Options()
options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36")
options.add_argument("--headless")  # Фоновый режим
options.add_argument("--window-size=1920,1080")  # Размер окна
options.add_argument("--disable-infobars")  # Отключение информационных панелей
options.add_argument("--disable-popup-blocking")  # Отключение всплывающих окон
options.add_argument("--ignore-certificate-errors")  # Игнорирование ошибок SSL
options.add_argument("--incognito")  # Инкогнито-режим
options.add_argument("--disable-blink-features=AutomationControlled")  # Маскировка Selenium

# Создаем драйвер
browser = gs.Chrome(options=options)
driver = gs.Chrome()
driver.get("https://neofamily.ru/biologiya/task-bank?ysclid=m8y9vc3bei55989583&sort_by=id&sort_order=desc&sections=33")
time.sleep(3)

# промотка до конца страницы
last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    ActionChains(driver).move_to_element(driver.find_element(By.TAG_NAME, "footer")).perform()
    time.sleep(2)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# # Получаем приблизительное количество заданий
# task_count = len(driver.find_elements(By.XPATH, '//div[contains(@class, "task")]'))
# print(f"📦 Всего заданий: {task_count}")

results = []
for i in range(1, task_count + 1):
    try:
        print("=" * 80)
        print(f"📘 Задание {i}")

        base = f'//*[@id="__next"]/div[2]/div/main/div/div[2]/div[2]/div/div[2]/div/div[{i}]'

        number_xpath = base + '/div/div[1]/div[1]/div[1]/div[1]'
        topic_xpath = base + '/div/div[1]/div/div[1]/div[2]/div'
        question_xpath = base + '/div/div[2]/div[1]'
        button_xpath = base + '//button[@data-name="solution"]'
        answer_xpath = base + '//div[contains(@class, "border-2") and contains(@class, "p-4")]'

        # Прокручиваем к блоку задания
        task_elem = driver.find_element(By.XPATH, base)
        driver.execute_script("arguments[0].scrollIntoView(true);", task_elem)
        time.sleep(0.5)

        # 1. Номер задания
        number = driver.find_element(By.XPATH, number_xpath)
        print("🔢 Номер задания:", number.text)

        # 1.1 Тема задания (по тексту "Тема:")
        try:
            topic_elem = task_elem.find_element(By.XPATH, './/div[contains(text(), "Тема:")]')
            topic_text = topic_elem.text.replace("Тема:", "").strip()
            print("📌 Тема задания:", topic_text)
        except Exception as e:
            topic_text = "[Тема не найдена]"
            print("⚠️ Тема задания не найдена:", e)

        # 2. Условие
        question = driver.find_element(By.XPATH, question_xpath)
        question_text = question.text

        # 2.1 Поиск таблицы (если есть)
        try:
            table_elem = question.find_element(By.TAG_NAME, "table")

            # Удалим текст таблицы из исходного текста
            table_raw_text = table_elem.text
            question_text = question_text.replace(table_raw_text, "").strip()

            # Форматируем таблицу красиво
            rows = table_elem.find_elements(By.TAG_NAME, "tr")
            table_lines = []

            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "th") or row.find_elements(By.TAG_NAME, "td")
                line = " | ".join(cell.text.strip() for cell in cells)
                table_lines.append(line)

            table_text = "\nТаблица:\n" + "\n".join(table_lines)
            question_text += "\n" + table_text
            print("📊 Таблица найдена, очищена и добавлена.")
        except:
            print("📊 Таблица не найдена.")

        print("🔹 Условие:")
        print(question_text)

        # 3. Картинки
        images = question.find_elements(By.TAG_NAME, "img")
        image_urls = [img.get_attribute("src") for img in images]
        if image_urls:
            print("🖼 Картинки:")
            for url in image_urls:
                print(url)
        else:
            print("🖼 Картинок нет")

        # 4. Нажимаем на кнопку "Показать ответ"
        try:
            show_answer_btn = driver.find_element(By.XPATH, button_xpath)
            driver.execute_script("arguments[0].scrollIntoView(true);", show_answer_btn)
            time.sleep(0.3)
            driver.execute_script("arguments[0].click();", show_answer_btn)
            print("✅ Кнопка нажата!")
        except Exception as e:
            print("⚠️ Кнопка 'Решение' не найдена или не нажалась:", e)

        # 5. Извлекаем ответ
        try:
            wait = WebDriverWait(driver, 10)

            # Ждём появления непустого ответа
            wait.until(lambda d: d.find_element(By.XPATH, answer_xpath).text.strip() != "")

            answer = driver.find_element(By.XPATH, answer_xpath)
            driver.execute_script("arguments[0].scrollIntoView(true);", answer)
            answer_text = answer.text.strip()
            print("✅ Ответ:")
            print(answer_text)

        except TimeoutException:
            print("⚠️ Ответ не найден: истёк таймаут ожидания появления текста.")
            answer_text = "[Ответ не найден]"
        except Exception as e:
            print("⚠️ Ответ не найден:", e)
            answer_text = "[Ответ не найден]"

    except Exception as e:
        print(f"❌ Ошибка при обработке задания {i}:", e)
    results.append({
    "number": number.text,
    "topic": topic_text,
    "question": question_text,
    "images": image_urls,
    "answer": answer_text
    })

# # сохраняем в джейсон
# with open("tasks.json", "w", encoding="utf-8") as f:
#     json.dump(results, f, ensure_ascii=False, indent=2)
