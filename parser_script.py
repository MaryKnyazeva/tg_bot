import json
import time
from selenium import webdriver as gs
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

def fetch_tasks_from_site():
    options = Options()
    options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36")
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--incognito")
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = gs.Chrome(options=options)
    driver.get("https://neofamily.ru/biologiya/task-bank?sections=33&themes=152")
    time.sleep(3)

    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    results = []
    task_count = len(driver.find_elements(By.XPATH, '//div[contains(@class, "task")]'))
    print(f"📦 Всего заданий: {task_count}")

    for i in range(1, task_count + 1):
        try:
            print("=" * 80)
            print(f"📘 Задание {i}")

            base = f'//*[@id="__next"]/div[2]/div/main/div/div[2]/div[2]/div/div[2]/div/div[{i}]'
            number_xpath = base + '/div/div[1]/div[1]/div[1]/div[1]'
            question_xpath = base + '/div/div[2]/div[1]'
            button_xpath = base + '//button[@data-name="solution"]'
            answer_xpath = base + '//div[contains(@class, "border-2") and contains(@class, "p-4")]'

            task_elem = driver.find_element(By.XPATH, base)
            driver.execute_script("arguments[0].scrollIntoView(true);", task_elem)
            time.sleep(0.5)

            number = driver.find_element(By.XPATH, number_xpath)
            print("🔢 Номер задания:", number.text)

            question = driver.find_element(By.XPATH, question_xpath)
            question_text = question.text

            try:
                table_elem = question.find_element(By.TAG_NAME, "table")
                table_raw_text = table_elem.text
                question_text = question_text.replace(table_raw_text, "").strip()

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

            images = question.find_elements(By.TAG_NAME, "img")
            image_urls = [img.get_attribute("src") for img in images]
            if image_urls:
                print("🖼 Картинки:")
                for url in image_urls:
                    print(url)
            else:
                print("🖼 Картинок нет")

            try:
                show_answer_btn = driver.find_element(By.XPATH, button_xpath)
                driver.execute_script("arguments[0].scrollIntoView(true);", show_answer_btn)
                time.sleep(0.3)
                driver.execute_script("arguments[0].click();", show_answer_btn)
                print("✅ Кнопка нажата!")
            except Exception as e:
                print("⚠️ Кнопка 'Решение' не нажалась:", e)

            try:
                wait = WebDriverWait(driver, 10)
                wait.until(lambda d: d.find_element(By.XPATH, answer_xpath).text.strip() != "")
                answer = driver.find_element(By.XPATH, answer_xpath)
                driver.execute_script("arguments[0].scrollIntoView(true);", answer)
                answer_text = answer.text.strip()
                print("✅ Ответ:")
                print(answer_text)
            except TimeoutException:
                print("⚠️ Ответ не найден (таймаут).")
                answer_text = "[Ответ не найден]"
            except Exception as e:
                print("⚠️ Ошибка при получении ответа:", e)
                answer_text = "[Ответ не найден]"

            results.append({
                "number": number.text,
                "question": question_text,
                "images": image_urls,
                "answer": answer_text
            })

        except Exception as e:
            print(f"❌ Ошибка при обработке задания {i}:", e)

    driver.quit()
    with open("tasks.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Сохранено заданий: {len(results)} в tasks.json")

if __name__ == "__main__":
    fetch_tasks_from_site()
