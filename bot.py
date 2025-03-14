#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import os
import requests
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def process_api_call(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Brightdata balance
    """
    url = os.getenv("LANGFLOW_API_URL")
    headers = {
        "Content-Type": "application/json",
        "x-api-key": os.getenv("LANGFLOW_API_KEY")
    }
    data = {
        "input_value": f"{update.message.text}",
        "output_type": "chat",
        "input_type": "chat",
        "tweaks": {
            "YouTubeTranscripts-4yjq0": {},
            "ChatOutput-DsMLq": {},
            "ChatInput-dTjJK": {},
            "AnthropicModel-gtPYu": {}
        }
    }

    response = requests.post(url, headers=headers, json=data)
    await update.message.reply_text(
        response.json()['outputs'][0]['outputs'][0]['results']['message']['data']['text'],
    )


if __name__ == "__main__":
    load_dotenv()
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    is_production = os.environ.get("IS_PRODUCTION", "0") == "1"

    application = Application.builder().token(token).build()
    application.add_handler(MessageHandler(filters.TEXT, process_api_call))

    if is_production:
        # Production: use webhook
        webhook_url = os.environ.get("WEBHOOK_URL")
        port = int(os.environ.get("PORT", 8443))

        # Set webhook
        application.bot.set_webhook(
            url=f"{webhook_url}/{token}",
            drop_pending_updates=True
        )

        application.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=token,
            webhook_url=f"{webhook_url}/{token}"
        )
    else:
        # Development: use polling
        application.run_polling()
