import redis

import env

db = redis.Redis(host=env.REDIS_ENDPOINT, port=6379, db=1)


def get_currency(user_id: int, test: bool = False) -> int:
	key = f'{user_id}:currency{":test" if test else ""}'
	return int(db.get(key)) if db.exists(key) else 0


def update_currency(user_id: int, adjustment: int, test: bool = False):
	key = f'{user_id}:currency{":test" if test else ""}'
	db.incr(key, amount=adjustment)
