# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/ranked/ranked_year_award_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class RankedYearAwardModel(ViewModel):
    __slots__ = ('onActionBtnClick', 'onDestroyEvent')

    def __init__(self, properties=7, commands=2):
        super(RankedYearAwardModel, self).__init__(properties=properties, commands=commands)

    def getAwardType(self):
        return self._getString(0)

    def setAwardType(self, value):
        self._setString(0, value)

    def getStartClose(self):
        return self._getBool(1)

    def setStartClose(self, value):
        self._setBool(1, value)

    def getRewards(self):
        return self._getArray(2)

    def setRewards(self, value):
        self._setArray(2, value)

    def getActionButtonLabel(self):
        return self._getResource(3)

    def setActionButtonLabel(self, value):
        self._setResource(3, value)

    def getPointsTotal(self):
        return self._getNumber(4)

    def setPointsTotal(self, value):
        self._setNumber(4, value)

    def getPointsCompensated(self):
        return self._getNumber(5)

    def setPointsCompensated(self, value):
        self._setNumber(5, value)

    def getCrystals(self):
        return self._getNumber(6)

    def setCrystals(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(RankedYearAwardModel, self)._initialize()
        self._addStringProperty('awardType', '')
        self._addBoolProperty('startClose', False)
        self._addArrayProperty('rewards', Array())
        self._addResourceProperty('actionButtonLabel', R.invalid())
        self._addNumberProperty('pointsTotal', 0)
        self._addNumberProperty('pointsCompensated', 0)
        self._addNumberProperty('crystals', 0)
        self.onActionBtnClick = self._addCommand('onActionBtnClick')
        self.onDestroyEvent = self._addCommand('onDestroyEvent')
