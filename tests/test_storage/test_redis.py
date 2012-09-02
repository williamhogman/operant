"""Tests for the redis"""

from mock import Mock,patch,ANY, sentinel, call
from nose.tools import ok_, eq_, raises
from nose.plugins.skip import SkipTest
import six

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

import operant.storage.common_redis as common_redis

def mock_badge(name="TestBadge"):
    m = Mock()
    m.badge_id = name
    return m

def mock_points(name="TestPoints"):
    m = Mock()
    m.points_id = name
    return m

def mock_currency(name="TestCurrency"):
    m = Mock()
    m.currency_id = name
    return m

def test_redis_user_id_conv():
    ret = common_redis.user_id("foo")
    ok_(isinstance(ret, six.string_types))

    ret = common_redis.user_id(1010)
    ok_(isinstance(ret, six.string_types))

class CommonTests(object):

    def test_ctor(self):
        with patch(self.client_class) as p:
            # This should result in the constructor being called with
            # a dict.
            self.mocked_provider({"test": "foo"})
            p.assert_called_once_with(test="foo")

    def test_track_events(self):

        pipe = self._lpush_mck()
        cli = Mock()
        cli.pipeline.return_value = pipe

        ds = self.mocked_provider(cli)
        ds.track_event("test_ev", 1010, {"ext": "bar"})

        pipe.lpush.assert_has_calls([
            call("events", ANY),
            call("events:1010", ANY)
        ])
        pipe.execute.assert_called()

    def test_add_badge(self):
        mck = self._sadd_mck(1)
        cli = self.mocked_provider(mck)

        badge = mock_badge()

        callback = Mock()
        cli.add_badge(1010, badge, callback)

        self._aoc(mck.sadd, "badges:1010", "TestBadge")

        callback.assert_called_once_with(True)

    def test_add_badge_existing(self):
        mck = self._sadd_mck(0)
        cli = self.mocked_provider(mck)

        badge = mock_badge()

        callback = Mock()
        cli.add_badge(1010, badge, callback)

        self._aoc(mck.sadd, "badges:1010", "TestBadge")
        callback.assert_called_once_with(False)


    def test_get_points_none(self):
        # aka not found
        cli = self.mocked_provider(self._hget_mck(None))

        points = mock_points()

        callback = Mock()
        cli.get_points(1010, points, callback)

        callback.assert_called_once_with(0)

    def test_get_points_str_int(self):
        cli = self.mocked_provider(self._hget_mck("12"))

        points = mock_points()
        callback = Mock()
        cli.get_points(1010, points, callback)

        callback.assert_called_once_with(12)

    def test_get_points_str_float(self):
        cli = self.mocked_provider(self._hget_mck("13.37"))

        points = mock_points()
        callback = Mock()
        cli.get_points(1010, points, callback)

        callback.assert_called_once_with(13.37)

    def test_add_points(self):
        mck = self._hincrby_mck()
        cli = self.mocked_provider(mck)

        points = mock_points()

        callback = Mock()
        cli.add_points(1010, points, 1, callback)

        self._aoc(mck.hincrby, "counter:1010", "points:TestPoints", 1)
        callback.assert_called_once_with(10)

    def test_get_points(self):
        mck = self._hget_mck()
        cli = self.mocked_provider(mck)

        points = mock_points()

        callback = Mock()
        cli.get_points(1010, points, callback)
        self._aoc(mck.hget, "counter:1010", "points:TestPoints")
        callback.assert_called_once_with(10)

    def test_get_balance(self):
        cli = self.mocked_provider(self._hget_mck(10))

        currency = mock_currency()
        callback = Mock()
        cli.get_balance(1010, currency, callback)

        callback.assert_called_once_with(10)

    def test_add_balance(self):
        mck = self._hincrby_mck()
        cli = self.mocked_provider(mck)

        currency = mock_currency()
        callback = Mock()

        cli.add_balance(1010, currency, 5, callback)
        self._aoc(mck.hincrby, "counter:1010", "currency:TestCurrency", 5)
        callback.assert_called_once_with(10)


class TestRedis(CommonTests):
    client_class = "redis.StrictRedis"

    def setup(self):
        if missing_redis:
            raise SkipTest

    def mocked_provider(self, mock):
        if missing_redis:
            raise SkipTest
        return plain_redis.Redis(mock)

    def _sadd_mck(self, ret=1):
        mck = Mock()
        mck.sadd.return_value = ret
        return mck

    def _hincrby_mck(self, num=10):
        mck = Mock()
        mck.hincrby.return_value = num
        return mck

    def _aoc(self, m, *args, **kwargs):
        """Assert called once with a callback if applicable"""
        m.assert_called_once_with(*args, **kwargs)

    def _hget_mck(self, ret=10):
        mck = Mock()
        mck.hget.return_value = ret
        return mck

    def _lpush_mck(self, ret=1):
        mck = Mock()
        mck.lpush.return_value = ret
        return mck


class TestTornadoRedis(CommonTests):
    client_class = "tornadoredis.Client"

    def setup(self):
        if missing_tornado:
            raise SkipTest

    def _aoc(self, m, *args, **kwargs):
        """Assert called once with a callback if applicable"""
        if not "callback" in kwargs:
            kwargs["callback"] = ANY
        m.assert_called_once_with(*args, **kwargs)

    def mocked_provider(self, mock):
        if missing_tornado:
            raise SkipTest
        return tornado_redis.TornadoRedis(mock)

    def _sadd_mck(self, ret=1):
        def _sadd(key, item, callback=None):
            callback(ret)
        mck = Mock()
        mck.sadd.side_effect = _sadd
        return mck

    def _hincrby_mck(self, num=10):
        def _hincrby(key, item, amount, callback=None):
            callback(num)
        mck = Mock()
        mck.hincrby.side_effect = _hincrby
        return mck

    def _hget_mck(self, ret=10):
        def _hget(k, i, callback=None):
            callback(ret)
        mck = Mock()
        mck.hget.side_effect = _hget
        return mck

    def _lpush_mck(self, ret=1):
        def _lpush(lst, item, callback=None):
            if callback:
                callback(ret)
        mck = Mock()
        mck.lpush.side_effect = _lpush
        return mck
