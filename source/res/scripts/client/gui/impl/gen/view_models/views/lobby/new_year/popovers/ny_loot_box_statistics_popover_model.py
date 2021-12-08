# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/popovers/ny_loot_box_statistics_popover_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.popovers.ny_loot_box_statistics_reward_model import NyLootBoxStatisticsRewardModel

class NyLootBoxStatisticsPopoverModel(ViewModel):
    __slots__ = ('onResetClick', 'onClose')

    def __init__(self, properties=3, commands=2):
        super(NyLootBoxStatisticsPopoverModel, self).__init__(properties=properties, commands=commands)

    def getCount(self):
        return self._getNumber(0)

    def setCount(self, value):
        self._setNumber(0, value)

    def getIsResetFailed(self):
        return self._getBool(1)

    def setIsResetFailed(self, value):
        self._setBool(1, value)

    def getRewards(self):
        return self._getArray(2)

    def setRewards(self, value):
        self._setArray(2, value)

    def _initialize(self):
        super(NyLootBoxStatisticsPopoverModel, self)._initialize()
        self._addNumberProperty('count', 0)
        self._addBoolProperty('isResetFailed', False)
        self._addArrayProperty('rewards', Array())
        self.onResetClick = self._addCommand('onResetClick')
        self.onClose = self._addCommand('onClose')
