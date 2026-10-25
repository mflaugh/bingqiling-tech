import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from booking_logic import BookingFlow, BookingStore, SLOTS  # noqa: E402

MONDAY = date(2026, 10, 26)


def make(tmp_path):
    return BookingFlow(BookingStore(tmp_path / "b.csv"), today=MONDAY)


def run(flow, chat, msgs):
    out = None
    for m in msgs:
        out = flow.handle(chat, m)
    return out


def test_happy_path_saves_booking(tmp_path):
    f = make(tmp_path); f.start(1)
    reply, _ = run(f, 1, ["Haircut", "tomorrow", "10:00", "Alex", "+1 555 010 0000", "yes"])
    assert reply.startswith("Booked!")
    rows = f.store.all()
    assert len(rows) == 1 and rows[0]["date"] == "2026-10-27" and rows[0]["time"] == "10:00"


def test_invalid_inputs_are_rejected(tmp_path):
    f = make(tmp_path); f.start(1)
    assert "choose one" in f.handle(1, "Massage")[0]
    f.handle(1, "Haircut")
    assert "couldn't read" in f.handle(1, "someday")[0]
    assert "between today" in f.handle(1, "2020-01-01")[0]
    assert "closed on Sundays" in f.handle(1, "2026-11-01")[0]
    f.handle(1, "tomorrow")
    assert "isn't available" in f.handle(1, "09:00")[0]
    f.handle(1, "10:00"); f.handle(1, "Alex")
    assert "valid phone" in f.handle(1, "abc")[0]


def test_no_double_booking(tmp_path):
    f = make(tmp_path)
    f.start(1); run(f, 1, ["Haircut", "tomorrow", "10:00", "Alex", "+15550100000", "yes"])
    f.start(2); f.handle(2, "Beard trim")
    _, slots = f.handle(2, "tomorrow")
    assert "10:00" not in slots and len(slots) == len(SLOTS) - 1


def test_cancel_and_no_session(tmp_path):
    f = make(tmp_path); f.start(1); f.handle(1, "Haircut")
    assert "cancelled" in f.cancel(1)[0]
    assert "/book" in f.handle(1, "hello")[0]


def test_bot_module_imports():
    import bot  # noqa: F401  (python-telegram-bot wiring loads without a token)


def test_application_builds_with_dummy_token():
    from telegram.ext import Application, CommandHandler
    import bot
    app = Application.builder().token("123456:TEST-DUMMY-TOKEN").build()  # no network call on build
    app.add_handler(CommandHandler("book", bot.book))
    assert app.handlers
