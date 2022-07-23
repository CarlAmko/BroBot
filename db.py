import redis

import env

db = redis.Redis(host=env.REDIS_ENDPOINT, port=6379, db=1)
