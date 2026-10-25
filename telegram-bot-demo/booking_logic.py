"""Booking-intake conversation logic (Demo project / sample build).

Pure Python, with no Telegram dependency, so it can be unit-tested and
simulated from the CLI without a bot token. bot.py wires it to Telegram.
"""
from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field, asdict
from datetime import date, datetime, timedelta
from pathlib import Path

SERVICES = ["Haircut", "Beard trim", "Haircut + Beard"]  # sample services for a fictional barber shop
SLOTS = ["10:00", "11:00", "13:00", "14:00", "15:00", "16:00"]
STEPS = ["service", "date", "time", "name", "phone", "confirm"]


@dataclass
class Booking:
    service: str = ""
    date: str = ""
    time: str = ""
    name: str = ""
    phone: str = ""


@dataclass
class Session:
    step: str = "service"
    booking: Booking = field(default_factory=Booking)


class BookingStore:
    """Appends confirmed bookings to a CSV file and prevents double-booking."""

    FIELDS = ["created_at", "chat_id", "service", "date", "time", "name", "phone"]

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def all(self) -> list[dict]:
        if not self.path.exists():
            return []
        with self.path.open(newline="") as f:
            return list(csv.DictReader(f))

    def is_taken(self, day: str, slot: str) -> bool:
        return any(r["date"] == day and r["time"] == slot for r in self.all())

    def add(self, chat_id: int, b: Booking) -> None:
        new = not self.path.exists()
        with self.path.open("a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=self.FIELDS)
            if new:
                w.writeheader()
            w.writerow({"created_at": datetime.now().isoformat(timespec="seconds"), "chat_id": chat_id, **asdict(b)})


def parse_date(text: str, today: date) -> date | None:
    t = text.strip().lower()
    if t == "today":
        return today
    if t == "tomorrow":
        return today + timedelta(days=1)
    try:
        return datetime.strptime(t, "%Y-%m-%d").date()
    except ValueError:
        return None


PHONE_RE = re.compile(r"^\+?[0-9][0-9 \-]{6,18}$")


class BookingFlow:
    """Each handle() call takes a user message and returns (reply, options)."""

    def __init__(self, store: BookingStore, today: date | None = None):
        self.store = store
        self.today = today
        self.sessions: dict[int, Session] = {}

    def _today(self) -> date:
        return self.today or date.today()

    def start(self, chat_id: int) -> tuple[str, list[str]]:
        self.sessions[chat_id] = Session()
        return ("Welcome to Sample Barber (demo bot)! Which service would you like?", SERVICES)

    def cancel(self, chat_id: int) -> tuple[str, list[str]]:
        self.sessions.pop(chat_id, None)
        return ("Booking cancelled. Send /book to start again.", [])

    def free_slots(self, day: str) -> list[str]:
        return [s for s in SLOTS if not self.store.is_taken(day, s)]

    def handle(self, chat_id: int, text: str) -> tuple[str, list[str]]:
        s = self.sessions.get(chat_id)
        if s is None:
            return ("Send /book to make a booking.", [])
        text = text.strip()
        b = s.booking

        if s.step == "service":
            match = next((x for x in SERVICES if x.lower() == text.lower()), None)
            if not match:
                return ("Please choose one of the services below.", SERVICES)
            b.service, s.step = match, "date"
            return ("Which date? Type YYYY-MM-DD, 'today' or 'tomorrow'.", ["today", "tomorrow"])

        if s.step == "date":
            d = parse_date(text, self._today())
            if d is None:
                return ("Sorry, I couldn't read that date. Use YYYY-MM-DD, 'today' or 'tomorrow'.", ["today", "tomorrow"])
            if d < self._today() or d > self._today() + timedelta(days=30):
                return ("Please choose a date between today and 30 days from now.", ["today", "tomorrow"])
            if d.weekday() == 6:
                return ("We're closed on Sundays. Please pick another date.", ["tomorrow"])
            slots = self.free_slots(d.isoformat())
            if not slots:
                return ("That day is fully booked. Please pick another date.", ["tomorrow"])
            b.date, s.step = d.isoformat(), "time"
            return (f"Available times on {b.date}:", slots)

        if s.step == "time":
            if text not in self.free_slots(b.date):
                return ("That time isn't available. Please choose one of these:", self.free_slots(b.date))
            b.time, s.step = text, "name"
            return ("What's your name?", [])

        if s.step == "name":
            if len(text) < 2:
                return ("Please enter your name.", [])
            b.name, s.step = text[:60], "phone"
            return ("And a phone number we can reach you on?", [])

        if s.step == "phone":
            if not PHONE_RE.match(text):
                return ("That doesn't look like a valid phone number. Try again, e.g. +44 7700 900123.", [])
            b.phone, s.step = text, "confirm"
            return (self.summary(b) + "\n\nConfirm this booking?", ["Yes", "No"])

        if s.step == "confirm":
            if text.lower() in ("yes", "y"):
                if self.store.is_taken(b.date, b.time):  # race: slot taken meanwhile
                    s.step = "time"
                    return ("Sorry, that slot was just taken. Pick another time:", self.free_slots(b.date))
                self.store.add(chat_id, b)
                self.sessions.pop(chat_id, None)
                return (f"Booked! See you on {b.date} at {b.time}. (Demo: saved to CSV.)", [])
            if text.lower() in ("no", "n"):
                return self.cancel(chat_id)
            return ("Please answer Yes or No.", ["Yes", "No"])

        return ("Something went wrong. Send /book to restart.", [])

    @staticmethod
    def summary(b: Booking) -> str:
        return f"Service: {b.service}\nDate: {b.date}\nTime: {b.time}\nName: {b.name}\nPhone: {b.phone}"
