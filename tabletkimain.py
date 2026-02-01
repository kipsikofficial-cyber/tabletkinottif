import logging
from datetime import time
from pytz import timezone
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройки
TOKEN = "8436447853:AAH3miX36x2CAKk04qOz4jV9_DTaxV0le5Y"
USER_A_ID = 244904795  # ID пользователя, который будет получать напоминания и отправлять фото
USER_B_ID = 987950927  # ID пользователя, который будет получать фото

# Настройка логгирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Временная зона (Москва)
MOSCOW_TZ = timezone('Europe/Moscow')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Бот запущен! Ожидайте напоминаний.')


async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    # Отправка напоминания пользователю A
    try:
        await context.bot.send_message(chat_id=USER_A_ID, text="⏰ Напоминание: пора выпить таблетки!")
    except Exception as e:
        logger.error(f"Ошибка отправки напоминания: {e}")


async def request_photo(context: ContextTypes.DEFAULT_TYPE):
    # Запрос фото у пользователя A в полночь
    try:
        await context.bot.send_message(chat_id=USER_A_ID, text="📷 Пожалуйста, отправьте фото пустой таблетницы.")
    except Exception as e:
        logger.error(f"Ошибка запроса фото: {e}")


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Обработка фото от пользователя A
    if update.effective_user.id == USER_A_ID:
        photo = update.message.photo[-1]
        # Пересылаем фото пользователю B
        try:
            await context.bot.send_photo(chat_id=USER_B_ID, photo=photo.file_id,
                                         caption="Фото таблетницы от пользователя A")
            await update.message.reply_text("✅ Фото успешно отправлено!")
        except Exception as e:
            await update.message.reply_text("❌ Ошибка отправки фото.")
            logger.error(f"Ошибка пересылки фото: {e}")
    else:
        await update.message.reply_text("⛔ У вас нет прав для отправки фото.")


def main():
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Настройка расписания
    job_queue = application.job_queue

    # Напоминания (13:59, 17:30, 23:30 по Москве)
    job_queue.run_daily(send_reminder, time(hour=13, minute=59, tzinfo=MOSCOW_TZ))
    job_queue.run_daily(send_reminder, time(hour=17, minute=30, tzinfo=MOSCOW_TZ))
    job_queue.run_daily(send_reminder, time(hour=23, minute=30, tzinfo=MOSCOW_TZ))

    # Запрос фото в 00:00 по Москве
    job_queue.run_daily(request_photo, time(hour=0, minute=0, tzinfo=MOSCOW_TZ))

    # Запуск бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()