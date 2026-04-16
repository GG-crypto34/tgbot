TOKEN = "8794465943:AAFNHtBInP_u0K8RMM3f1c6SSb8-dA96GxE"

import logging
from pathlib import Path

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

from process import process_image


WAITING_IMAGE = 1
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Доступные команды:\n"
        "/help — описание\n"
        "/find — отправить изображение на обработку\n"
        "/cancel — отмена"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "После команды /find отправь картинку.\n"
        "Можно также добавить подпись к изображению."
    )

async def find_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Отправь изображение для обработки.\n"
        "Можно с подписью.\n"
        "Для отмены введи /cancel"
    )
    return WAITING_IMAGE

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if message is None or not message.photo:
        await update.message.reply_text("Не вижу изображения. Отправь фото еще раз.")
        return WAITING_IMAGE

    # Берем самое качественное фото из списка размеров
    photo = message.photo[-1]
    caption = (message.caption or "").strip()

    # Получаем файл и скачиваем локально
    telegram_file = await photo.get_file()
    file_path = DOWNLOAD_DIR / f"{message.from_user.id}_{message.message_id}.jpg"
    await telegram_file.download_to_drive(custom_path=str(file_path))

    try:
        # process_image должен вернуть строку
        result_text = process_image(
            image_path=str(file_path),
            text=caption,
        )

        if not result_text:
            result_text = "Обработка завершена, но результат пустой."

        await update.message.reply_text(result_text)

    except Exception as e:
        logging.exception("Ошибка обработки изображения")
        await update.message.reply_text(f"Ошибка при обработке изображения: {e}")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Действие отменено.")
    return ConversationHandler.END

async def fallback_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Используй /find, чтобы отправить изображение на обработку."
    )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logging.exception("Ошибка во время работы бота:", exc_info=context.error)

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("find", find_command)],
        states={
            WAITING_IMAGE: [
                MessageHandler(filters.PHOTO, handle_image),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, fallback_message))
    app.add_error_handler(error_handler)

    app.run_polling()

if __name__ == "__main__":
    main()