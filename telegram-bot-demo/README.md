# Telegram booking-intake bot (Demo project)

**Demo project / sample build** for a fictional barber shop. This is not client work.

A Telegram bot that walks customers through a booking: service, date, free time slot, name, phone, confirm.
It validates every answer, blocks Sundays, past dates and double-bookings, saves bookings to CSV, and can
notify the owner's Telegram chat on each new booking.

## Files
- `booking_logic.py`: conversation state machine and CSV store. Pure Python, testable.
- `bot.py`: python-telegram-bot v21+/v22 wiring (long polling, reply-keyboard buttons).
- `simulate.py`: run the conversation in a terminal **without a token**.
- `tests/`: pytest unit tests.

## Try it without Telegram
```bash
pip install -r requirements.txt
python simulate.py        # scripted demo
python simulate.py -i     # type messages yourself
pytest -q
```

## Run for real
1. Create a bot with @BotFather and copy the token.
2. `export TELEGRAM_BOT_TOKEN=...` (optionally `ADMIN_CHAT_ID`, `BOOKINGS_CSV`; see `.env.example`).
3. `python bot.py`, then message your bot `/book`.

For a client build, the CSV could be swapped for Google Sheets, Airtable, or a database, with reminders, payments, or a web admin added.
