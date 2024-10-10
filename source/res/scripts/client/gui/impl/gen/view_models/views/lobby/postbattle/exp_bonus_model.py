# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/exp_bonus_model.py
from frameworks.wulf import ViewModel

class ExpBonusModel(ViewModel):
    __slots__ = ()
    IS_APPLIED = 1
    IS_NOT_VICTORY = 2
    DEPRECATED_RESULTS = 3
    NO_VEHICLE = 4
    NO_CREW = 5
    FASTER_EDUCATION_CREW_NOT_ACTIVE = 6
    FASTER_EDUCATION_CREW_ACTIVE = 7

    def __init__(self, properties=6, commands=0):
        super(ExpBonusModel, self).__init__(properties=properties, commands=commands)

    def getMaxBonusCount(self):
        return self._getNumber(0)

    def setMaxBonusCount(self, value):
        self._setNumber(0, value)

    def getUsedBonusCount(self):
        return self._getNumber(1)

    def setUsedBonusCount(self, value):
        self._setNumber(1, value)

    def getNextBonusTime(self):
        return self._getReal(2)

    def setNextBonusTime(self, value):
        self._setReal(2, value)

    def getBonusMultiplier(self):
        return self._getNumber(3)

    def setBonusMultiplier(self, value):
        self._setNumber(3, value)

    def getRestriction(self):
        return self._getNumber(4)

    def setRestriction(self, value):
        self._setNumber(4, value)

    def getIsEnabled(self):
        return self._getBool(5)

    def setIsEnabled(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(ExpBonusModel, self)._initialize()
        self._addNumberProperty('maxBonusCount', 0)
        self._addNumberProperty('usedBonusCount', 0)
        self._addRealProperty('nextBonusTime', 0.0)
        self._addNumberProperty('bonusMultiplier', 0)
        self._addNumberProperty('restriction', 0)
        self._addBoolProperty('isEnabled', False)
