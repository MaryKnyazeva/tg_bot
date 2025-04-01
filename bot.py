import json
import time
from selenium import webdriver as gs
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

def fetch_tasks_from_site():
    options = Options()
    options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64)")
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

    for i in range(1, task_count + 1):
        try:
            base = f'//*[@id="__next"]/div[2]/div/main/div/div[2]/div[2]/div/div[2]/div/div[{i}]'
            question_xpath = base + '/div/div[2]/div[1]'
            button_xpath = base + '//button[@data-name="solution"]'
            answer_xpath = base + '//div[contains(@class, "border-2") and contains(@class, "p-4")]'

            task_elem = driver.find_element(By.XPATH, base)
            driver.execute_script("arguments[0].scrollIntoView(true);", task_elem)
            time.sleep(0.5)

            question_elem = driver.find_element(By.XPATH, question_xpath)
            question_text = question_elem.text

            try:
                table_elem = question_elem.find_element(By.TAG_NAME, "table")
                table_text = "\nТаблица:\n"
                rows = table_elem.find_elements(By.TAG_NAME, "tr")
                for row in rows:
                    cells = row.find_elements(By.TAG_NAME, "th") or row.find_elements(By.TAG_NAME, "td")
                    line = " | ".join(cell.text.strip() for cell in cells)
                    table_text += line + "\n"
                question_text += "\n" + table_text
            except:
                pass

            try:
                show_answer_btn = driver.find_element(By.XPATH, button_xpath)
                driver.execute_script("arguments[0].click();", show_answer_btn)
                time.sleep(0.5)
            except:
                pass

            try:
                wait = WebDriverWait(driver, 10)
                wait.until(lambda d: d.find_element(By.XPATH, answer_xpath).text.strip() != "")
                answer_text = driver.find_element(By.XPATH, answer_xpath).text.strip()
            except TimeoutException:
                answer_text = "[Ответ не найден]"

            results.append({
                "question": question_text,
                "answer": answer_text
            })

        except Exception as e:
            print(f"Ошибка при парсинге задания {i}: {e}")
            continue

    driver.quit()
    return results

if __name__ == '__main__':
    tasks = fetch_tasks_from_site()
    with open("tasks.json", "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)
    print(f"✅ Сохранено заданий: {len(tasks)} в tasks.json")
