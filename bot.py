import os
import json
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Загружаем задания
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

    selected = random.choice(tasks_data)
    user_states[user_id] = selected
    reply += f"\n\n📘 Следующее задание №{selected['number']}:\n\n{selected['question']}"
    await update.message.reply_text(reply)

# 🚀 Старт без asyncio.run()
if __name__ == "__main__":
    app = ApplicationBuilder().token(os.environ["TOKEN"]).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))

    # Ручной запуск — без закрытия event loop
    import asyncio

    async def run_bot():
        await app.initialize()
        await app.start()
        print("🤖 Бот запущен!")
        await app.updater.start_polling()
        await app.updater.idle()

    asyncio.get_event_loop().create_task(run_bot())
    asyncio.get_event_loop().run_forever()
