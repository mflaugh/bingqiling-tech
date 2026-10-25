"""Run the booking conversation in the terminal without Telegram or a token.

    python simulate.py            # scripted demo conversation
    python simulate.py -i         # interactive: type messages yourself
"""
import sys
import tempfile
from datetime import date
from pathlib import Path

from booking_logic import BookingFlow, BookingStore

CHAT = 1001


def show(reply, opts):
    print(f"BOT : {reply}")
    if opts:
        print(f"      [buttons: {' | '.join(opts)}]")


def scripted():
    store = BookingStore(Path(tempfile.mkdtemp()) / "bookings.csv")
    flow = BookingFlow(store, today=date(2026, 10, 26))  # fixed Monday for a reproducible demo
    print("=== Demo project: booking bot simulation (no Telegram needed) ===")
    print("USER: /book"); show(*flow.start(CHAT))
    for msg in ["Massage", "Haircut", "next week", "tomorrow", "09:00", "11:00", "J", "Alex Sample",
                "12", "+44 7700 900123", "Yes"]:
        print(f"USER: {msg}"); show(*flow.handle(CHAT, msg))
    print("\nSaved bookings:", store.all())
    print("\nSecond customer tries the same day; 11:00 is no longer offered:")
    show(*flow.start(2002)); flow.handle(2002, "Beard trim"); show(*flow.handle(2002, "tomorrow"))


def interactive():
    flow = BookingFlow(BookingStore("sim_bookings.csv"))
    show(*flow.start(CHAT))
    for line in sys.stdin:
        line = line.strip()
        if line == "/cancel":
            show(*flow.cancel(CHAT))
        elif line == "/book":
            show(*flow.start(CHAT))
        else:
            show(*flow.handle(CHAT, line))


if __name__ == "__main__":
    interactive() if "-i" in sys.argv else scripted()
