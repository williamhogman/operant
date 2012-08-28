"""Module for badges
"""
from __future__ import (with_statement, print_function,
                        division, absolute_import)
from operant.base import Registry


class BadgePrototype(object):
    """A prototype that builds a badge"""

    def __init__(self, badge_id):
        self.badge_id = badge_id

    def _precondition(self, user):
        return True

    def _check_preconditions(self, user):
        return self._precondition(user)

    def _add_badge_to_user(self, store, user, callback):

        def cb(success):
            if success:
                store.track_event("badge.awarded." + self.badge_id,
                                  user.operant_id())
                callback(self)
            else:
                callback(False)
        user_id = user.operant_id()
        store.add_badge(user_id, self, cb)

    def award(self, store, user, callback):
        """Awards a badge to a user"""
        if self._check_preconditions(user):
            self._add_badge_to_user(store, user, callback)
        else:
            callback(False)


Badges = Registry("badge", "badge_id")
Badges.set_str_handler(BadgePrototype)

get_badge = Badges.get
register_badge = Badges.register
