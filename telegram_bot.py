import asyncio
from random import randint
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import requests
import json

button1 = InlineKeyboardButton("Кнопка 1", callback_data="button1")
button2 = InlineKeyboardButton("Кнопка 2", callback_data="button2")
button_url = InlineKeyboardButton("Ссылка на Путина", url="https://ru.wikipedia.org/wiki/%D0%92%D0%BB%D0%B0%D0%B4%D0%B8%D0%BC%D0%B8%D1%80_(%D0%B3%D0%BE%D1%80%D0%BE%D0%B4,_%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D1%8F)")

keyboard = InlineKeyboardMarkup([
    [button1, button2],
    [button_url],
    [InlineKeyboardButton("Кнопка 3", callback_data="button3")]
])

#Получаем ключ weather api и ключ telegram бота
with open("config.json", "r") as f:
    config = json.load(f)
    BOT_TOKEN = config["BOT_KEY"]
    WEATHER_API_KEY = config["WEATHER_API_KEY"]

# Функция стартового сообщения
async def start(update: Update, context):
    await update.message.reply_text('Привет! Я тестовый бот. Напиши что-нибудь!', reply_markup=keyboard)

# Эхо-команда
async def echo(update: Update, context):
    word_user = update.message.text
    word_reserve = word_user[::-1]
    await update.message.reply_text(f'Ты написал: {word_reserve}')

# Угадай число
async def guess_number(update: Update, context):
    if not context.args:
        await update.message.reply_text("Укажите число для угадывания")
        return

    if not context.user_data.get("number"):
        context.user_data["number"] = str(randint(1, 10))

    if int(context.args[0]) > int(context.user_data["number"]):
        await update.message.reply_text("Число меньше")
    elif int(context.args[0]) < int(context.user_data["number"]):
        await update.message.reply_text("Число больше")
    else:
        await update.message.reply_text("Поздравляю, вы угадали! Число сброшено.")
        context.user_data["number"] = str(randint(1, 10))

# Таймер
async def settimer(update: Update, context):
    if not context.args:
        await update.message.reply_text("Вы должны ввести команду в формате /settimer <секунды>")
        return

    seconds = int(context.args[0])
    await update.message.reply_text(f"Таймер на {seconds} секунд установлен!")
    await asyncio.sleep(seconds)
    await update.message.reply_text("Таймер сработал!")

# Команда погоды
async def get_weather(update: Update, context):
    if not context.args:
        await update.message.reply_text("Вы должны ввести команду в формате /getWeather <название города>")
        return

    city = context.args[0]
    url = 'http://api.weatherapi.com/v1/current.json'
    aqi = 'yes'
    params = {
        'key': WEATHER_API_KEY,
        'q': city,
        'aqi': aqi
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        message = f"""
        Город: {data['location']['name']},
        Регион: {data['location']['region']},
        Время: {data['location']['localtime']},
        Температура: {data['current']['temp_c']}°C,
        Облачность: {data['current']['cloud']},
        Влажность: {data['current']['humidity']}%,
        Ветер: {data['current']['wind_kph']} км/ч
        """
        await update.message.reply_text(message)
    except Exception as e:
        await update.message.reply_text(f"Ошибка при получении погоды: {e}")

# Главная функция для запуска бота
def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_handler(CommandHandler("guess", guess_number))
    application.add_handler(CommandHandler("settimer", settimer))
    application.add_handler(CommandHandler("getWeather", get_weather))
    print("Бот запущен")
    application.run_polling()

if __name__ == '__main__':
    main()
