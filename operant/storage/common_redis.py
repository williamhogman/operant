"""Functions common to all our redis storage implementations"""
from six import integer_types
import json


def mkname(*args):
    return ":".join(args)


def user_id(id_):
    if isinstance(id_, integer_types):
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
                          callback)

    def track_event(self, event, subject=None, ext={}):
        body = (event, subject, ext)

        data = json.dumps(body)
        self._add_to_ev(data, subject)

    def get_points(self, user, points, callback):
        self._counter_get(user,
                          mkname("points", points.points_id),
                          callback=callback)

    def add_points(self, user, points, count, callback):
        self._counter_add(user,
                          mkname("points", points.points_id),
                          count, callback=callback)
