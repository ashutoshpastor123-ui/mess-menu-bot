
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Bot
from telegram.error import TelegramError
from dotenv import load_dotenv
from openpyxl import load_workbook

import os
import asyncio
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("BOT_TOKEN and CHAT_ID must be set")

# Telegram bot
bot = Bot(BOT_TOKEN)

# Indian timezone
IST = ZoneInfo("Asia/Kolkata")

# Scheduler
scheduler = BackgroundScheduler(timezone=IST)


def get_menu_for_day(day_name):
    """Open Excel only when menu is requested."""

    workbook = None

    try:
        workbook = load_workbook(
            "menu.xlsx",
            read_only=True,
            data_only=True
        )

        sheet = workbook.active

        for row in sheet.iter_rows(min_row=3, values_only=True):

            day = row[0]

            if not day:
                continue

            if str(day).strip().lower() == day_name.lower():

                return {
                    "BREAKFAST": row[1],
                    "LUNCH": row[2],
                    "SNACKS": row[3],
                    "DINNER": row[4]
                }

        logger.warning("Menu not found for %s", day_name)
        return None

    except Exception as e:
        logger.exception("Failed to read Excel: %s", e)
        return None

    finally:
        if workbook:
            workbook.close()


async def send_reminder(meal):

    try:
        today = datetime.now(IST).strftime("%A")

        # Read Excel only when reminder is due
        menu_data = get_menu_for_day(today)

        if not menu_data:
            return

        menu = menu_data.get(meal)

        if not menu:
            logger.warning("No %s menu for %s", meal, today)
            return

        await bot.send_message(
            chat_id=CHAT_ID,
            text=f"""🔔 {meal.title()} starts in 10 minutes!

🍽 Today's Menu

{menu}
"""
        )

        logger.info("%s reminder sent successfully", meal)

    except TelegramError as e:
        logger.error("Telegram error: %s", e)

    except Exception as e:
        logger.exception("Unexpected error: %s", e)


def breakfast():
    asyncio.run(send_reminder("BREAKFAST"))


def lunch():
    asyncio.run(send_reminder("LUNCH"))


def snacks():
    asyncio.run(send_reminder("SNACKS"))


def dinner():
    asyncio.run(send_reminder("DINNER"))


def start_scheduler():

    if scheduler.running:
        logger.warning("Scheduler is already running")
        return

    # No Excel reading during startup

    scheduler.add_job(
        breakfast,
        "cron",
        hour=7,
        minute=50,
        id="breakfast",
        replace_existing=True
    )

    scheduler.add_job(
        lunch,
        "cron",
        hour=12,
        minute=20,
        id="lunch",
        replace_existing=True
    )

    scheduler.add_job(
        snacks,
        "cron",
        hour=16,
        minute=20,
        id="snacks",
        replace_existing=True
    )

    scheduler.add_job(
        dinner,
        "cron",
        hour=20,
        minute=5,
        id="dinner",
        replace_existing=True
    )

    scheduler.start()

    logger.info("Telegram reminder scheduler started (IST)")


def stop_scheduler():

    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
