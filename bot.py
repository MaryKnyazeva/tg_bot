import os
import json
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Загрузка заданий
with open("tasks.json", "r", encoding="utf-8") as f:
    tasks_data = json.load(f)

user_states = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    selected = random.choice(tasks_data)
    user_states[user_id] = selected

    await update.message.reply_text(f"Привет! Вот задание №{selected['number']}:\n\n{selected['question']}")

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_input = update.message.text.strip()
    correct = user_states.get(user_id, {}).get("answer", "")

    if user_input.lower() in correct.lower():
        reply = "✅ Верно!"
    else:
        reply = f"❌ Неверно.\n\n🔍 Правильный ответ:\n{correct}"

    # Новое задание
    selected = random.choice(tasks_data)
    user_states[user_id] = selected

    reply += f"\n\n📘 Следующее задание №{selected['number']}:\n\n{selected['question']}"
    await update.message.reply_text(reply)

async def main():
    app = ApplicationBuilder().token(os.environ["TOKEN"]).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
