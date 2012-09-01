""" Module for point systems.

Points are a count of some kind, they are different from currency in
that they are not exchanged from anything else.
"""
from __future__ import (with_statement, print_function,
                        division, absolute_import)
from operant.base import Registry

class PointSystem(object):
    """A prototype for a point system.

    An instance of a PointSystem represents a type of points such as
    experience or frequenc flyer miles. Derived classes may be used to
    create point systems with different rules.
    """
    def __init__(self, points_id):
        self.points_id = points_id

    def on_awarded_points(self, user, now, amount):
        """ Called when a player has been awarded points of this kind.

        Override this method to implement custom logic like badges
        awarded every etc
        """

    def _add_points_to_user(self, store, user, amount, callback):
        def _cb(now):
            self.on_awarded_points(user, now, amount)
            callback(now)
        store.add_points(user.operant_id(), self, amount, _cb)

    def award(self, store, user, amount=1, callback=None):
        """Awards a number of points to a player"""
        def _cb(n):
            store.track_event("point.awarded." + self.points_id,
                              user.operant_id(), dict(amount=amount))
            callback(n)
        self._add_points_to_user(store, user, amount, _cb)

    def get_count(self, store, user, callback=None):
        """Gets the number of points a player has"""
        def _foo(x):
            callback(x)
        store.get_points(user.operant_id(), self, _foo)

PointSystems = Registry("point system", "points_id")
PointSystems.set_str_handler(PointSystem)

get = PointSystems.get
register = PointSystems.register
