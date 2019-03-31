# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/idlelib/Delegator.py
# Compiled at: 2010-05-25 20:46:16


class Delegator:

    def __init__(self, delegate=None):
        self.delegate = delegate
        self.__cache = {}

    def __getattr__(self, name):
        attr = getattr(self.delegate, name)
        setattr(self, name, attr)
        self.__cache[name] = attr
        return attr

    def resetcache(self):
        for key in self.__cache.keys():
            try:
                delattr(self, key)
            except AttributeError:
                pass

        self.__cache.clear()

    def cachereport(self):
        keys = self.__cache.keys()
        keys.sort()
        print keys

    def setdelegate(self, delegate):
        self.resetcache()
        self.delegate = delegate

    def getdelegate(self):
        return self.delegate
