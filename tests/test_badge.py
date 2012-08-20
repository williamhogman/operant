"""Tests for the badge system"""
try:
    from mock import Mock,patch,ANY
except ImportError:
    from unittest.mock import Mock,patch,ANY

from nose.tools import ok_,eq_,raises

from operant.badge import BadgePrototype,get_badge,register_badge

def dprovider():
    return Mock()

def test_no_dupes():
    ds = dprovider()
    ds.add_badge.side_effect = lambda user, badge, cb: cb(False)

    user = Mock()
    user.operant_id = 1010

    badge_id = "test.testbadge1"
    badge = BadgePrototype(badge_id)
    
    callback = Mock()
    badge.award(ds, user, callback)

    callback.assert_called_once_with(False)

    # not added to logs
    eq_(len(ds.track_event.mock_calls),0)

def test_award():
    ds = Mock()
    ds.add_badge.side_effect = lambda user, badge, cb: cb(True)

    badge_id = "test.testbadge2"
    badge = BadgePrototype(badge_id)

    callback = Mock()

    user = Mock()
    user.operant_id = 1010

    badge.award(ds, user, callback)
    
    callback.assert_called_once_with(True)

    dbname = ("operant.badge",badge_id)

    ds.track_event.assert_called_once_with('badge.awarded.test.testbadge2',user)


@raises(RuntimeError)
def test_register_existing_badge():
    b = BadgePrototype("test.testbadge3")
    register_badge(b)

    b2 = BadgePrototype("test.testbadge3")
    
    register_badge(b2)

def test_register_badge():
    b = BadgePrototype("test.testbadge4")
    register_badge(b)

    eq_(get_badge("test.testbadge4"),b)

def test_get_badge():
    eq_(get_badge("___not.a.badge"),None)
