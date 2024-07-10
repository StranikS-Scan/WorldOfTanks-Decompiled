# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/gen/view_models/views/lobby/feature/battle_results/fun_random_progress_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel

class FunRandomProgressModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=0):
        super(FunRandomProgressModel, self).__init__(properties=properties, commands=commands)

    def getHasProgress(self):
        return self._getBool(0)

    def setHasProgress(self, value):
        self._setBool(0, value)

    def getAssetsPointer(self):
        return self._getString(1)

    def setAssetsPointer(self, value):
        self._setString(1, value)

    def getDescription(self):
        return self._getString(2)

    def setDescription(self, value):
        self._setString(2, value)

    def getIsInUnlimitedProgression(self):
        return self._getBool(3)

    def setIsInUnlimitedProgression(self, value):
        self._setBool(3, value)

    def getPreviousStage(self):
        return self._getNumber(4)

    def setPreviousStage(self, value):
        self._setNumber(4, value)

    def getCurrentStage(self):
        return self._getNumber(5)

    def setCurrentStage(self, value):
        self._setNumber(5, value)

    def getMaximumStage(self):
        return self._getNumber(6)

    def setMaximumStage(self, value):
        self._setNumber(6, value)

    def getPreviousPoints(self):
        return self._getNumber(7)

    def setPreviousPoints(self, value):
        self._setNumber(7, value)

    def getEarnedPoints(self):
        return self._getNumber(8)

    def setEarnedPoints(self, value):
        self._setNumber(8, value)

    def getCurrentPoints(self):
        return self._getNumber(9)

    def setCurrentPoints(self, value):
        self._setNumber(9, value)

    def getMaximumPoints(self):
        return self._getNumber(10)

    def setMaximumPoints(self, value):
        self._setNumber(10, value)

    def getRewards(self):
        return self._getArray(11)

    def setRewards(self, value):
        self._setArray(11, value)

    @staticmethod
    def getRewardsType():
        return ItemBonusModel

    def _initialize(self):
        super(FunRandomProgressModel, self)._initialize()
        self._addBoolProperty('hasProgress', False)
        self._addStringProperty('assetsPointer', 'undefined')
        self._addStringProperty('description', '')
        self._addBoolProperty('isInUnlimitedProgression', False)
        self._addNumberProperty('previousStage', -1)
        self._addNumberProperty('currentStage', -1)
        self._addNumberProperty('maximumStage', -1)
        self._addNumberProperty('previousPoints', -1)
        self._addNumberProperty('earnedPoints', -1)
        self._addNumberProperty('currentPoints', -1)
        self._addNumberProperty('maximumPoints', -1)
        self._addArrayProperty('rewards', Array())
