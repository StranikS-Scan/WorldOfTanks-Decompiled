# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/seniority_awards/seniority_awards_vehicles_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.seniority_awards.seniority_awards_vehicle_model import SeniorityAwardsVehicleModel

class ViewState(Enum):
    SELECTION = 'selection'
    VIEW_REWARD_AFTER_SELECTION = 'viewRewardAfterSelection'
    VIEW_REWARD = 'viewReward'


class SeniorityAwardsVehiclesViewModel(ViewModel):
    __slots__ = ('onMoreRewards', 'onGoToHangar', 'onClose', 'onSelectVehicleReward')

    def __init__(self, properties=5, commands=4):
        super(SeniorityAwardsVehiclesViewModel, self).__init__(properties=properties, commands=commands)

    def getCategory(self):
        return self._getString(0)

    def setCategory(self, value):
        self._setString(0, value)

    def getFromEntryPoint(self):
        return self._getBool(1)

    def setFromEntryPoint(self, value):
        self._setBool(1, value)

    def getVehicles(self):
        return self._getArray(2)

    def setVehicles(self, value):
        self._setArray(2, value)

    @staticmethod
    def getVehiclesType():
        return SeniorityAwardsVehicleModel

    def getViewState(self):
        return ViewState(self._getString(3))

    def setViewState(self, value):
        self._setString(3, value.value)

    def getAvailableRewardsCount(self):
        return self._getNumber(4)

    def setAvailableRewardsCount(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(SeniorityAwardsVehiclesViewModel, self)._initialize()
        self._addStringProperty('category', '')
        self._addBoolProperty('fromEntryPoint', False)
        self._addArrayProperty('vehicles', Array())
        self._addStringProperty('viewState', ViewState.VIEW_REWARD.value)
        self._addNumberProperty('availableRewardsCount', 0)
        self.onMoreRewards = self._addCommand('onMoreRewards')
        self.onGoToHangar = self._addCommand('onGoToHangar')
        self.onClose = self._addCommand('onClose')
        self.onSelectVehicleReward = self._addCommand('onSelectVehicleReward')
