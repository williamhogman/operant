"""Module for currency systems.

Currencies are a closely related to points, but differ in that they
are often exchanged for rewards of some kind. The value of a
currencies stem from what they are traded in, while points often carry
some intrinsic value. A currency loses this intrinsic value because it
is redeemable.
"""
from __future__ import (with_statement, print_function,
                        division, absolute_import)
from operant.base import Registry

class Currency(object):
    """An instance of this class represents currency"""

    def __init__(self, currency_id):
        self.currency_id = currency_id

    def _add_currency_to_user(self, store, user, amount, callback):
        store.add_balance(user.operant_id(), self, amount, callback)

    def _deduct_currency_from_user(self, store, user, amount, callback):
        store.deduct_balance(user.operant_id(), self, amount, callback)

    def award(self, store, user, amount=1, callback=None):
        """Awards the passed in amount of this currency"""
        def _cb(n):
            store.track_event("currency.awarded." + self.currency_id,
                              user.operant_id(), dict(amount=amount))
            callback(n)
        self._add_currency_to_user(store, user, amount, _cb)

    def deduct_balance(self, store, user, amount=1, callback=None):
        """Deducts the passed in amount of this currency from the player"""
        def _cb(n):
            store.track_event("currency.deducted." + self.currency_id,
                              user.operant_id(), dict(amount=amount))
            callback(n)
        self._deduct_currency_from_user(store, user, amount, _cb)

    def get_balance(self, store, user, callback=None):
        """Gets the users balance in the passed  in currency"""
        store.get_balance(user.operant_id(), self, callback)

Currencies = Registry("currency", "currency_id")

get = Currencies.get
register = Currencies.register
