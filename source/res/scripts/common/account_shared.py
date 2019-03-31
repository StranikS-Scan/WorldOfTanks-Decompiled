# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/account_shared.py
# Compiled at: 2011-01-13 17:31:45
import collections

class AmmoIterator(object):

    def __init__(self, ammo):
        self.__ammo = ammo
        self.__idx = 0

    def __iter__(self):
        return self

    def next(self):
        if self.__idx >= len(self.__ammo):
            raise StopIteration
        idx = self.__idx
        self.__idx += 2
        return (self.__ammo[idx], self.__ammo[idx + 1])


def getAmmoDiff(ammo1, ammo2):
    diff = collections.defaultdict(int)
    for compDescr, count in AmmoIterator(ammo1):
        diff[compDescr] += count

    for compDescr, count in AmmoIterator(ammo2):
        diff[compDescr] -= count

    return diff


def getEquipmentsDiff(eqs1, eqs2):
    diff = collections.defaultdict(int)
    for eqCompDescr in eqs1:
        if eqCompDescr != 0:
            diff[eqCompDescr] += 1

    for eqCompDescr in eqs2:
        if eqCompDescr != 0:
            diff[eqCompDescr] -= 1

    return diff
