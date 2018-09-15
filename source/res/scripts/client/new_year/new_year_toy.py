# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/new_year_toy.py


class ToyItemInfo(object):

    def __init__(self, item, count=1, newCount=0):
        self.__count = count
        self.__item = item
        self.__newCount = newCount

    def __getattr__(self, name):
        attr = getattr(self.__item, name, None)
        if attr is None:
            raise AttributeError
        return attr

    @property
    def count(self):
        return self.__count

    @count.setter
    def count(self, value):
        self.__count = value

    @property
    def newCount(self):
        return self.__newCount

    @newCount.setter
    def newCount(self, value):
        self.__newCount = value

    @property
    def item(self):
        return self.__item
