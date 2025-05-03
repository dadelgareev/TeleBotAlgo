import asyncio
from io import BytesIO
from random import randint, choice

from PIL import ImageFont, ImageDraw, Image
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import requests
import json

# Получаем ключ weather api и ключ telegram бота
with open("config.json", "r") as f:
    config = json.load(f)
    BOT_TOKEN = config["BOT_KEY"]
    WEATHER_API_KEY = config["WEATHER_API_KEY"]

# Создаем объекты кнопок
button1 = InlineKeyboardButton(text="Нажми меня!", callback_data="button1")
button2 = InlineKeyboardButton(text="Другая кнопка", callback_data="button2")

keyboard = [
    [button1, button2],  # Первый ряд с двумя кнопками
    [InlineKeyboardButton(text="Ещё одна", callback_data="button3")]  # Второй ряд с одной кнопкой
]
reply_markup = InlineKeyboardMarkup(keyboard)

# Объекты для игры в камень ножницы бумага
rps_keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton("✊ Камень", callback_data="rps_rock"),
        InlineKeyboardButton("✋ Бумага", callback_data="rps_paper"),
        InlineKeyboardButton("✌️ Ножницы", callback_data="rps_scissors")
    ]
])


# Функция стартового сообщения
async def start(update: Update, context):
    await update.message.reply_text('Привет! Я тестовый бот. Напиши что-нибудь!', reply_markup=reply_markup) # Добавили параметр reply_markup

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

async def rps_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Выбери: камень, ножницы или бумага", reply_markup=rps_keyboard)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Подтверждаем получение callback

    if query.data.startswith("rps_"):
        user_choice = query.data.replace("rps_", "")
        bot_choice = choice(["rock", "paper", "scissors"])

        beats = {
            "rock": "scissors",
            "scissors": "paper",
            "paper": "rock"
        }

        result = ""
        if user_choice == bot_choice:
            result = "Ничья!"
        elif beats[user_choice] == bot_choice:
            result = "Ты победил!"
        else:
            result = "Бот победил!"

        await query.message.reply_text(
            f"Ты выбрал: {user_choice}\nБот выбрал: {bot_choice}\n\n{result}"
        )

    if query.data == "button1":
        await query.message.reply_text("Вы нажали первую кнопку!")
    elif query.data == "button2":
        await query.message.reply_text("Вы нажали вторую кнопку!")
    elif query.data == "button3":
        await query.message.reply_text("Вы нажали третью кнопку!")


async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Использование: /generate_image <размер> <текст>")
        return

    try:
        size = int(context.args[0])
        text = " ".join(context.args[1:])

        image = Image.new('RGB', (size, size), color=(173, 216, 230))  # Голубой фон
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype("arial.ttf", size // 10)
        except:
            font = ImageFont.load_default()
        """ центрирование
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((size - text_width) // 2, (size - text_height) // 2)
        """
        draw.text((0,0), text, fill="black", font=font)

        buffer = BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)

        await update.message.reply_photo(photo=buffer, caption="Вот ваше изображение!")

    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")


# Главная функция для запуска бота
def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_handler(CommandHandler("guess", guess_number))
    application.add_handler(CommandHandler("settimer", settimer))
    application.add_handler(CommandHandler("getWeather", get_weather))
    application.add_handler(CommandHandler("rps_game", rps_game))
    application.add_handler(CommandHandler("generate_image", generate_image))
    application.add_handler(CallbackQueryHandler(button_callback))
    print("Бот запущен")
    application.run_polling()

if __name__ == '__main__':
    main()
