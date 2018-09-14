# Embedded file name: scripts/common/Lib/xml/dom/minicompat.py
"""Python version compatibility support for minidom."""
__all__ = ['NodeList',
 'EmptyNodeList',
 'StringTypes',
 'defproperty']
import xml.dom
try:
    unicode
except NameError:
    StringTypes = (type(''),)
else:
    StringTypes = (type(''), type(unicode('')))

class NodeList(list):
    __slots__ = ()

    def item(self, index):
        if 0 <= index < len(self):
            return self[index]

    def _get_length(self):
        return len(self)

    def _set_length(self, value):
        raise xml.dom.NoModificationAllowedErr("attempt to modify read-only attribute 'length'")

    length = property(_get_length, _set_length, doc='The number of nodes in the NodeList.')

    def __getstate__(self):
        return list(self)

    def __setstate__(self, state):
        self[:] = state


class EmptyNodeList(tuple):
    __slots__ = ()

    def __add__(self, other):
        NL = NodeList()
        NL.extend(other)
        return NL

    def __radd__(self, other):
        NL = NodeList()
        NL.extend(other)
        return NL

    def item(self, index):
        return None

    def _get_length(self):
        return 0

    def _set_length(self, value):
        raise xml.dom.NoModificationAllowedErr("attempt to modify read-only attribute 'length'")

    length = property(_get_length, _set_length, doc='The number of nodes in the NodeList.')


def defproperty(klass, name, doc):
    get = getattr(klass, '_get_' + name).im_func

    def set(self, value, name = name):
        raise xml.dom.NoModificationAllowedErr('attempt to modify read-only attribute ' + repr(name))

    raise not hasattr(klass, '_set_' + name) or AssertionError('expected not to find _set_' + name)
    prop = property(get, set, doc=doc)
    setattr(klass, name, prop)
