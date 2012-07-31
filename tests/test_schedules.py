"""Tests for schedules"""
try:
    from unittest.mock import Mock, patch, ANY, sentinel
except ImportError:
    from mock import Mock, patch, ANY, sentinel

from nose.tools import ok_, eq_, raises
import collections

import operant.schedules as s


def _sum_rewards(sched, rn):
    return sum(map(sched, rn))


def rewards_eq(sched, rn, tot):
    eq_(_sum_rewards(sched, rn), tot)


class TestFixedRatio(object):

    def test_reward_every(self):
        f = s.FixedRatio(1)
        # if nth==1 reward everytime
        rewards_eq(f, range(10), 10)

    def test_reward_every_other(self):
        f = s.FixedRatio(2)
        rewards_eq(f, range(1, 11), 5)

    def test_no_initial_reward(self):
        f = s.FixedRatio(999)
        rewards_eq(f, range(10), 0)


class TestVariableRatio(object):

    def test_reward_every(self):
        f = s.VariableRatio(1)
        eq_(f(), 1)

    def test_reward_some(self):
        with patch("operant.schedules.runif", return_value=0.51):
            # 0.51 > 1/2 : Reward!
            f = s.VariableRatio(2)
            eq_(f(), 1)
            f = s.VariableRatio(3)
            # But not a 1/3
            eq_(f(), 0)

        with patch("operant.schedules.runif", return_value=0.67):
            # 0.67 > 1/3 : Reward!
            f = s.VariableRatio(3)
            eq_(f(), 1)


class TestFixedInterval(object):
    @patch("operant.schedules.seconds", return_value=30)
    def test_exactly_after(self, p):
        f = s.FixedInterval(10)
        eq_(f(20), (30, 1))

    @patch("operant.schedules.seconds", return_value=30)
    def test_reward_some(self, p):
        f = s.FixedInterval(31)
        eq_(f(0), (None, 0))

        f = s.FixedInterval(0)
        eq_(f(0), (30, 1))
        eq_(f(1), (30, 1))

        f = s.FixedInterval(10)
        eq_(f(10), (30, 1))


class TestVariableInterval(object):
    @patch("operant.schedules.rnorm", return_value=20)
    @patch("operant.schedules.seconds", return_value=30)
    def test_reward_some(self, sec, rnd):
        f = s.VariableInterval(20, 1)

        # 30 - 10 = 20 since last OK given our rnd
        eq_(f(10), (30, 1))
        rnd.assert_called_once_with(20, 1)

        # 30 - 20 = 10 not OK given our rnd
        eq_(f(20), (None, 0))
        rnd.assert_called_with(20, 1)


class TestCombined(object):
    def _mock_sched(self, ret):
        sched = Mock()
        sched.return_value = ret
        sched.tracking = list()
        return sched

    def test_combining(self):
        s1 = self._mock_sched(sentinel.r1)
        s2 = self._mock_sched(sentinel.r2)
        comb = s.Combined(s1, s2)

        a, b = comb()

        eq_(a, sentinel.r1)
        eq_(b, sentinel.r2)

    def test_null_combined(self):
        comb = s.Combined([])
        ret = comb()
        ok_(isinstance(ret, collections.Iterable))
        eq_(list(ret), [])

    def test_applying_args(self):
        s1 = self._mock_sched(sentinel.r1)
        s2 = self._mock_sched(sentinel.r2)

        s1.tracking = ["foo"]
        s2.tracking = ["foo", "bar"]

        comb = s.Combined(s1, s2)

        ret = comb.call_nonlazy(foo=sentinel.foo_arg,
                                bar=sentinel.bar_arg)

        # Both should get foo
        s1.assert_called_once_with(foo=sentinel.foo_arg)
        s2.assert_called_once_with(foo=sentinel.foo_arg,
                                   bar=sentinel.bar_arg)
