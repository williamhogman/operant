"""Tests for the redis"""
try:
    from mock import Mock,patch,ANY
except ImportError:
    from unittest.mock import Mock,patch,ANY

from nose.tools import ok_, eq_, raises

from operant.storage import plain_redis


class TestRedis(object):
    def mocked_provider(self, mock):
        return plain_redis.Redis(mock)

    def mock_badge(self, name="TestBadge"):
        m = Mock()
        m.badge_id = name
        return m

    def test_add_badge(self):
        mck = Mock()
        mck.sadd.return_value = 1
        cli = self.mocked_provider(mck)

        badge = self.mock_badge()

        callback = Mock()

        cli.add_badge(1010, badge, callback)

        mck.sadd.assert_called_once_with("badges:1010","TestBadge")
    
        callback.assert_called_once_with(True)

    def test_add_badge_existing(self):
        mck = Mock()
        mck.sadd.return_value = 0
        cli = self.mocked_provider(mck)

        badge = self.mock_badge()

        callback = Mock()
        cli.add_badge(1010, badge, callback)
        
        mck.sadd.assert_called_once_with("badges:1010", "TestBadge")

        callback.assert_called_once_with(False)