# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/gift_system/progression_stage_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class ProgressionStageModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(ProgressionStageModel, self).__init__(properties=properties, commands=commands)

    def getCurrentCoinsCount(self):
        return self._getNumber(0)

    def setCurrentCoinsCount(self, value):
        self._setNumber(0, value)

    def getMaxCoinsCount(self):
        return self._getNumber(1)

    def setMaxCoinsCount(self, value):
        self._setNumber(1, value)

    def getStyleIDs(self):
        return self._getArray(2)

    def setStyleIDs(self, value):
        self._setArray(2, value)

    def getRewards(self):
        return self._getArray(3)

    def setRewards(self, value):
        self._setArray(3, value)

    def _initialize(self):
        super(ProgressionStageModel, self)._initialize()
        self._addNumberProperty('currentCoinsCount', 0)
        self._addNumberProperty('maxCoinsCount', 0)
        self._addArrayProperty('styleIDs', Array())
        self._addArrayProperty('rewards', Array())
