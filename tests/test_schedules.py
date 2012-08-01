"""Tests for schedules"""
try:
    from unittest.mock import Mock, patch, ANY, sentinel
except ImportError:
    from mock import Mock, patch, ANY, sentinel

from nose.tools import ok_, eq_, raises
import collections
import math

import operant.schedules as s


def _sum_rewards(sched, rn):
    return sum(map(sched, rn))


def rewards_eq(sched, rn, tot):
    eq_(_sum_rewards(sched, rn), tot)


class TestSchedule(object):

    def _deriv_class(self):
        class Foo(s._Schedule):
            abbrev = "Foo"
        return Foo

    def _deriv_inst(self):
        return self._deriv_class()()

    def test_repr(self):
        r = repr(self._deriv_inst())
        eq_(r, "Foo")

    def test_add(self):
        f1 = self._deriv_inst()
        f2 = self._deriv_inst()

        res = f1 + f2
        ok_(isinstance(res, s.Combined))

        r1, r2 = list(res)

        eq_(r1, f1)
        eq_(r2, f2)


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
        with patch("operant.schedules.runif",
                   return_value=0.51):

            # 0.51 > 1/2 : Reward!
            f = s.VariableRatio(2)
            eq_(f(), 1)
            f = s.VariableRatio(3)
            # But not a 1/3
            eq_(f(), 0)

        with patch("operant.schedules.runif",
                   return_value=0.67):

            # 0.67 > 1/3 : Reward!
            f = s.VariableRatio(3)
            eq_(f(), 1)


class TestInterval(object):

    def test_repr(self):
        class Foo(s._Interval):
            abbrev = "foo"
        inst = Foo(10)

        r = repr(inst)
        ok_(Foo.abbrev in r)
        ok_("10" in r)


class TestRatio(object):

    def _deriv(self):
        class Foo(s._Ratio):
            abbrev = "foo"
        return Foo

    def test_repr(self):
        inst = self._deriv()(10, reward=99)
        r = repr(inst)
        ok_("r=99" in r)

    def test_no_repr_ext(self):
        inst = self._deriv()(10, reward=1)
        r = repr(inst)
        ok_("r=1" not in r)


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
        sched.__repr__ = lambda self: repr(ret)
        return sched

    def test_adding(self):
        s1 = self._mock_sched(sentinel.r1)
        s2 = self._mock_sched(sentinel.r2)

        comb1 = s.Combined([s1])
        comb2 = s.Combined([s2])

        added = comb1 + comb2

        a, b = added()
        eq_(a, sentinel.r1)
        eq_(b, sentinel.r2)

    def test_adding_any(self):
        comb = s.Combined([])

        ret = comb + sentinel.part

        ok_(sentinel.part in list(ret))

    def test_repr(self):
        s1 = self._mock_sched(sentinel.r1)
        s2 = self._mock_sched(sentinel.r2)

        comb = s.Combined(s1, s2)

        r = repr(comb)

        res = eval(r, {"Combined": s.Combined, "sentinel": sentinel})

        eq_(repr(res), r)  # we can recreate the exact same repr

    def test_combining(self):
        s1 = self._mock_sched(sentinel.r1)
        s2 = self._mock_sched(sentinel.r2)
        comb = s.Combined(s1, s2)

        a, b = comb()

        eq_(a, sentinel.r1)
        eq_(b, sentinel.r2)

    def test_combined_one_arg(self):
        comb = s.Combined(sentinel.foo)
        ok_(sentinel.foo in list(comb))

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


class TestMisc(object):
    def test_runif(self):
        ret = s.runif()
        ok_(1 > ret > 0)

    def test_rnorm(self):
        ret = s.rnorm()
        # Test for strange behaviour
        wtf = not 3 > ret > -3
        if wtf:
            # measure the deviation from the mean
            d = sum(math.fabs(s.rnorm()) for i in range(100)) / 100
            ok_(d < 2, "Our RNG is exhibiting strange"
                "behaviour, see if you can repro")
