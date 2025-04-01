import os
import json
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    selected = random.choice(tasks_data)
    user_states[user_id] = selected

    await update.message.reply_text(f"📘 Задание №{selected['number']}:\n\n{selected['question']}")

    if selected.get("images"):
        for url in selected["images"]:
            await update.message.reply_photo(photo=url)

    if "Таблица:" in selected["answer"]:
        table_raw = selected["answer"].split("Таблица:")[-1].split("Решение:")[0].strip()
        pretty_table = format_table_from_text(table_raw)
        await update.message.reply_text(pretty_table)

    await update.message.reply_text("✏️ Введите свой ответ:")

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_input = update.message.text.strip()
    correct = user_states.get(user_id, {}).get("answer", "")

    if user_input.lower() in correct.lower():
        reply = "✅ Верно!"
    else:
        reply = f"❌ Неверно.\n\n🔍 Правильный ответ:\n{correct}"

    selected = random.choice(tasks_data)
    user_states[user_id] = selected

    await update.message.reply_text(reply)
    await update.message.reply_text(f"\n📘 Следующее задание №{selected['number']}:\n\n{selected['question']}")

    if selected.get("images"):
        for url in selected["images"]:
            await update.message.reply_photo(photo=url)

    if "Таблица:" in selected["answer"]:
        table_raw = selected["answer"].split("Таблица:")[-1].split("Решение:")[0].strip()
        pretty_table = format_table_from_text(table_raw)
        await update.message.reply_text(pretty_table)

    await update.message.reply_text("✏️ Введите свой ответ:")

# 🚀 Старт без asyncio.run()
if __name__ == "__main__":
    app = ApplicationBuilder().token(os.environ["TOKEN"]).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))

    import asyncio

    async def run_bot():
        await app.initialize()
        await app.start()
        print("🤖 Бот запущен!")
        await app.updater.start_polling()
        await app.updater.idle()

    asyncio.get_event_loop().create_task(run_bot())
    asyncio.get_event_loop().run_forever()
