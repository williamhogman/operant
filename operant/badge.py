"""Module for badges
"""
from __future__ import (with_statement, print_function,
                        division, absolute_import)


class BadgePrototype(object):
    """A prototype that builds a badge"""

    def __init__(self, badge_id):
        self.badge_id = badge_id

    def _precondition(self, user):
        return True

    def check_preconditions(self, user):
        return self._precondition(user)

    def _get_ds_name(self):
        return ("operant.badge", self.badge_id)

    def _add_badge_to_user(self, store, user, callback):

        def cb(success):
            if success:
                store.track_event(
                    ("badge", "awarded", self._badge_id),
                    user)
            callback(success)

        store.add_badge(user, self, cb)

    def award(self, store, user):
        """Awards a badge to a user"""
        if self._check_preconditions(store, user):
            return self._add_badge_to_user(store, user)
        else:
            return False


class Badges(object):
    """Class holding every registered badge in the system"""
    _badges = {}

    @classmethod
    def register(cls, badge):
        """Registers a badge with the badges collection"""
        if badge.badge_id in cls._badges:
            raise RuntimeError("A badge with the id {0} "
                               "has already been registered"
                               .format(badge.badge_id))
        cls._badges[badge.badge_id] = badge

    @classmethod
    def get(cls, badge_id):
        """Gets a named badge from the badge collection"""
        return cls._badges.get(badge_id, None)

get_badge = Badges.get
register_badge = Badges.register
