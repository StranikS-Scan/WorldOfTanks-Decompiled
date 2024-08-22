# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle/death_cam/hud_model.py
from frameworks.wulf import ViewModel

class HudModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(HudModel, self).__init__(properties=properties, commands=commands)

    def getBarsVisible(self):
        return self._getBool(0)

    def setBarsVisible(self, value):
        self._setBool(0, value)

    def getIsFinalPhase(self):
        return self._getBool(1)

    def setIsFinalPhase(self, value):
        self._setBool(1, value)

    def getRemainingTime(self):
        return self._getReal(2)

    def setRemainingTime(self, value):
        self._setReal(2, value)

    def _initialize(self):
        super(HudModel, self)._initialize()
        self._addBoolProperty('barsVisible', False)
        self._addBoolProperty('isFinalPhase', False)
        self._addRealProperty('remainingTime', 0.0)
