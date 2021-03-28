import redis
from django.conf import settings


class RedisSett:
    RED_HOST = settings.REDIS_HOST
    RED_PORT = settings.REDIS_PORT
    RED_PASS = settings.REDIS_PASSWORD
    db = None

    @classmethod
    def get_redis_instance(cls, db):
        redis_data = dict(
            host=cls.RED_HOST, port=cls.RED_PORT, password=cls.RED_PASS, db=db
        )
        redis_instance = redis.StrictRedis(**redis_data)
        return redis_instance


# 0, 1 are reserved
redis_pi = RedisSett.get_redis_instance(2)
