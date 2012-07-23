"""Tests for the badge system"""
from mock import Mock,patch,ANY
from nose.tools import ok_,eq_

from operant.badge import BadgePrototype

def test_no_dupes():
    user = Mock()
    user.has_badge.return_value = True

    badge_id = "test.testbadge1"
    badge = BadgePrototype(badge_id)
    
    eq_(badge.award(user),False,
        "awarding a badge to a user who already has one should return false")

    user.has_badge.assert_called_once_with(badge_id)

def test_award():
    user = Mock()
    user.has_badge.return_value = False

    badge_id = "test.testbadge2"
    badge = BadgePrototype(badge_id)

    rtn = badge.award(user)

    eq_(rtn.badge_id,badge_id)
    eq_(rtn.to,user.operant_id.return_value)
    ok_(isinstance(rtn.awarded_at,int))

    user.add_badge.assert_called_once_with(rtn)
