from database.db import db
from modules.casino.data.models import JACKPOT_BASE


def get_slot_jackpot(slot_id) -> int:
	multiplier = int(slot_id.replace('7', ''))
	return int(db.get(slot_id)) if db.exists(slot_id) and not int(db.get(slot_id)) == 0 else JACKPOT_BASE * multiplier


def update_slot_jackpot(slot_id, adjustment: int):
	db.incr(slot_id, amount=adjustment)

