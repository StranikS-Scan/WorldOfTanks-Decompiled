# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/common/tankman_restore_info.py
from frameworks.wulf import ViewModel

class TankmanRestoreInfo(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(TankmanRestoreInfo, self).__init__(properties=properties, commands=commands)

    def getFreePeriod(self):
        return self._getNumber(0)

    def setFreePeriod(self, value):
        self._setNumber(0, value)

    def getPaidPeriod(self):
        return self._getNumber(1)

    def setPaidPeriod(self, value):
        self._setNumber(1, value)

    def getRecoverPrice(self):
        return self._getNumber(2)

    def setRecoverPrice(self, value):
        self._setNumber(2, value)

    def getMembersBuffer(self):
        return self._getNumber(3)

    def setMembersBuffer(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(TankmanRestoreInfo, self)._initialize()
        self._addNumberProperty('freePeriod', 0)
        self._addNumberProperty('paidPeriod', 0)
        self._addNumberProperty('recoverPrice', 0)
        self._addNumberProperty('membersBuffer', 0)
