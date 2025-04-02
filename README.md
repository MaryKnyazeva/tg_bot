# Telegram бот ЕГЭ по биологии

Этот бот помогает готовиться к ЕГЭ по биологии, предлагая задания в формате Telegram-диалога. Пользователь получает случайный вопрос из набора, может видеть таблицы, изображения, вводить ответы и получать обратную связь — включая правильный ответ и объяснение.

## Что умеет бот

- Показывает случайные задания из файла `tasks.json`
- Если к заданию прикреплены изображения — отправляет их
- Умеет красиво оформлять таблицы (если они есть в задании)
- Принимает ответ от пользователя и проверяет его
- Показывает правильный ответ и объяснение
- После каждого задания предлагает перейти к следующему

---

## Как это работает

- Вся логика бота — в файле `bot.py`
- Flask-сервер (`background.py`) нужен, чтобы бот не выключался на бесплатном Replit
- Replit-проект «будит» специальный сайт, а UptimeRobot шлёт на него запросы каждые 5 минут — так бот остаётся онлайн 24/7
- Все задания хранятся в `tasks.json`

---

## Пример задания
Задание №5

Какие признаки характерны для хордовых животных?

После этого бот:
- Отправит картинку (если она есть)
- Покажет таблицу (если есть)
- Попросит ввести ответ
- Проверит, правильно ли ты ответил
- Объяснит решение
- Предложит следующее задание

---

## Как запустить

1. Сохрани свой Telegram Bot Token в переменную окружения `TOKEN` (в Replit → Secrets)
2. Убедись, что рядом есть файл `tasks.json` с заданиями
3. Запусти `bot.py`
4. Если всё настроено правильно — бот начнёт работать!

---

## Структура проекта

- `bot.py` — главный файл, где работает логика Telegram-бота
- `background.py` — Flask-сервер, который не даёт Replit «заснуть»
- `tasks.json` — список заданий (в формате JSON)
- `.replit` и `requirements.txt` — технические настройки проекта

---

## Пример задания в JSON

```json
{
  "number": 12,
  "question": "Какая структура участвует в фотосинтезе?",
  "answer": "Ответ: 3\nРешение: Это хлоропласт — органоид, содержащий хлорофилл.",
  "images": ["https://example.com/image.jpg"]
}






