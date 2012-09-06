"""Common functionality for modules based on mongodb

operant stores its objectes like this:

There is one collection called operant_user containing
documents containing counters and badges (sets)

"""
import pymongo
import pymongo.database
def counter_name(*args):
    return "counters." + "_".join(arg.replace(".", "_") for arg in args)


def currency_name(currency):
    return counter_name("currency", currency.currency_id)


def points_name(points):
    return counter_name("points", currency.currency_id)


def _extract_field(names, obj):
    cur = obj
    for name in names:
        cur = cur.get(name)
    return cur

def _extract_currency(currency, obj):
    return _extract_field((
        "counters",
        "currency_" + currency.currency_id),
        obj)


class MongoBase(object):
    """Base class for mongodb drivers"""

    @property
    def _users_col(self):
        return self._db.operant_users

    @property
    def _log_col(self):
        return self._db.operant_log

    def _badge_add(self, user, badge, callback):
        def _parse(res):
            if res is None:
                callback(False)
            else:
                callback(True)

        res = self._update_user({"_id": user, "$not": {"badges": badge}},
                                {"$addToSet": {"badges": badge}},
                                callback=_parse)

    def _counter_add(self, user, key, amount, callback):
        self._update_user({"_id": user},
                          {"$inc": {key: amount}},
                          {key: 1},
                          callback=callback)

    def _counter_get(self, user, key, callback=None):
        self._find_user({"_id": user},
                        {key: 1},
                        callback=callback)

    def add_balance(self, user, currency, amount, callback):
        def _parse(obj):
            res = _extract_currency(currency, obj)
            callback(res)

        self._counter_add(user, currency_name(currency),
                          amount, _parse)

    def deduct_balance(self, user, currency, amount, callback):
        self.add_balance(user, currency, -amount, callback)

    def get_balance(self, user, currency, callback):
        def _parse(obj):
            res = _extract_currency(currency, obj)
            callback(res)
        self._counter_get(user, currency_name(currency), _parse)

    def add_points(self, user, points, count, callback):
        self._counter_add(user, points_name(points), count, callback)

    def deduct_points(self, user, points, count, callback):
        self.add_points(user, points, -count, callback)

    def get_points(self, user, points, callback):
        self._counter_get(user, points_name(points), callback)

    def track_event(self, event, subject=None, ext=None):
        self._insert_log(dict(event=event, subject=subject, ext=ext))

    def add_badge(self, user, badge, callback):
        self._badge_add(user, badge.badge_id, callback)
