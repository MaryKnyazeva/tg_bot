import os
import json
import random
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# Загружаем задания
with open("tasks.json", "r", encoding="utf-8") as f:
    tasks_data = json.load(f)

user_states = {}

def format_table_from_text(raw_text: str) -> str:
    lines = [line.strip() for line in raw_text.strip().splitlines() if line.strip()]
    rows = [line.split("|") for line in lines]
    col_widths = [max(len(cell.strip()) for cell in col) for col in zip(*rows)]

    def format_row(row, sep="│"):
        return sep + sep.join(f" {cell.strip():<{w}} " for cell, w in zip(row, col_widths)) + sep

    border_top = "┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐"
    border_mid = "├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤"
    border_bot = "└" + "┴".join("─" * (w + 2) for w in col_widths) + "┘"

    table = [border_top, format_row(rows[0])]
    if len(rows) > 1:
        table.append(border_mid)
        for row in rows[1:]:
            table.append(format_row(row))
    table.append(border_bot)

    return "📊 Таблица:\n" + "\n".join(table)

async def send_task(update_or_message, user_id: int):
    selected = random.choice(tasks_data)
    user_states[user_id] = selected

    await update_or_message.reply_text(f"📘 Задание №{selected['number']}:\n\n{selected.get('question', '')}")

    if selected.get("images"):
        for url in selected["images"]:
            await update_or_message.reply_photo(photo=url)

    if "Таблица:" in selected["answer"]:
        table_raw = selected["answer"].split("Таблица:")[-1].split("Решение:")[0].strip()
        pretty_table = format_table_from_text(table_raw)
        await update_or_message.reply_text(pretty_table)

    if "Ответ:" in selected["answer"]:
        await update_or_message.reply_text("✏️ Напишите только цифры, без пробелов, в любом порядке")
    else:
        await update_or_message.reply_text("✏️ Напишите ответ в любом формате, вам все равно самостоятельно придется сверяться(")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await send_task(update.message, user_id)

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_input = update.message.text.strip()
    current = user_states.get(user_id, {})
    answer_text = current.get("answer", "")

    match = re.search(r"Ответ:\s*([0-9]+)", answer_text)
    if match:
        correct = match.group(1)
        if ''.join(sorted(user_input)) == ''.join(sorted(correct)):
            reply = "✅ Верно!"
        else:
            reply = f"❌ Неверно.\n\n🔍 Правильный ответ: {correct}"
    else:
        reply = f"Молодец, ты попытался ответить — это уже успех!\n\n🔍 Правильный ответ:\n{answer_text}"

    keyboard = [[InlineKeyboardButton("➡️ Следующий вопрос", callback_data="next_question")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(reply, reply_markup=reply_markup)

async def next_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    await send_task(query.message, user_id)

# 🚀 Запуск
if __name__ == "__main__":
    app = ApplicationBuilder().token(os.environ["TOKEN"]).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))
    app.add_handler(CallbackQueryHandler(next_question, pattern="^next_question$"))

    import asyncio

    async def run_bot():
        await app.initialize()
        await app.start()
        print("🤖 Бот запущен!")
        await app.updater.start_polling()
        await app.updater.idle()

    asyncio.get_event_loop().create_task(run_bot())
    asyncio.get_event_loop().run_forever()
