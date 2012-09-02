"""Tests for the currency system"""
from mock import Mock, patch, ANY, sentinel
from nose.tools import ok_, eq_, raises

from operant.currency import Currency

def _m_user():
    mck = Mock()
    mck.operant_id.return_value = 1010
    return mck


class TestCurrency(object):

    def _ds_add_balance(self, n):
        def _add_balance(a, b, c, callback=None):
            callback(n)
        ds = Mock()
        ds.add_balance.side_effect = _add_balance
        return ds

    def _ds_get_balance(self, n):
        def _get_balance(a, b, callback=None):
            callback(n)
        ds = Mock()
        ds.get_balance.side_effect = _get_balance
        return ds

    def _ds_deduct_balance(self, n):
        def _deduct_balance(a, b, c, callback=None):
            callback(n)
        ds = Mock()
        ds.deduct_balance.side_effect = _deduct_balance
        return ds

    def test_award(self):
        ds = self._ds_add_balance(9)

        currency_id = "test.testcurrency"
        currency = Currency(currency_id)

        cb = Mock()
        currency.award(ds, _m_user(), 1, cb)

        cb.assert_called_once_with(9)
        ds.add_balance.assert_called_once_with(1010, currency, 1, ANY)

    def test_deduct(self):
        ds = self._ds_deduct_balance(9)

        currency_id = "test.testcurrency"
        currency = Currency(currency_id)

        cb = Mock()
        currency.deduct_balance(ds, _m_user(), 1, cb)

        cb.assert_called_once_with(9)
        ds.deduct_balance.assert_called_once_with(1010, currency, 1, ANY)

    def test_get(self):
        ds = self._ds_get_balance(9)

        currency_id = "test.testcurrency"
        currency = Currency(currency_id)

        cb = Mock()
        currency.get_balance(ds, _m_user(), cb)

        cb.assert_called_once_with(9)
        ds.get_balance.assert_called_once_with(1010, currency, ANY)
