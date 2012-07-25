"""Reinforcement Schedules"""
from __future__ import (with_statement, print_function,
                        division, absolute_import)
import random
import time


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
    def __call__(self, *args, **kwargs):
        return self.calc_reward(*args, **kwargs)


class RatioSchedule(RewardSchedule):
    def calc_reward(self, *args, **kwargs):
        return self._reward if self._condition(*args, **kwargs) else 0


class FixedRatio(RatioSchedule):
    """Fixed ratio schedule. Returns reward every nth responses

    To use this scheme you need to keep track of the number of
    occurances yourself.
    """

    def __init__(self, nth, reward=1):
        self._nth = nth
        self._reward = reward
        # Optimize nth == 1
        if self._nth == 1:
            self._condition = lambda current: True

    def _condition(self, current):
        return current > 0 and current % self._nth == 0


class VariableRatio(RatioSchedule):
    """Variable ratio schedule. Reward on average once every nth.

    The probability is constant, thus resulting in a variable reward
    frequency.
    """
    def __init__(self, nth, reward=1):
        self._crit = 1 - 1 / nth
        self._reward = reward

    def _condition(self):
        return runif() > self._crit


class IntervalSchedule(RewardSchedule):
    """Base-classes for a schedule based on intervals."""
    def calc_reward(self, last):
        now = seconds()
        delta = now - last
        return (now, self._reward) if self._condition(delta) else (None, 0)


class FixedInterval(IntervalSchedule):
    """Fixed interval schedule. Reward if a minimum time has passed.

    This schedule is suitable for making what in game design is called
    a cooldown mechanic, limiting the rate of which a reward is given.

    Calculating the reward returns, where the first item is either an int
    containing the current time to update the last occurance with. The
    second item is an int with the points to reward, if any.
    """
    def __init__(self, interval, reward=1):
        self._reward = reward
        self._interval = interval

    def _condition(self, delta):
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

    def __init__(self, interval, s=1, reward=1):
        self._interval = interval
        self._s = s
        self._reward = reward

    def _condition(self, delta):
        return delta >= rnorm(self._interval, self._s)
