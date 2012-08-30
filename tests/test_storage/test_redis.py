"""Tests for the redis"""
try:
    from mock import Mock,patch,ANY, sentinel
except ImportError:
    from unittest.mock import Mock,patch,ANY, sentinel

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

def mock_points(name="TestPoints"):
    m = Mock()
    m.points_id = name
    return m

class CommonTests(object):
    def test_ctor(self):
        with patch(self.client_class) as p:
            # This should result in the constructor being called with
            # a dict.
            self.mocked_provider({"test": "foo"})
            p.assert_called_once_with(test="foo")

class TestRedis(CommonTests):
    client_class = "redis.StrictRedis"

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

        mck.sadd.assert_called_once_with("badges:1010", "TestBadge")
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

    def test_add_points(self):
        mck = Mock()
        mck.hincrby.return_value = 10

        cli = self.mocked_provider(mck)

        points = mock_points()

        callback = Mock()

        cli.add_points(1010, points, 1, callback)

        mck.hincrby.assert_called_once("counter:1010",
                                       "points:TestPoints",
                                       1)
        callback.assert_called_once_with(10)



class TestTornadoRedis(CommonTests):
    client_class = "tornadoredis.Client"

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

        mck.sadd.assert_called_once_with("badges:1010",
                                         "TestBadge",
                                         callback=ANY)

        callback.assert_called_once_with(True)

    def test_add_badge_existing(self):
        mck = Mock()
        mck.sadd.side_effect = lambda key, item, callback=None: callback(0)
        cli = self.mocked_provider(mck)

        badge = mock_badge()

        callback = Mock()
        cli.add_badge(1010, badge, callback)

        mck.sadd.assert_called_once_with("badges:1010",
                                         "TestBadge",
                                         callback=ANY)
        callback.assert_called_once_with(False)

    def test_add_points(self):

        def _hincrby(key, item, amount, callback=None):
            callback(10)

        mck = Mock()
        mck.hincrby.side_effect = _hincrby

        cli = self.mocked_provider(mck)

        points = mock_points()

        callback = Mock()

        cli.add_points(1010, points, 1, callback)

        mck.hincrby.assert_called_once("counter:1010",
                                       "points:TestPoints",
                                       1,
                                       callback=ANY)
        callback.assert_called_once_with(10)
