
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Bot
from telegram.error import TelegramError
from dotenv import load_dotenv

from excel_reader import get_day_menu

import os
import asyncio
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("BOT_TOKEN and CHAT_ID must be set")

bot = Bot(BOT_TOKEN)

IST = ZoneInfo("Asia/Kolkata")

scheduler = BackgroundScheduler(timezone=IST)


async def send_reminder(meal):
    try:
        today = datetime.now(IST).strftime("%A")

        # Excel opens only when reminder is due
        menu_data = get_day_menu(today)

        if not menu_data:
            logger.warning("Menu unavailable for %s", today)
            return

        menu = menu_data.get(meal.title())

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

    except Exception:
        logger.exception("Unexpected reminder error")


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
        logger.warning("Scheduler already running")
        return

    scheduler.add_job(
        breakfast, "cron",
        hour=7, minute=50,
        id="breakfast",
        replace_existing=True
    )

    scheduler.add_job(
        lunch, "cron",
        hour=12, minute=20,
        id="lunch",
        replace_existing=True
    )

    scheduler.add_job(
        snacks, "cron",
        hour=16, minute=20,
        id="snacks",
        replace_existing=True
    )

    scheduler.add_job(
        dinner, "cron",
        hour=20, minute=5,
        id="dinner",
        replace_existing=True
    )

    scheduler.start()

    logger.info("Reminder scheduler started (IST)")


def stop_scheduler():

    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
