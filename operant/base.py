""" Bases shared by the different gamification components"""

try:
    string_types = basestring
except NameError:
    # Python 3.x
    string_types = str


class Registry(object):
    """Class providing a collection of named objects.

       Components use which components use to register objects to
       indentifiers and provide smart regisration functions"""

    def __init__(self, kind, name_prop):
        self._kind = kind
        self._name_prop = name_prop
        self._spec = list()
        self._classes = dict()

    def _np_of(self, i):
        return getattr(i, self._name_prop)

    def set_handler(self, tp, fn):
        """ Setup a special handler for special types"""
        self._spec.append((tp, fn))

    def set_str_handler(self, fn):
        """ Setup a special handler for strings"""
        self.set_handler(string_types, fn)

    def _parse_with_handlers(self, obj):
        fns = [x for tps, fn in self._spec if isinstance(obj, tps)]
        out = obj
        for fn in fns:
            out = fn(obj)
        return out

    def register(self, toreg):
        """Registers an object to the registry"""
        toreg = self._parse_with_handlers(toreg)
        if self._np_of(toreg) in self._classes:
            raise RuntimeError("A {0} with the id {1} "
                               "has already been registered"
                               .format(self._kind, self._np_of(toreg)))
        self._classes[self._np_of(toreg)] = toreg

    def get(self, name):
        return self._classes.get(name, None)
