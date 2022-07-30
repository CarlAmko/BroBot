import redis

import env

_db = redis.Redis(host=env.REDIS_ENDPOINT, port=6379, db=1)


def get_currency(user_id: int) -> int:
	key = f'{user_id}:currency'
	return int(_db.get(key)) if _db.exists(key) else 0


def set_currency(user_id: int, new_value: int):
	key = f'{user_id}:currency'
	_db.set(key, new_value)


def update_current_currency(user_id: int, adjustment: int):
	set_currency(user_id, get_currency(user_id) + adjustment)
