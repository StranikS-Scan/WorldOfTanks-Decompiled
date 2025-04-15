# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/impl/gen/view_models/views/lobby/tooltips/reward_info_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class RewardState(Enum):
    AVAILABLE = 'AVAILABLE'
    RECEIVED = 'RECEIVED'
    IN_GARAGE = 'IN_GARAGE'
    SOLD_OUT = 'SOLD_OUT'


class RewardInfoModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(RewardInfoModel, self).__init__(properties=properties, commands=commands)

    def getVehicleName(self):
        return self._getString(0)

    def setVehicleName(self, value):
        self._setString(0, value)

    def getRewardCount(self):
        return self._getNumber(1)

    def setRewardCount(self, value):
        self._setNumber(1, value)

    def getIsSerial(self):
        return self._getBool(2)

    def setIsSerial(self, value):
        self._setBool(2, value)

    def getRewardState(self):
        return RewardState(self._getString(3))

    def setRewardState(self, value):
        self._setString(3, value.value)

    def _initialize(self):
        super(RewardInfoModel, self)._initialize()
        self._addStringProperty('vehicleName', '')
        self._addNumberProperty('rewardCount', 0)
        self._addBoolProperty('isSerial', False)
        self._addStringProperty('rewardState')
