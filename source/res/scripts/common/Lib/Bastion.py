# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/Bastion.py
from warnings import warnpy3k
warnpy3k('the Bastion module has been removed in Python 3.0', stacklevel=2)
del warnpy3k
__all__ = ['BastionClass', 'Bastion']
from types import MethodType

class BastionClass:

    def __init__(self, get, name):
        self._get_ = get
        self._name_ = name

    def __repr__(self):
        return '<Bastion for %s>' % self._name_

    def __getattr__(self, name):
        attribute = self._get_(name)
        self.__dict__[name] = attribute
        return attribute


def Bastion(object, filter=lambda name: name[:1] != '_', name=None, bastionclass=BastionClass):
    raise RuntimeError, 'This code is not secure in Python 2.2 and later'

    def get1(name, object=object, filter=filter):
        if filter(name):
            attribute = getattr(object, name)
            if type(attribute) == MethodType:
                return attribute
        raise AttributeError, name

    def get2(name, get1=get1):
        return get1(name)

    if name is None:
        name = repr(object)
    return bastionclass(get2, name)


def _test():

    class Original:

        def __init__(self):
            self.sum = 0

        def add(self, n):
            self._add(n)

        def _add(self, n):
            self.sum = self.sum + n

        def total(self):
            return self.sum

    o = Original()
    b = Bastion(o)
    testcode = 'if 1:\n    b.add(81)\n    b.add(18)\n    print "b.total() =", b.total()\n    try:\n        print "b.sum =", b.sum,\n    except:\n        print "inaccessible"\n    else:\n        print "accessible"\n    try:\n        print "b._add =", b._add,\n    except:\n        print "inaccessible"\n    else:\n        print "accessible"\n    try:\n        print "b._get_.func_defaults =", map(type, b._get_.func_defaults),\n    except:\n        print "inaccessible"\n    else:\n        print "accessible"\n    \n'
    exec testcode
    print '====================', 'Using rexec:', '===================='
    import rexec
    r = rexec.RExec()
    m = r.add_module('__main__')
    m.b = b
    r.r_exec(testcode)


if __name__ == '__main__':
    _test()
