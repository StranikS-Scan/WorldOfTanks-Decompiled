# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/gen/view_models/views/lobby/battle_result.py
from frameworks.wulf import ViewModel

class BattleResult(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(BattleResult, self).__init__(properties=properties, commands=commands)

    def getBattles(self):
        return self._getNumber(0)

    def setBattles(self, value):
        self._setNumber(0, value)

    def getShot(self):
        return self._getNumber(1)

    def setShot(self, value):
        self._setNumber(1, value)

    def getRamming(self):
        return self._getNumber(2)

    def setRamming(self, value):
        self._setNumber(2, value)

    def getBoost(self):
        return self._getNumber(3)

    def setBoost(self, value):
        self._setNumber(3, value)

    def getShield(self):
        return self._getNumber(4)

    def setShield(self, value):
        self._setNumber(4, value)

    def getPowerImpulse(self):
        return self._getNumber(5)

    def setPowerImpulse(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(BattleResult, self)._initialize()
        self._addNumberProperty('battles', 0)
        self._addNumberProperty('shot', 0)
        self._addNumberProperty('ramming', 0)
        self._addNumberProperty('boost', 0)
        self._addNumberProperty('shield', 0)
        self._addNumberProperty('powerImpulse', 0)
