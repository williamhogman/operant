"""Module for plain redis support"""
try:
    from numbers import Integral
except ImportError:
    Integral = [int,long]

import json

import zope.interface as interface



import redis

import operant.data

def _mkname(*args):
    return ":".join(args)

def _user_id(id_):
    if isinstance(id_,Integral):
        return str(id_)
    else:
        return id_

@interface.implementer(operant.data.IStorageProvider)
class Redis(object):

    def __init__(self, client):
        if isinstance(client, dict):
            client = redis.StrictRedis(**client)
        self.client = client

    def add_badge(self, user, badge, callback):
        key = _mkname("badges", _user_id(user))

        success = self.client.sadd(key,badge.badge_id) == 1

        callback(success)

    def track_event(self, event, subject=None, ext={}):
        gkey = _mkname("events")
        pkey = _mkname("events",_user_id(subject))

        
        if ext:
            body = (event, subject, ext)
        else:
            body = (event, subject)

        s = json.dumps(body)

        pipe = self.client.pipeline()

        pipe.lpush(gkey, s)
        pipe.lpush(pkey, s)

        pipe.execute()

        callback(True)


    def _counter_add(self, user, counter, amount, callback):
        hash_name = _mkname("counter", _user_id(user))

        res = self.client.hincrby(hash_name, counter, amount)

        callback(res)
        
    def _counter_get(self, user, counter, amount, callback):
        hash_name = _mkname("counter", _user_id(user))

        res = self.client.hget(hash_name, counter, amount)
        
        if isinstance(res,basestring):
            try:
                callback(int(res))
            except ValueError:
                callback(float(res))
        elif res is None:
            callback(0)
        else:
            callback(res)
            

    def add_balance(self, user, currency, amount, callback):
        self._counter_add(user, _mkname("currency", currency.currency_id), amount, callback)

    def deduct_balance(self, user, currency, amount, callback):
        self.add_balance(user, currency, -amount, callback)

    def get_balance(self, user, currency, callback):
        self._counter_get(user, _mkname("currency", currency.currency_id), amount, callback)