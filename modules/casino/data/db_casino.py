from database.db import db


SMALL_SLOT_KEY = 777001
MEDIUM_SLOT_KEY = 777025
LARGE_SLOT_KEY = 777100


def get_slot_jackpot(slot_size: str) -> int:
	if slot_size == "small":
		return int(db.get(SMALL_SLOT_KEY)) if db.exists(SMALL_SLOT_KEY) else 2000
	elif slot_size == "medium":
		return int(db.get(MEDIUM_SLOT_KEY)) if db.exists(MEDIUM_SLOT_KEY) else (2000 * 25)
	elif slot_size == "large":
		return int(db.get(LARGE_SLOT_KEY)) if db.exists(LARGE_SLOT_KEY) else (2000 * 100)
	else:
		return 0


def update_slot_jackpot(slot_size: str, adjustment: int):
	if slot_size == "small":
		db.incr(SMALL_SLOT_KEY, amount=adjustment)
	elif slot_size == "medium":
		db.incr(MEDIUM_SLOT_KEY, amount=adjustment)
	elif slot_size == "large":
		db.incr(LARGE_SLOT_KEY, amount=adjustment)
	else:
		return
