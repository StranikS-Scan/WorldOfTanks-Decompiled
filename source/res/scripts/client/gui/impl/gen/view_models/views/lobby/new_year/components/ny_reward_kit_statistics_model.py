# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/ny_reward_kit_statistics_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_resource_model import NyResourceModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_reward_kit_statistics_reward_model import NyRewardKitStatisticsRewardModel

class NyRewardKitStatisticsModel(ViewModel):
    __slots__ = ('onResetStatistics', 'onUpdateLastSeen')

    def __init__(self, properties=5, commands=2):
        super(NyRewardKitStatisticsModel, self).__init__(properties=properties, commands=commands)

    def getCount(self):
        return self._getNumber(0)

    def setCount(self, value):
        self._setNumber(0, value)

    def getTotalResourcesCount(self):
        return self._getNumber(1)

    def setTotalResourcesCount(self, value):
        self._setNumber(1, value)

    def getIsResetFailed(self):
        return self._getBool(2)

    def setIsResetFailed(self, value):
        self._setBool(2, value)

    def getRewards(self):
        return self._getArray(3)

    def setRewards(self, value):
        self._setArray(3, value)

    @staticmethod
    def getRewardsType():
        return NyRewardKitStatisticsRewardModel

    def getResources(self):
        return self._getArray(4)

    def setResources(self, value):
        self._setArray(4, value)

    @staticmethod
    def getResourcesType():
        return NyResourceModel

    def _initialize(self):
        super(NyRewardKitStatisticsModel, self)._initialize()
        self._addNumberProperty('count', 0)
        self._addNumberProperty('totalResourcesCount', 0)
        self._addBoolProperty('isResetFailed', False)
        self._addArrayProperty('rewards', Array())
        self._addArrayProperty('resources', Array())
        self.onResetStatistics = self._addCommand('onResetStatistics')
        self.onUpdateLastSeen = self._addCommand('onUpdateLastSeen')
