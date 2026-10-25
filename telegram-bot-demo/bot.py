"""Telegram booking-intake bot (Demo project / sample build).

Usage:
    export TELEGRAM_BOT_TOKEN=123456:ABC...   # from @BotFather
    export ADMIN_CHAT_ID=123456789            # optional: notified of each new booking
    export BOOKINGS_CSV=bookings.csv          # optional
    python bot.py
"""
import logging
import os

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from booking_logic import BookingFlow, BookingStore

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("booking-bot")

flow = BookingFlow(BookingStore(os.environ.get("BOOKINGS_CSV", "bookings.csv")))
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID")


def keyboard(options):
    if not options:
        return ReplyKeyboardRemove()
    rows = [options[i:i + 3] for i in range(0, len(options), 3)]
    return ReplyKeyboardMarkup(rows, one_time_keyboard=True, resize_keyboard=True)


async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! I'm a demo booking bot for a fictional barber shop.\n/book to make a booking, /cancel to stop.")


async def book(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    reply, opts = flow.start(update.effective_chat.id)
    await update.message.reply_text(reply, reply_markup=keyboard(opts))


async def cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    reply, opts = flow.cancel(update.effective_chat.id)
    await update.message.reply_text(reply, reply_markup=keyboard(opts))


async def on_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    reply, opts = flow.handle(chat_id, update.message.text)
    await update.message.reply_text(reply, reply_markup=keyboard(opts))
    if reply.startswith("Booked!") and ADMIN_CHAT_ID:
        last = flow.store.all()[-1]
        await ctx.bot.send_message(int(ADMIN_CHAT_ID), "New booking:\n" + "\n".join(f"{k}: {v}" for k, v in last.items()))


def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise SystemExit("Set TELEGRAM_BOT_TOKEN (see README). To try the logic without a token: python simulate.py")
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("book", book))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text))
    log.info("Bot running (long polling). Ctrl+C to stop.")
    app.run_polling()


if __name__ == "__main__":
    main()
