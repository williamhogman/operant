try:
    from mock import Mock, patch, ANY, sentinel
except ImportError:
    from unittest.mock import Mock, patch, ANY, sentinel

from nose.tools import ok_, eq_, raises

from operant.base import Registry


class RegObject(object):
    def __init__(self, name):
        self.name = name


class TestRegistry(object):

    @property
    def _reg(self):
        return Registry("testing", "name")

    @raises(RuntimeError)
    def test_register_existing(self):
        a = RegObject("foo")
        b = RegObject("foo")
        reg = self._reg
        reg.register(a)
        # This line should raise
        reg.register(b)

    def test_register(self):
        reg = self._reg
        a = RegObject("bar")
        reg.register(a)
        eq_(reg.get("bar"), a)

    def test_get_none(self):
        eq_(self._reg.get("__not__valid__"), None)

    def _handler_res(self):
        m = Mock()
        m.name = "handler_res"
        return m

    def test_str_handler(self):
        reg = self._reg

        res = self._handler_res()
        handler = Mock(return_value=res)

        reg.set_str_handler(handler)

        reg.register("whatever")
        handler.assert_called_once_with("whatever")
        eq_(reg.get("handler_res"), res)

    def test_cust_handler(self):
        reg = self._reg

        res = self._handler_res()
        handler = Mock(return_value=res)

        class Foo(object):
            name = "Foo"
        reg.set_handler(Foo, handler)

        foo = Foo()
        reg.register(foo)

        handler.assert_called_once_with(foo)
        eq_(reg.get("handler_res"), res)
