import requests
import json
import logging
from telegram import Bot, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram.error import TelegramError

''' Example https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/pollbot.py'''
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



BOT_TOKEN = "insert your bot token"
CHANNEL_ID = "insert your channel id"

bot = Bot(token=BOT_TOKEN)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Inform the user about what this bot can do."""
    await update.message.reply_text(
        "Welcome to the 'Would You Rather' Poll Bot!\n\n"
        "Available commands:\n"
        "/sendpoll - Create and send a poll to the channel.\n"
        "/help - Display this information page."
    )

async def sendpoll(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /sendpoll command and collect poll data."""
    user = update.effective_user
    chat_id = update.effective_chat.id

    if not context.args:
        await update.message.reply_text(
            "To create a poll, send the command followed by the question in quotes.\n"
            "Example: /sendpoll 'Would you rather eat pizza or burgers?'"
        )
        return

    question = " ".join(context.args).strip("'\"")
    context.user_data['question'] = question

    await update.message.reply_text(
        f"Poll Question: {question}\n\n"
        "Now send the two options as a reply, separated by a comma.\n"
        "Example: Pizza, Burgers"
    )
    

async def handle_options(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the user input containing the options."""
    if 'question' not in context.user_data:
        await update.message.reply_text(
            "First, send a poll question using /sendpoll."
        )
        return

    options = update.message.text.split(",")
    if len(options) != 2:
        await update.message.reply_text(
            "Please provide exactly two options separated by a comma. Try again."
        )
        return

    option1, option2 = options[0].strip(), options[1].strip()
    question = context.user_data['question'] 
    try:
        parameters = {
            "chat_id": CHANNEL_ID,
            "question": {question},
            "options": json.dumps([option1, option2])
        }

        resp = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPoll", data=parameters)
        
        if resp.status_code == 200:
            await update.message.reply_text("Poll successfully sent to the channel!")
            logger.info("Poll successfully uploaded!")
        else:
            raise Exception(f"Failed to send poll. Response: {resp.text}")
        
    except TelegramError as e:
        await update.message.reply_text(
            f"Error uploading poll: {e.message}. Please try again."
        )
        logger.error(f"Error uploading poll: {e}")

    del context.user_data['question']


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display the help message with available commands."""
    await update.message.reply_text(
        "This bot helps you create and send 'Would You Rather' polls.\n\n"
        "Commands:\n"
        "/start - Show the welcome message.\n"
        "/sendpoll - Create and send a poll to the channel.\n"
        "/help - Display this help message."
    )

def main() -> None:
    """Run the bot."""
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("sendpoll", sendpoll))
    application.add_handler(CommandHandler("help", help_handler))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_options))

    application.run_polling()

if __name__ == "__main__":
    main()
