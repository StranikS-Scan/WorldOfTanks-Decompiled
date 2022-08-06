# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_matters/tooltips/battle_matters_entry_tooltip_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel

class BattleMattersEntryTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(BattleMattersEntryTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getString(0)

    def setTitle(self, value):
        self._setString(0, value)

    def getCondition(self):
        return self._getString(1)

    def setCondition(self, value):
        self._setString(1, value)

    def getHasToken(self):
        return self._getBool(2)

    def setHasToken(self, value):
        self._setBool(2, value)

    def getIsPaused(self):
        return self._getBool(3)

    def setIsPaused(self, value):
        self._setBool(3, value)

    def getCurrentProgress(self):
        return self._getNumber(4)

    def setCurrentProgress(self, value):
        self._setNumber(4, value)

    def getMaxProgress(self):
        return self._getNumber(5)

    def setMaxProgress(self, value):
        self._setNumber(5, value)

    def getCurrentQuest(self):
        return self._getNumber(6)

    def setCurrentQuest(self, value):
        self._setNumber(6, value)

    def getQuestsCount(self):
        return self._getNumber(7)

    def setQuestsCount(self, value):
        self._setNumber(7, value)

    def getEndDate(self):
        return self._getNumber(8)

    def setEndDate(self, value):
        self._setNumber(8, value)

    def getRewards(self):
        return self._getArray(9)

    def setRewards(self, value):
        self._setArray(9, value)

    @staticmethod
    def getRewardsType():
        return ItemBonusModel

    def _initialize(self):
        super(BattleMattersEntryTooltipViewModel, self)._initialize()
        self._addStringProperty('title', '')
        self._addStringProperty('condition', '')
        self._addBoolProperty('hasToken', False)
        self._addBoolProperty('isPaused', False)
        self._addNumberProperty('currentProgress', 0)
        self._addNumberProperty('maxProgress', 0)
        self._addNumberProperty('currentQuest', 0)
        self._addNumberProperty('questsCount', 0)
        self._addNumberProperty('endDate', 0)
        self._addArrayProperty('rewards', Array())
