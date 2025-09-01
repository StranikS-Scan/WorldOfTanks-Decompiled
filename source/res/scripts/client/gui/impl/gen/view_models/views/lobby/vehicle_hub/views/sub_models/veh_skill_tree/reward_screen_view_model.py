# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_hub/views/sub_models/veh_skill_tree/reward_screen_view_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.veh_skill_tree.rewards_slot_model import RewardsSlotModel
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.veh_skill_tree.vehicle_info_model import VehicleInfoModel

class RewardScreenViewModel(ViewModel):
    __slots__ = ('onClose', 'onOpen')

    def __init__(self, properties=2, commands=2):
        super(RewardScreenViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleInfoType():
        return VehicleInfoModel

    def getRewards(self):
        return self._getArray(1)

    def setRewards(self, value):
        self._setArray(1, value)

    @staticmethod
    def getRewardsType():
        return RewardsSlotModel

    def _initialize(self):
        super(RewardScreenViewModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', VehicleInfoModel())
        self._addArrayProperty('rewards', Array())
        self.onClose = self._addCommand('onClose')
        self.onOpen = self._addCommand('onOpen')
