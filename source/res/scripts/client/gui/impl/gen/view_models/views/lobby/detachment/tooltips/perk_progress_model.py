# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/tooltips/perk_progress_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class PerkProgressModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(PerkProgressModel, self).__init__(properties=properties, commands=commands)

    def getVehParamName(self):
        return self._getResource(0)

    def setVehParamName(self, value):
        self._setResource(0, value)

    def getLevel(self):
        return self._getNumber(1)

    def setLevel(self, value):
        self._setNumber(1, value)

    def getPoints(self):
        return self._getNumber(2)

    def setPoints(self, value):
        self._setNumber(2, value)

    def getMaxPoints(self):
        return self._getNumber(3)

    def setMaxPoints(self, value):
        self._setNumber(3, value)

    def getBonusPoints(self):
        return self._getNumber(4)

    def setBonusPoints(self, value):
        self._setNumber(4, value)

    def getMarkPoints(self):
        return self._getNumber(5)

    def setMarkPoints(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(PerkProgressModel, self)._initialize()
        self._addResourceProperty('vehParamName', R.invalid())
        self._addNumberProperty('level', 0)
        self._addNumberProperty('points', 0)
        self._addNumberProperty('maxPoints', 0)
        self._addNumberProperty('bonusPoints', 0)
        self._addNumberProperty('markPoints', 0)
