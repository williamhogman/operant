"""Tests for the badge system"""
from mock import Mock,patch,ANY
from nose.tools import ok_,eq_,raises

from operant.badge import BadgePrototype,get_badge,register_badge

def user_with_ds(ds):
    user = Mock()
    user.operant_ds.return_value = ds
    return user

def test_no_dupes():
    ds = Mock()
    ds.has_attribute.return_value = True
    user = user_with_ds(ds)

    badge_id = "test.testbadge1"
    badge = BadgePrototype(badge_id)
    
    eq_(badge.award(user),False,
        "awarding a badge to a user who already has one should return false")

    # Checking should be done
    ds.has_attribute.assert_called_once_with(("operant.badge",badge_id))
    # but add_attribute shouldn't be called
    eq_(len(ds.add_attribute.mock_calls),0)
    # nor should it be logged
    eq_(len(ds.log.mock_calls),0)

def test_award():
    ds = Mock()
    ds.has_attribute.return_value = False
    user = user_with_ds(ds)


    badge_id = "test.testbadge2"
    badge = BadgePrototype(badge_id)

    rtn = badge.award(user)
    ok_(rtn)

    dbname = ("operant.badge",badge_id)
    # We should check before we add
    ds.has_attribute.assert_called_once_with(dbname)
    # and after that we should add it
    ds.add_attribute.assert_called_once_with(dbname)

    ds.log.assert_called_once_with("badge.awarded",badge_id)

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
