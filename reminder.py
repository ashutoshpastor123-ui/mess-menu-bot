from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Bot
from telegram.error import TelegramError
from dotenv import load_dotenv
from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException

import os
from datetime import datetime, timedelta
import asyncio
import logging

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Validate environment variables
if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("BOT_TOKEN and CHAT_ID must be set in .env file")

bot = Bot(BOT_TOKEN)

DAY_COLUMNS = {
    "Monday": 3,
    "Tuesday": 4,
    "Wednesday": 5,
    "Thursday": 6,
    "Friday": 7,
    "Saturday": 8,
    "Sunday": 9
}

scheduler = BackgroundScheduler()

# Use dict to track sent messages with timestamp for cleanup
sent = {}
REMINDER_VALIDITY_HOURS = 24


async def send_message(msg):
    """Send message to Telegram chat with error handling"""
    try:
        await bot.send_message(chat_id=CHAT_ID, text=msg)
        logger.info("Message sent successfully")
    except TelegramError as e:
        logger.error(f"Failed to send Telegram message: {e}")
    except Exception as e:
        logger.error(f"Unexpected error sending message: {e}")


def cleanup_sent_messages():
    """Remove old entries from sent messages to prevent memory leak"""
    current_time = datetime.now()
    expired_keys = [
        key for key, timestamp in sent.items()
        if (current_time - timestamp).total_seconds() > REMINDER_VALIDITY_HOURS * 3600
    ]
    for key in expired_keys:
        del sent[key]
    if expired_keys:
        logger.info(f"Cleaned up {len(expired_keys)} expired reminders")


def check_menu():
    """Check menu and send reminder if it's time"""
    try:
        # Check if file exists
        if not os.path.exists("menu.xlsx"):
            logger.error("menu.xlsx file not found")
            return

        workbook = load_workbook("menu.xlsx")
        sheet = workbook.active

        today = datetime.now().strftime("%A")
        column = DAY_COLUMNS.get(today)

        if column is None:
            logger.error(f"Invalid day: {today}")
            return

        current = datetime.now().strftime("%H:%M")

        for row in sheet.iter_rows(min_row=2):
            meal = row[0].value

            if meal is None:
                continue

            try:
                menu = row[column - 1].value

                if menu is None:
                    continue

                meal = str(meal).strip()

                # Parse meal time - Example: "BREAKFAST 08:00 AM TO 08:50 AM"
                parts = meal.split()
                if len(parts) < 3:
                    logger.warning(f"Unexpected meal format: {meal}")
                    continue

                start = parts[1] + " " + parts[2]
                meal_name = parts[0].title()

                meal_time = datetime.strptime(start, "%I:%M %p")

                reminder_time = (meal_time - timedelta(minutes=10)).strftime("%H:%M")

                key = today + meal_name

                # Check if reminder should be sent and hasn't been sent yet
                if current == reminder_time and key not in sent:
                    message = f"""
🔔 {meal_name} starts in 10 minutes!

🍽 Menu

{menu}

🕒 {start}
"""
                    # Use asyncio to run the async function
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(send_message(message))
                    loop.close()

                    sent[key] = datetime.now()
                    logger.info(f"Reminder sent for {meal_name}")

            except ValueError as e:
                logger.warning(f"Error parsing meal row: {e}")
                continue
            except Exception as e:
                logger.error(f"Unexpected error processing meal: {e}")
                continue

        workbook.close()

    except InvalidFileException:
        logger.error("menu.xlsx is not a valid Excel file")
    except Exception as e:
        logger.error(f"Error in check_menu: {e}")


def start_scheduler():
    """Start the background scheduler"""
    if not scheduler.running:
        # Add the main job to check menu every minute
        scheduler.add_job(check_menu, "interval", minutes=1, id="check_menu")
        
        # Add cleanup job to run every hour
        scheduler.add_job(cleanup_sent_messages, "interval", hours=1, id="cleanup_messages")
        
        scheduler.start()
        logger.info("🤖 Scheduler started")


def stop_scheduler():
    """Stop the background scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("🤖 Scheduler stopped")