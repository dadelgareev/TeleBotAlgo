import asyncio
import json
import random
import uuid
from random import randint

import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, CallbackContext

from PIL import Image, ImageDraw

button1 = InlineKeyboardButton("Кнопка 1", callback_data="button1")
button2 = InlineKeyboardButton("Кнопка 2", callback_data="button2")
button_url = InlineKeyboardButton("Ссылка на Путина", url="https://ru.wikipedia.org/wiki/%D0%92%D0%BB%D0%B0%D0%B4%D0%B8%D0%BC%D0%B8%D1%80_(%D0%B3%D0%BE%D1%80%D0%BE%D0%B4,_%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D1%8F)", callback_data="putin")

keyboard = InlineKeyboardMarkup([
    [button1, button2],
    [button_url],
    [InlineKeyboardButton("Кнопка 3", callback_data="button3")]
])

rock_button = InlineKeyboardButton("🗿", callback_data="button_rock")
paper_button = InlineKeyboardButton("📜", callback_data="button_paper")
scissor_button = InlineKeyboardButton("✂️", callback_data="button_scissor")

rps_keyboard = InlineKeyboardMarkup([
    [rock_button, paper_button],
    [scissor_button]
])
#Получаем ключ weather api и ключ telegram бота
with open("config.json", "r") as f:
    config = json.load(f)
    BOT_TOKEN = config["BOT_KEY"]
    WEATHER_API_KEY = config["WEATHER_API_KEY"]
    RUNWARE_API_KEY = config["RUNWARE_API_KEY"]

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

async def play_rpc(update: Update, context):
    await update.message.reply_text("Начинаем игру в цуэ-фа!", reply_markup=rps_keyboard)

async def generate_image(update: Update, context: CallbackContext):
    if not context.args:
        await update.message.reply_text("Вы должны ввести команду в формате /generate_image <цвет>")
        return

    color = context.args[0]

    image = Image.new('RGB', (200, 200), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.ellipse((40, 10, 160, 125), outline=color, width = 5)
    draw.line((0,200,70,115), fill=color, width=5)
    draw.line((200,200,130,115), fill=color, width=5)

    image.save("white_image.jpg")
    await update.message.reply_photo(open("white_image.jpg", "rb"))
    #await update.message.reply_text("Изображение создалили и сохранили!")

URL_AI = 'https://api.runware.ai/v1'

async def generate_image_ai(update: Update, context: CallbackContext):
    if not context.args:
        await update.message.reply_text(f"Пишите команду - /generate_image_ai <текстовый промпт>")
        return
    prompt = ' '.join(context.args)
    #await update.message.reply_text(prompt)

    headers = {'Content-Type': 'application/json',
               'Authorization': f'Bearer {RUNWARE_API_KEY}'}

    task_uuid = str(uuid.uuid4())

    payload = [
        {
            "taskType": "imageInference",
            "taskUUID": task_uuid,
            "positivePrompt": f"{prompt}",
            "width": 512,
            "height": 512,
            "model": "runware:100@1",
            "numberResults": 1,
            "outputFormat": "PNG"
        }
    ]

    image_url = None

    main_response = requests.post(URL_AI, json = payload, headers=headers)

    if "data" in main_response.json():
        data = main_response.json().get('data')[0]
        image_url = data.get('imageURL')
        await update.message.reply_photo(image_url, caption = prompt)
        print(image_url)

    if not image_url:
        await update.message.reply_text("Изображение не получилось скачать!")




async def button_callback(update: Update, context):
    query = update.callback_query
    await query.answer("SOS нажали на кнопку")
    user = query.from_user

    variants = ["paper", "rock", "scissor"]
    bot_choice = random.choice(variants)
    user_choice = query.data[7:len(query.data)]
    #await query.message.reply_text(user_choice)

    win_varinats = {
        "scissor": "paper",
        "rock": "scissor",
        "paper": "rock",
    }
    emoji_varinats = {
        "paper": "📜",
        "rock": "🗿",
        "scissor": "✂️"
    }

    if bot_choice == user_choice:
        await query.message.reply_text(f"Выбор бота-{emoji_varinats.get(bot_choice)},Выбор человека-{emoji_varinats.get(user_choice)}, это определенно ничья!")
    elif win_varinats.get(bot_choice) == user_choice:
        await query.message.reply_text(f"Выбор бота-{emoji_varinats.get(bot_choice)},Выбор человека-{emoji_varinats.get(user_choice)} - победа за ботом!")
        print("Выбор бота", bot_choice)
        print("Выбор человека", user_choice)
    else:
        await query.message.reply_text(f"Выбор бота-{emoji_varinats.get(bot_choice)},Выбор человека-{emoji_varinats.get(user_choice)}, - победа за кожаным!")

    """
    await query.message.reply_text(query.data)
    if query.data == "button1":
        await query.message.reply_text(f"Вы нажали на кнопку одын, {user.first_name}")
    if query.data == "button2":
        await query.message.reply_text(f"Вы нажали на кнопку двыа 📄, {user.first_name}")
    if query.data == "button3":
        await query.message.reply_text(f"Вы нажали на кнопку триада,  {user.first_name}")
    if query.data == "putin":
        await query.message.reply_text(f"{user.first_name} успешно проголосал за Путина!")
    """


# Главная функция для запуска бота
def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_handler(CommandHandler("guess", guess_number))
    application.add_handler(CommandHandler("settimer", settimer))
    application.add_handler(CommandHandler("getWeather", get_weather))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(CommandHandler("play_rpc", play_rpc))
    application.add_handler(CommandHandler("generate_image", generate_image))
    application.add_handler(CommandHandler("generate_image_ai", generate_image_ai))
    print("Бот запущен")
    application.run_polling()

if __name__ == '__main__':
    main()
