import redis

import env

db = redis.Redis(host=env.REDIS_ENDPOINT)