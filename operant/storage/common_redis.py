"""Functions common to all our redis storage implementations"""
try:
    from numbers import Integral
except ImportError:
    Integral = [int, long]

import json


def mkname(*args):
    return ":".join(args)


def user_id(id_):
    if isinstance(id_, Integral):
        return str(id_)
    else:
        return id_


class RedisCommon(object):

    def add_balance(self, user, currency, amount, callback):
        self._counter_add(user,
                          mkname("currency", currency.currency_id),
                          amount, callback)

    def deduct_balance(self, user, currency, amount, callback):
        self.add_balance(user, currency, -amount, callback)

    def get_balance(self, user, currency, callback):
        self._counter_get(user,
                          mkname("currency", currency.currency_id),
                          amount, callback)

    def track_event(self, event, subject=None, ext={}):
        if ext:
            body = (event, subject, ext)
        else:
            body = (event, subject)

        data = json.dumps(body)
        self._add_to_ev(data, subject)

