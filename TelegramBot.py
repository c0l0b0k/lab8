from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import re
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

# Загружаем параметры из .env файла
load_dotenv('params.env')

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

# Чтение настроек SMTP
smtp_host = os.getenv("SMTP_SERVER")
smtp_port = os.getenv("SMTP_PORT")
sender_email = os.getenv("EMAIL_ADDRESS")
app_password = os.getenv("APP_PASSWORD")

# Регулярное выражение для проверки корректности email
email_regex = r'^[\w\.-]+@([\w-]+\.)+[\w-]{2,4}$'

# Хранение данных пользователей
user_sessions = {}

def send_email(recipient_email: str, message: str) -> bool:
    """Функция отправки email через SMTP-сервер."""
    logging.info(f'Попытка отправить письмо на адрес: {recipient_email}')

    try:
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            server.login(sender_email, app_password)

            email_message = MIMEMultipart()
            email_message['From'] = sender_email
            email_message['To'] = recipient_email
            email_message['Subject'] = "Сообщение от Telegram-бота"
            email_message.attach(MIMEText(message, 'plain'))

            server.sendmail(sender_email, recipient_email, email_message.as_string())

        logging.info(f'Письмо успешно отправлено на {recipient_email}')
        return True

    except Exception as error:
        logging.error(f'Ошибка при отправке письма: {error}')
        return False

def is_valid_email(email: str) -> bool:
    """Проверка корректности формата email."""
    return re.match(email_regex, email) is not None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для приветствия и начала общения с ботом."""
    user_id = update.effective_user.id
    logging.info(f'Пользователь с ID {user_id} начал разговор с ботом')
    user_sessions[user_id] = {'email': None, 'message': None}
    await update.message.reply_text("Введите ваш email.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений от пользователя."""
    user_id = update.effective_user.id
    message_text = update.message.text

    if user_id not in user_sessions:
        await update.message.reply_text("Используйте команду /start.")
        return

    if user_sessions[user_id]['email'] is None:
        await handle_email(update, user_id, message_text)
    elif user_sessions[user_id]['message'] is None:
        await handle_message_input(update, user_id, message_text)

async def handle_email(update: Update, user_id: int, email_input: str):
    """Обработка ввода email-адреса пользователем."""
    logging.info(f'Пользователь с ID {user_id} вводит email: {email_input}')

    if is_valid_email(email_input):
        user_sessions[user_id]['email'] = email_input
        await update.message.reply_text("Email принят! Теперь отправьте ваше сообщение.")
    else:
        await update.message.reply_text("Неверный формат email. Попробуйте снова.")
        logging.warning(f'Некорректный email: "{email_input}" для пользователя с ID {user_id}')

async def handle_message_input(update: Update, user_id: int, message_input: str):
    """Обработка сообщения пользователя."""
    user_sessions[user_id]['message'] = message_input
    user_email = user_sessions[user_id]['email']

    if send_email(user_email, message_input):
        await update.message.reply_text("Сообщение отправлено")
    else:
        await update.message.reply_text("Не удалось отправить сообщение. Повторите попытку.")

    # Очистка сессии пользователя
    del user_sessions[user_id]

def run_bot(bot_token: str):
    """Запуск работы Telegram-бота."""
    app = Application.builder().token(bot_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logging.info("Бот запущен и готов к использованию...")
    app.run_polling()

# Запуск бота
run_bot(os.getenv("TG_BOT_TOKEN"))
