# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/lootboxes_full_stats_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.lootbox_view_model import LootboxViewModel
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.statistic_reward_model import StatisticRewardModel

class LootboxesFullStatsViewModel(ViewModel):
    __slots__ = ('onClose', 'onSelectedLootBoxes', 'onVehiclePreview', 'onStylePreview')
    SELECT_LOOTBOXES_ARG_NAME = 'lootBoxesID'

    def __init__(self, properties=4, commands=4):
        super(LootboxesFullStatsViewModel, self).__init__(properties=properties, commands=commands)

    def getAllRewards(self):
        return self._getArray(0)

    def setAllRewards(self, value):
        self._setArray(0, value)

    @staticmethod
    def getAllRewardsType():
        return StatisticRewardModel

    def getLootboxes(self):
        return self._getArray(1)

    def setLootboxes(self, value):
        self._setArray(1, value)

    @staticmethod
    def getLootboxesType():
        return LootboxViewModel

    def getSelectedLootBoxes(self):
        return self._getArray(2)

    def setSelectedLootBoxes(self, value):
        self._setArray(2, value)

    @staticmethod
    def getSelectedLootBoxesType():
        return int

    def getCategory(self):
        return self._getString(3)

    def setCategory(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(LootboxesFullStatsViewModel, self)._initialize()
        self._addArrayProperty('allRewards', Array())
        self._addArrayProperty('lootboxes', Array())
        self._addArrayProperty('selectedLootBoxes', Array())
        self._addStringProperty('category', '')
        self.onClose = self._addCommand('onClose')
        self.onSelectedLootBoxes = self._addCommand('onSelectedLootBoxes')
        self.onVehiclePreview = self._addCommand('onVehiclePreview')
        self.onStylePreview = self._addCommand('onStylePreview')
