from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from excel_reader import get_day_menu


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 welcome to boku's kitchen \n\n"
        "Available Commands:\n\n"
        "/today\n\n"
        "/tomorrow\n\n"
        "/week"
    )


async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):

    day = datetime.now().strftime("%A")
    menu = get_day_menu(day)

    message = f"🍽 {day} Menu\n\n"

    for meal, item in menu.items():
        message += f"🍴 {meal}\n{item}\n\n"

    await update.message.reply_text(message)


async def tomorrow(update: Update, context: ContextTypes.DEFAULT_TYPE):

    tomorrow_day = (datetime.now() + timedelta(days=1)).strftime("%A")

    menu = get_day_menu(tomorrow_day)

    message = f"🍽 {tomorrow_day} Menu\n\n"

    for meal, item in menu.items():
        message += f"🍴 {meal}\n{item}\n\n"

    await update.message.reply_text(message)
async def week(update: Update, context: ContextTypes.DEFAULT_TYPE):

    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ]

    message = "📅 Weekly Mess Menu\n\n"

    for day in days:

        menu = get_day_menu(day)

        message += f"📍 {day}\n"

        for meal, item in menu.items():
            message += f"🍴 {meal}: {item}\n"

        message += "\n"

    await update.message.reply_text(message)