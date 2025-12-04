# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/gen/view_models/views/lobby/feature/armory_yard_level_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_rewards_vehicle_model import ArmoryYardRewardsVehicleModel

class RewardType(Enum):
    COMMON = 'common'
    PROGRESSION = 'progression'
    POSTPROGRESSION = 'postProgression'


class ArmoryYardLevelModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(ArmoryYardLevelModel, self).__init__(properties=properties, commands=commands)

    def getLevel(self):
        return self._getNumber(0)

    def setLevel(self, value):
        self._setNumber(0, value)

    def getRewardType(self):
        return RewardType(self._getString(1))

    def setRewardType(self, value):
        self._setString(1, value.value)

    def getRewards(self):
        return self._getArray(2)

    def setRewards(self, value):
        self._setArray(2, value)

    @staticmethod
    def getRewardsType():
        return ArmoryYardRewardsVehicleModel

    def _initialize(self):
        super(ArmoryYardLevelModel, self)._initialize()
        self._addNumberProperty('level', 0)
        self._addStringProperty('rewardType', RewardType.COMMON.value)
        self._addArrayProperty('rewards', Array())
