# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/gift_machine/gift_machine_reward_item_model.py
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel
from gui.impl.gen.view_models.views.lobby.new_year.components.reward_item_model import RewardItemModel

class GiftMachineRewardItemModel(RewardItemModel):
    __slots__ = ()

    def __init__(self, properties=17, commands=0):
        super(GiftMachineRewardItemModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleInfo(self):
        return self._getViewModel(14)

    @staticmethod
    def getVehicleInfoType():
        return VehicleInfoModel

    def getRentDays(self):
        return self._getNumber(15)

    def setRentDays(self, value):
        self._setNumber(15, value)

    def getRentBattles(self):
        return self._getNumber(16)

    def setRentBattles(self, value):
        self._setNumber(16, value)

    def _initialize(self):
        super(GiftMachineRewardItemModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', VehicleInfoModel())
        self._addNumberProperty('rentDays', 0)
        self._addNumberProperty('rentBattles', 0)
