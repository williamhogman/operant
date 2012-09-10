"""Tests for mongodb modules"""
from mock import Mock, patch, ANY, sentinel, call
from nose.tools import ok_, eq_, raises
from nose.plugins.skip import SkipTest

has_mongodb = True
try:
    import operant.storage.mongodb_plain
except ImportError:
    has_mongodb = False


def mock_currency(name="TestCurrency"):
    m = Mock()
    m.currency_id = name
    return m


def mock_badge(name="TestBadge"):
    m = Mock()
    m.badge_id = name
    return m


def mock_points(name="TestPoints"):
    m = Mock()
    m.points_id = name
    return m


class _MongoMock(object):
    def __init__(self, stuff):
        self.__dict__.update(stuff)

    def __getitem__(self, name):
        return self.__dict__[name]


def _simplemock(dbname, colname, colmock):
    db = _MongoMock({colname: colmock})
    return _MongoMock({dbname: db})


def _find_mod_rtn(uid, fields):
    d = dict(_id=uid)
    d.update(fields)
    return d


def _test_currency_mod_rtn(userid, ret):
    return _find_mod_rtn(userid, {
        "counters": {"currency_TestCurrency": ret}
    })


def _test_points_mod_rtn(userid, ret):
    return _find_mod_rtn(userid, {
        "counters": {"points_TestPoints": ret}
    })


def _test_badge_mod_rtn(userid, ret):
    return _find_mod_rtn(userid, {"badges": [ret]})


class CommonTests(object):

    def test_ctor(self):
        with patch(self.client_class) as p:
            # This should result in the constructor being called with
            # a dict.
            self.mocked_provider({"test": "foo"})
            p.assert_called_once_with(test="foo")

    def test_add_points(self):
        mck = self._find_mod_mck(_test_points_mod_rtn(1010, 5))
        db = _simplemock("operant", "operant_users", mck)
        ds = self.mocked_provider(db)

        callback = Mock()
        ds.add_points(1010, mock_points(), 5, callback=callback)

        callback.assert_called_once_with(5)

        self._aoc(mck.find_and_modify,
                  {"_id": 1010},
                  {"$inc": {"counters.points_TestPoints": 5}},
                  fields={"counters.points_TestPoints": 1},
                  upsert=True, new=True)

    def test_deduct_points(self):
        mck = self._find_mod_mck(_test_points_mod_rtn(1010, 2))
        db = _simplemock("operant", "operant_users", mck)
        ds = self.mocked_provider(db)

        callback = Mock()
        ds.deduct_points(1010, mock_points(), 5, callback=callback)

        callback.assert_called_once_with(2)

        self._aoc(mck.find_and_modify,
                  {"_id": 1010},
                  {"$inc": {"counters.points_TestPoints": -5}},
                  fields={"counters.points_TestPoints": 1},
                  upsert=True, new=True)

    def test_get_points(self):
        mck = self._find_mck(_test_points_mod_rtn(1010, 5))
        db = _simplemock("operant", "operant_users", mck)
        ds = self.mocked_provider(db)

        callback = Mock()
        ds.get_points(1010, mock_points(), callback=callback)

        callback.assert_called_once_with(5)

        self._aoc(mck.find,
                  {'_id': 1010},
                  {'counters.points_TestPoints': 1})

    def test_add_balance(self):
        mck = self._find_mod_mck(_test_currency_mod_rtn(1010, 5))
        db = _simplemock("operant", "operant_users", mck)
        ds = self.mocked_provider(db)

        callback = Mock(name="callback")
        ds.add_balance(1010, mock_currency(), 5, callback=callback)

        callback.assert_called_once_with(5)

        self._aoc(mck.find_and_modify,
                  {"_id": 1010},
                  {"$inc": {"counters.currency_TestCurrency": 5}},
                  fields={"counters.currency_TestCurrency": 1},
                  upsert=True, new=True)

    def test_deduct_balance(self):
        mck = self._find_mod_mck(_test_currency_mod_rtn(1010, 5))
        db = _simplemock("operant", "operant_users", mck)
        ds = self.mocked_provider(db)

        callback = Mock()

        ds.deduct_balance(1010, mock_currency(), 20, callback=callback)

        callback.assert_called_once(5)

        self._aoc(mck.find_and_modify,
                  {"_id": 1010},
                  {"$inc": {"counters.currency_TestCurrency": -20}},
                  fields={"counters.currency_TestCurrency": 1},
                  upsert=True, new=True)

    def test_get_balance(self):
        mck = self._find_mck(_test_currency_mod_rtn(1010, 5))
        db = _simplemock("operant", "operant_users", mck)
        ds = self.mocked_provider(db)

        callback = Mock()

        ds.get_balance(1010, mock_currency(), callback=callback)

        callback.assert_called_once(5)

        self._aoc(mck.find,
                  {'_id': 1010},
                  {'counters.currency_TestCurrency': 1})

    def test_add_badge(self):
        mck = self._find_mod_mck(_test_badge_mod_rtn(1010, "SomeRandomBadge"))
        db = _simplemock("operant", "operant_users", mck)
        ds = self.mocked_provider(db)

        callback = Mock()

        ds.add_badge(1010, mock_badge(), callback)

        callback.assert_called_once(True)

        self._aoc(mck.find_and_modify,
                  {'_id': 1010},
                  {'$addToSet': {'badges': "TestBadge"}},
                  fields={"badges": 1},
                  upsert=True, new=False)

    def test_add_badge_existing(self):
        mck = self._find_mod_mck(_test_badge_mod_rtn(1010, "TestBadge"))
        db = _simplemock("operant", "operant_users", mck)
        ds = self.mocked_provider(db)

        callback = Mock()

        ds.add_badge(1010, mock_badge(), callback)

        callback.assert_called_once(False)

        self._aoc(mck.find_and_modify,
                  {'_id': 1010},
                  {'$addToSet': {'badges': "TestBadge"}},
                  fields={"badges": 1},
                  upsert=True, new=False)

class TestPlainMongodb(CommonTests):
    client_class = "pymongo.Connection"

    def _aoc(self, fn, *args, **kwargs):
        fn.assert_called_once_with(*args, **kwargs)

    def mocked_provider(self, arg):
        return operant.storage.mongodb_plain.MongoDS(arg)

    def _find_mod_mck(self, res):
        mck = Mock(name="col:find_and_modify")
        mck.find_and_modify.return_value = res
        return mck

    def _find_mck(self, res):
        mck = Mock()
        mck.find.return_value = res
        return mck
