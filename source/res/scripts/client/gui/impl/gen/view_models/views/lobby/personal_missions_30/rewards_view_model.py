# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions_30/rewards_view_model.py
from enum import Enum
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel

class RewardsViewType(Enum):
    VEHICLE_PART = 'vehiclePart'
    OPERATION_WITH_HONORS = 'operationWithHonors'
    CAMPAIGN_WITH_HONORS = 'campaignWithHonors'
    OPERATION = 'operation'


class RewardsViewModel(ViewModel):
    __slots__ = ('close', 'goToOperation', 'goToVehicle', 'disableVideoOverlaySound')
    ARG_REWARD_INDEX = 'tooltipId'

    def __init__(self, properties=8, commands=4):
        super(RewardsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicle(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleType():
        return VehicleInfoModel

    def getType(self):
        return RewardsViewType(self._getString(1))

    def setType(self, value):
        self._setString(1, value.value)

    def getRewards(self):
        return self._getArray(2)

    def setRewards(self, value):
        self._setArray(2, value)

    @staticmethod
    def getRewardsType():
        return IconBonusModel

    def getVehicleDetailName(self):
        return self._getString(3)

    def setVehicleDetailName(self, value):
        self._setString(3, value)

    def getCampaignName(self):
        return self._getString(4)

    def setCampaignName(self, value):
        self._setString(4, value)

    def getOperationName(self):
        return self._getString(5)

    def setOperationName(self, value):
        self._setString(5, value)

    def getNextOperationName(self):
        return self._getString(6)

    def setNextOperationName(self, value):
        self._setString(6, value)

    def getOperationId(self):
        return self._getNumber(7)

    def setOperationId(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(RewardsViewModel, self)._initialize()
        self._addViewModelProperty('vehicle', VehicleInfoModel())
        self._addStringProperty('type')
        self._addArrayProperty('rewards', Array())
        self._addStringProperty('vehicleDetailName', '')
        self._addStringProperty('campaignName', '')
        self._addStringProperty('operationName', '')
        self._addStringProperty('nextOperationName', '')
        self._addNumberProperty('operationId', 0)
        self.close = self._addCommand('close')
        self.goToOperation = self._addCommand('goToOperation')
        self.goToVehicle = self._addCommand('goToVehicle')
        self.disableVideoOverlaySound = self._addCommand('disableVideoOverlaySound')
