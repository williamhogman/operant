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
        if user.operant_ds().has_attribute(self._get_ds_name()):
            return False

        return self._precondition(user)

    def _get_ds_name(self):
        return ("operant.badge",self.badge_id)

    def _add_badge_to_user(self,user):
        ds = user.operant_ds()
        ds.add_attribute(self._get_ds_name())
        ds.log("badge.awarded",self.badge_id)
        return True

    def award(self,user):
        """Awards a badge to a user"""
        if self._check_preconditions(user):
            return self._add_badge_to_user(user)
        else:
            return False
