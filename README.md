
Нужно настроить переменные окружения. 

```
TG_BOT_TOKEN=your_token
SMTP_SERVER=smtp.yandex.ru
SMTP_PORT=465
EMAIL_ADDRESS=your@yandex.ru
APP_PASSWORD=your_app_password
```


## Установка зависимостей и запуск

1. Установите необходимые зависимости:
   ```
   pip install -r requirements.txt
   ```
2. Запустите приложение:
   ```
   python TelegramBot.py
   ```

## Взаимодействие с ботом

Чтобы начать использовать бота, отправьте команду `/start`. Бот попросит ввести ваш email. Если адрес окажется правильным, он запросит текст сообщения и отправит на указанный email.
