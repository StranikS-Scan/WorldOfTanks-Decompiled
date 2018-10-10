# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/functools.py
from _functools import partial, reduce
WRAPPER_ASSIGNMENTS = ('__module__', '__name__', '__doc__')
WRAPPER_UPDATES = ('__dict__',)

def update_wrapper(wrapper, wrapped, assigned=WRAPPER_ASSIGNMENTS, updated=WRAPPER_UPDATES):
    for attr in assigned:
        setattr(wrapper, attr, getattr(wrapped, attr))

    for attr in updated:
        getattr(wrapper, attr).update(getattr(wrapped, attr, {}))

    return wrapper


def wraps(wrapped, assigned=WRAPPER_ASSIGNMENTS, updated=WRAPPER_UPDATES):
    return partial(update_wrapper, wrapped=wrapped, assigned=assigned, updated=updated)


def total_ordering(cls):
    convert = {'__lt__': [('__gt__', lambda self, other: not (self < other or self == other)), ('__le__', lambda self, other: self < other or self == other), ('__ge__', lambda self, other: not self < other)],
     '__le__': [('__ge__', lambda self, other: not self <= other or self == other), ('__lt__', lambda self, other: self <= other and not self == other), ('__gt__', lambda self, other: not self <= other)],
     '__gt__': [('__lt__', lambda self, other: not (self > other or self == other)), ('__ge__', lambda self, other: self > other or self == other), ('__le__', lambda self, other: not self > other)],
     '__ge__': [('__le__', lambda self, other: not self >= other or self == other), ('__gt__', lambda self, other: self >= other and not self == other), ('__lt__', lambda self, other: not self >= other)]}
    roots = set(dir(cls)) & set(convert)
    if not roots:
        raise ValueError('must define at least one ordering operation: < > <= >=')
    root = max(roots)
    for opname, opfunc in convert[root]:
        if opname not in roots:
            opfunc.__name__ = opname
            opfunc.__doc__ = getattr(int, opname).__doc__
            setattr(cls, opname, opfunc)

    return cls


def cmp_to_key(mycmp):

    class K(object):
        __slots__ = ['obj']

        def __init__(self, obj, *args):
            self.obj = obj

        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0

        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0

        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0

        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0

        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0

        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0

        def __hash__(self):
            raise TypeError('hash not implemented')

    return K
