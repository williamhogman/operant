"""Reinforcement Schedules"""
from __future__ import (with_statement, print_function,
                        division, absolute_import)
import random
import time

from itertools import chain


def runif():
    """Returns a value between 0 and 1 from a uniform distribution"""
    return random.random()


def rnorm(m=0, s=1):
    """Returns a random value from a normal distribution with a given m and sd

    Takes two arugments a mean defaulting to zero, and a standard
    deviation with a default of one. Returns a value between -Inf and Inf.
    """
    return random.normalvariate(m, s)


def seconds():
    """Returns the time in seconds as an integer"""
    return int(time.time())


class RewardSchedule(object):

    def __init__(self, reward=1):
        self._reward = reward

    def __call__(self, *args, **kwargs):
        return self.calc_reward(*args, **kwargs)

    def _repr_options(self):
        return (None, None)

    def __repr__(self):
        main, opts = self._repr_options()
        bfr = [self.abbrev]
        if main:
            bfr.append(str(main))
        if opts:
            bfr.append("(" + str(opts) + ")")
        return "".join(bfr)

    def _accepted_args(self, pargs, nargs):
        as_named = chain(zip(self.tracking, pargs), nargs.items())
        return dict((k, v) for (k, v) in as_named if k in self.tracking)

    def _eval_condition(self, pargs, nargs, **kwargs):
        accepted = self._accepted_args(pargs, nargs)
        kwargs.update(accepted)
        return self._condition(**kwargs)

    def calc_reward(self, *args, **kwargs):
        return self._reward if self._eval_condition(args, kwargs) else 0


class RatioSchedule(RewardSchedule):
    def __init__(self, nth, *args, **kwargs):
        self._nth = nth
        super(RatioSchedule, self).__init__(*args, **kwargs)
        # Optimize nth == 1
        if self._nth == 1:
            self._condition = lambda *args, **kwargs: True

    def _repr_options(self):
        if self._reward != 1:
            return self._nth, "r=" + str(self._reward)
        else:
            return ""

    def _accepted_args(self, pargs, nargs):
        as_named = chain(zip(self.tracking, pargs), nargs.items())
        return dict((k, v) for (k, v) in as_named if k in self.tracking)


class FixedRatio(RatioSchedule):
    """Fixed ratio schedule. Returns reward every nth responses

    To use this scheme you need to keep track of the number of
    occurances yourself.
    """
    abbrev = "FR"
    tracking = ["current"]

    def _condition(self, current):
        return current > 0 and current % self._nth == 0


class VariableRatio(RatioSchedule):
    """Variable ratio schedule. Reward on average once every nth.

    The probability is constant, thus resulting in a variable reward
    frequency.
    """
    abbrev = "VR"
    tracking = []

    @property
    def _crit(self):
        if not hasattr(self, "__crit"):
            self.__crit = 1 - 1 / self._nth
        return self.__crit

    def _condition(self):
        return runif() > self._crit


class IntervalSchedule(RewardSchedule):
    """Base-classes for a schedule based on intervals."""
    tracking = ["last"]

    def __init__(self, interval, *args, **kwargs):
        self._interval = interval
        super(IntervalSchedule, self).__init__(*args, **kwargs)

    def calc_reward(self, *args, **kwargs):
        now = seconds()
        c = self._eval_condition(args, kwargs, now=now)
        if c:
            return (now, self._reward)
        else:
            return (None, 0)

    def _condition(self, last, now=seconds()):
        delta = now - last
        return self._delta_condition(delta)


class FixedInterval(IntervalSchedule):
    """Fixed interval schedule. Reward if a minimum time has passed.

    This schedule is suitable for making what in game design is called
    a cooldown mechanic, limiting the rate of which a reward is given.

    Calculating the reward returns, where the first item is either an int
    containing the current time to update the last occurance with. The
    second item is an int with the points to reward, if any.
    """

    def _delta_condition(self, delta):
        return delta >= self._interval


class VariableInterval(IntervalSchedule):
    """Variable interval schedule. Reward if a random time has passed.

    The time limit is randomized using the interval as mean and a
    setable standard deviation that defaults to 1. A standard
    deviation of one means that most of the interval will fall within
    +-1 from the mean interval which is on the low-end for most
    applications. For example for an interval of one hour a SD of 10
    minutes may be suitable.

    Calculating the reward returns a two tuple, where the first item
    is either an int containing the current time to update the last
    occurance with. The second item is an int with the points to
    reward, if any.

    Keep in mind that the time is randomized on each response, as
    opposed to pre-response, resulting in a higher chance of reward
    with more responses. However for most practical gamification
    purposes this should be a good enough approximation.
    """

    def __init__(self, interval, s=1, *args, **kwargs):
        self._s = s
        super(VariableInterval, self).__init__(*args,
                                               interval=interval, **kwargs)

    def _delta_condition(self, delta):
        return delta >= rnorm(self._interval, self._s)
