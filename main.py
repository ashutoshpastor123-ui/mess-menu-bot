import os
import logging

from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler

import reminder
from commands import start, today, tomorrow, week

logging.basicConfig(level=logging.INFO)

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

async def post_init(application):
    reminder.start_scheduler()
    print("✅ Reminder Scheduler Started")

app = (
    Application.builder()
    .token(TOKEN)
    .post_init(post_init)
    .build()
)

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("today", today))
app.add_handler(CommandHandler("tomorrow", tomorrow))
app.add_handler(CommandHandler("week", week))


app.run_polling()