"""Module for plain redis support"""
import zope.interface as interface

try:
    import redis
except ImportError:
    raise ImportError("You need to install the redis python package to"
                      "use this storage module")

import operant.data
from operant.storage.common_redis import mkname, user_id, RedisCommon

from six import string_types

@interface.implementer(operant.data.IStorageProvider)
class Redis(RedisCommon):

    def __init__(self, client):
        if isinstance(client, dict):
            client = redis.StrictRedis(**client)
        self.client = client

    def add_badge(self, user, badge, callback):
        key = mkname("badges", user_id(user))
        success = self.client.sadd(key, badge.badge_id) == 1
        callback(success)

    def _add_to_ev(self, data, subject):
        gkey = mkname("events")
        pkey = mkname("events", user_id(subject))

        pipe = self.client.pipeline()

        pipe.lpush(gkey, data)
        pipe.lpush(pkey, data)

        pipe.execute()

    def _counter_add(self, user, counter, amount, callback):
        hash_name = mkname("counter", user_id(user))

        res = self.client.hincrby(hash_name, counter, amount)

        callback(res)

    def _counter_get(self, user, counter, callback):
        hash_name = mkname("counter", user_id(user))

        res = self.client.hget(hash_name, counter)

        if isinstance(res, string_types):
            try:
                callback(int(res))
            except ValueError:
                callback(float(res))
        elif res is None:
            callback(0)
        else:
            callback(res)
