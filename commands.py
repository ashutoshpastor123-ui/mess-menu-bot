
from telegram import Update
from telegram.ext import ContextTypes

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from excel_reader import get_day_menu

IST = ZoneInfo("Asia/Kolkata")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to boku ji ke rasoi!\n\n"
        "Available Commands:\n\n"
        "/today\n"
        "/tomorrow\n"
        "/week\n"
    )


async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):

    day = datetime.now(IST).strftime("%A")

    menu = get_day_menu(day)

    if not menu:
        await update.message.reply_text(
            f"Sorry! Menu for {day} is not available."
        )
        return

    message = f"🍽 <b>{day.upper()} MENU</b>\n\n"

    for meal, item in menu.items():
        message += f"🤤 <b>{meal}</b>\n\n{item or 'Not available'}\n\n"

    await update.message.reply_text(
        message,
        parse_mode="HTML"
    )


async def tomorrow(update: Update, context: ContextTypes.DEFAULT_TYPE):

    tomorrow_day = (
        datetime.now(IST) + timedelta(days=1)
    ).strftime("%A")

    menu = get_day_menu(tomorrow_day)

    if not menu:
        await update.message.reply_text(
            f"Sorry! Menu for {tomorrow_day} is not available."
        )
        return

    message = f"🍽 <b>{tomorrow_day.upper()} MENU</b>\n\n"

    for meal, item in menu.items():
        message += f"🤤 <b>{meal}</b>\n\n{item or 'Not available'}\n\n"

    await update.message.reply_text(
        message,
        parse_mode="HTML"
    )


async def week(update: Update, context: ContextTypes.DEFAULT_TYPE):

    days = [
        "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"
    ]

    message = "🍽 <b>WEEKLY MESS MENU</b>\n\n"

    for day in days:

        # Excel is read when /week is requested
        menu = get_day_menu(day)

        message += f"📍 <b>{day.upper()}</b>\n\n"

        if not menu:
            message += "Menu not available.\n\n"
            continue

        for meal, item in menu.items():
            message += f"🤤 <b>{meal}</b>\n{item or 'Not available'}\n\n"

        message += "\n"

    await update.message.reply_text(
        message,
        parse_mode="HTML"
    )
