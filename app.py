import os
from flask import Flask, request, jsonify
import whisper
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

app = Flask(__name__)

# Загружаем модель Whisper
model = whisper.load_model("large-v3")  # Лучшая для русского

# Твой Telegram токен от @BotFather
TELEGRAM_TOKEN = "7639183192:AAHqcnLAJCavdlh2BnFasDgsuNLFUmS5q1s"

# Настройка Telegram-бота
application = Application.builder().token(TELEGRAM_TOKEN).build()

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id

    # Скачиваем голосовое сообщение
    voice_file = await update.message.voice.get_file()
    file_path = f"voice_{user_id}.ogg"
    await voice_file.download_to_drive(file_path)

    # Транскрибация
    result = model.transcribe(file_path, language="ru")
    transcribed_text = result["text"]

    # Удаляем файл
    os.remove(file_path)

    # Отправляем результат
    await context.bot.send_message(chat_id=chat_id, text=f"Расшифровка: {transcribed_text}")
    return transcribed_text

# Добавляем обработчик голосовых сообщений
application.add_handler(MessageHandler(filters.VOICE, handle_voice))

# Flask маршрут для проверки работоспособности
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    # Запускаем Telegram-бота в polling-режиме
    application.run_polling()
