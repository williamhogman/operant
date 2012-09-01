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

        pipe = Mock()
        pipe.lpush.return_value = 1
        pipe.lpush.side_effect = lambda l, i, callback=None: callback and callback()
        cli = Mock()
        cli.pipeline.return_value = pipe

        ds = self.mocked_provider(cli)
        ds.track_event("test_ev", 1010, {"ext": "bar"})

        pipe.lpush.assert_has_calls([
                call("events", ANY),
                call("events:1010", ANY)
            ])
        pipe.execute.assert_called()

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


class TestRedis(CommonTests):
    client_class = "redis.StrictRedis"

    def setup(self):
        if missing_redis:
            raise SkipTest

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

    def _hget_mck(self, ret=10):
        mck = Mock()
        mck.hget.return_value = ret
        return mck

    def test_get_points(self):
        cli = self.mocked_provider(self._hget_mck())

        points = mock_points()

        callback = Mock()
        cli.get_points(1010, points, callback)

        callback.assert_called_once_with(10)

class TestTornadoRedis(CommonTests):
    client_class = "tornadoredis.Client"

    def setup(self):
        if missing_tornado:
            raise SkipTest

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

    def _hget_mck(self, ret=10):
        def _hget(k, i, callback=None):
            callback(ret)
        mck = Mock()
        mck.hget.side_effect = _hget
        return mck

    def test_get_points(self):
        cli = self.mocked_provider(self._hget_mck())

        points = mock_points()

        callback = Mock()
        cli.get_points(1010, points, callback)

        callback.assert_called_once_with(10)
