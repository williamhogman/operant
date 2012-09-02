import zope.interface as interface

try:
    import tornadoredis
except ImportError:
    raise ImportError("You need to install tornado-redis to"
                      "use this storage module")
import operant.data
from operant.storage.common_redis import mkname, user_id, RedisCommon


@interface.implementer(operant.data.IStorageProvider)
class TornadoRedis(RedisCommon):

    def __init__(self, client):
        if isinstance(client, dict):
            client = tornadoredis.Client(**client)
        self.client = client

    def add_badge(self, user, badge, callback):
        def parse(n):
            callback(n == 1)

        key = mkname("badges", user_id(user))
        self.client.sadd(key, badge.badge_id, callback=parse)

    def _add_to_ev(self, data, subject=None):
        gkey = mkname("events")
        pkey = mkname("events", user_id(subject))

        pipe = self.client.pipeline()
        pipe.lpush(gkey, data)
        pipe.lpush(pkey, data)
        pipe.execute(callback=lambda x: None)

    def _counter_add(self, user, counter, amount, callback):
        hash_name = mkname("counter", user_id(user))
        self.client.hincrby(hash_name, counter,
                            amount, callback=callback)

    def _counter_get(self, user, counter, callback):
        def parse(res):
            if isinstance(res, basestring):
                try:
                    callback(int(res))
                except ValueError:
                    callback(float(res))
            elif res is None:
                callback(0)
            else:
                callback(res)
        hash_name = mkname("counter", user_id(user))
        self.client.hget(hash_name, counter, callback=parse)
