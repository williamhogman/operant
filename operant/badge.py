"""Module for badges
"""
from __future__ import (with_statement,print_function,division,absolute_import)
from time import time
from collections import namedtuple

class BadgePrototype(object):
    """A prototype that builds a badge"""
    
    def __init__(self,badge_id):
        self.badge_id = badge_id

    def _precondition(self,user):
        return True

    def _check_preconditions(self,user):
        if user.has_badge(self.badge_id):
            return False

        return self._precondition(user)

    def _add_badge_to_user(self,user):
        badge = AwardedBadge(self.badge_id,user.operant_id(),int(time()))
        user.add_badge(badge)
        return badge

    def award(self,user):
        """Awards a badge to a user"""
        if self._check_preconditions(user):
            return self._add_badge_to_user(user)
        else:
            return False
        

AwardedBadge = namedtuple("AwardedBadge",["badge_id","to","awarded_at"])
