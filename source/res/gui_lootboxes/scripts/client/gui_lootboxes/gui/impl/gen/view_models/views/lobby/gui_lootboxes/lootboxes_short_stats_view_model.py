# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/lootboxes_short_stats_view_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.statistic_reward_model import StatisticRewardModel

class TabState(IntEnum):
    SINGLE = 0
    ALL = 1


class LootboxesShortStatsViewModel(ViewModel):
    __slots__ = ('onCloseStat', 'onOpenFullStats', 'onTabSwitch', 'onVehiclePreview')

    def __init__(self, properties=7, commands=4):
        super(LootboxesShortStatsViewModel, self).__init__(properties=properties, commands=commands)

    def getCurrentTab(self):
        return TabState(self._getNumber(0))

    def setCurrentTab(self, value):
        self._setNumber(0, value.value)

    def getCurrentRewards(self):
        return self._getArray(1)

    def setCurrentRewards(self, value):
        self._setArray(1, value)

    @staticmethod
    def getCurrentRewardsType():
        return StatisticRewardModel

    def getAllRewards(self):
        return self._getArray(2)

    def setAllRewards(self, value):
        self._setArray(2, value)

    @staticmethod
    def getAllRewardsType():
        return StatisticRewardModel

    def getIsLoading(self):
        return self._getBool(3)

    def setIsLoading(self, value):
        self._setBool(3, value)

    def getLootBoxName(self):
        return self._getString(4)

    def setLootBoxName(self, value):
        self._setString(4, value)

    def getIsShown(self):
        return self._getBool(5)

    def setIsShown(self, value):
        self._setBool(5, value)

    def getHasVisibleLootBoxes(self):
        return self._getBool(6)

    def setHasVisibleLootBoxes(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(LootboxesShortStatsViewModel, self)._initialize()
        self._addNumberProperty('currentTab')
        self._addArrayProperty('currentRewards', Array())
        self._addArrayProperty('allRewards', Array())
        self._addBoolProperty('isLoading', True)
        self._addStringProperty('lootBoxName', '')
        self._addBoolProperty('isShown', False)
        self._addBoolProperty('hasVisibleLootBoxes', False)
        self.onCloseStat = self._addCommand('onCloseStat')
        self.onOpenFullStats = self._addCommand('onOpenFullStats')
        self.onTabSwitch = self._addCommand('onTabSwitch')
        self.onVehiclePreview = self._addCommand('onVehiclePreview')
