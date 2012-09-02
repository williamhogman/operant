"""Tests for the points system"""
from mock import Mock, patch, ANY

from nose.tools import ok_, eq_, raises

from operant.point import PointSystem


def _m_user():
    mck = Mock()
    mck.operant_id.return_value = 1010
    return mck


class TestAward(object):

    def _ds_add_points(self, n):
        ds = Mock()
        ds.add_points.side_effect = lambda a, b, c, callback: callback(n)
        return ds

    def test_award(self):
        ds = self._ds_add_points(9)

        points_id = "test.testpoint"
        point = PointSystem(points_id)

        cb = Mock()
        point.award(ds, _m_user(), 1, cb)

        ds.add_points.assert_called_once_with(1010, point, 1, ANY)
        ds.track_event.assert_called_once()

        cb.assert_called_once_with(9)

    def test_get(self):
        ds = Mock()
        ds.get_points.side_effect = lambda a, b, callback: callback(10)

        points_id = "test.testpoint"
        point = PointSystem(points_id)

        cb = Mock()
        point.get_count(ds, _m_user(), cb)

        cb.assert_called_once_with(10)

    def test_on_awarded_hook(self):
        ds = self._ds_add_points(5)

        points_id = "test.testpoint"
        point = PointSystem(points_id)

        on_awarded = Mock()
        setattr(point, "on_awarded_points", on_awarded)

        cb = Mock()

        user = _m_user()
        point.award(ds, user, 1, cb)

        on_awarded.assert_called_once_with(user, 5, 1)
