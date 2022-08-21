import redis

import env

db = redis.Redis(host=env.REDIS_ENDPOINT, port=6379, db=1)


def get_currency(user_id: int) -> int:
	key = f'{user_id}:currency'
	return int(db.get(key)) if db.exists(key) else 0


def update_currency(user_id: int, adjustment: int):
	key = f'{user_id}:currency'
	db.incr(key, amount=adjustment)
