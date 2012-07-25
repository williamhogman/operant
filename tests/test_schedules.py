"""Tests for schedules"""
try:
    from unittest.mock import Mock, patch, ANY
except ImportError:
    from mock import Mock, patch, ANY

from nose.tools import ok_, eq_, raises

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
