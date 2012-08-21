"""Tests for the redis"""
try:
    from mock import Mock,patch,ANY
except ImportError:
    from unittest.mock import Mock,patch,ANY

from nose.tools import ok_, eq_, raises
from nose.plugins.skip import SkipTest

import functools
import inspect

missing_redis = False
try:
    from operant.storage import plain_redis
except ImportError:
    missing_redis = True

missing_tornado = False

try:
    from operant.storage import tornado_redis
except ImportError:
    missing_tornado = True

def mock_badge(name="TestBadge"):
    m = Mock()
    m.badge_id = name
    return m

class TestRedis(object):
    def mocked_provider(self, mock):
        if missing_redis:
            raise SkipTest
        return plain_redis.Redis(mock)

    def test_add_badge(self):
        mck = Mock()
        mck.sadd.return_value = 1
        cli = self.mocked_provider(mck)

        badge = mock_badge()

        callback = Mock()

        cli.add_badge(1010, badge, callback)

        mck.sadd.assert_called_once_with("badges:1010","TestBadge")
    
        callback.assert_called_once_with(True)

    def test_add_badge_existing(self):
        mck = Mock()
        mck.sadd.return_value = 0
        cli = self.mocked_provider(mck)

        badge = mock_badge()

        callback = Mock()
        cli.add_badge(1010, badge, callback)
        
        mck.sadd.assert_called_once_with("badges:1010", "TestBadge")

        callback.assert_called_once_with(False)

class TestTornadoRedis(object):

    def mocked_provider(self, mock):
        if missing_tornado:
            raise SkipTest
        return tornado_redis.TornadoRedis(mock)

    def test_add_badge(self):
        mck = Mock()
        mck.sadd.side_effect = lambda key, item, callback=None: callback(1)
        cli = self.mocked_provider(mck)

        badge = mock_badge()

        callback = Mock()
        cli.add_badge(1010, badge, callback)

        mck.sadd.assert_called_once_with("badges:1010", "TestBadge", callback=ANY)
        
        callback.assert_called_once_with(True)

    def test_add_badge_existing(self):
        mck = Mock()
        mck.sadd.side_effect = lambda key, item, callback=None: callback(0)
        cli = self.mocked_provider(mck)

        badge = mock_badge()

        callback = Mock()
        cli.add_badge(1010, badge, callback)

        mck.sadd.assert_called_once_with("badges:1010", "TestBadge", callback=ANY)
        
        callback.assert_called_once_with(False)