# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenter/getter/common.py
from copy import deepcopy

class _Copyable(object):

    def copy(self, **kwargs):
        other = deepcopy(self)
        for k, v in kwargs.iteritems():
            setattr(other, k, v)

        return other


class Field(_Copyable):
    __slots__ = ('__stringID',)

    def __init__(self, stringID):
        self.__stringID = stringID

    @property
    def stringID(self):
        return self.__stringID

    @stringID.setter
    def stringID(self, value):
        self.__stringID = value

    def getFieldValues(self, *args):
        raise NotImplementedError

    def _getRecord(self, *args):
        raise NotImplementedError

    def _getValue(self, *args):
        raise NotImplementedError
