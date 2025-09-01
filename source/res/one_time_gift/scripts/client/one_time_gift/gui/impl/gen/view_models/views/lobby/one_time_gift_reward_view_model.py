# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/gui/impl/gen/view_models/views/lobby/one_time_gift_reward_view_model.py
from enum import Enum
from gui.impl.wrappers.user_list_model import UserListModel
from one_time_gift.gui.impl.gen.view_models.views.lobby.vehicle_bonus_model import VehicleBonusModel
from gui.impl.gen.view_models.views.lobby.common.awards_view_model import AwardsViewModel

class RewardType(Enum):
    BRANCH_REWARD = 'BranchReward'
    COLLECTORS_COMPENSATION_REWARD = 'CollectorsCompensationReward'
    BONUS_VEHICLES_REWARD = 'BonusVehiclesReward'
    ADDITIONAL_REWARD = 'AdditionalReward'


class OneTimeGiftRewardViewModel(AwardsViewModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=3):
        super(OneTimeGiftRewardViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleRewards(self):
        return self._getViewModel(9)

    @staticmethod
    def getVehicleRewardsType():
        return VehicleBonusModel

    def getRewardType(self):
        return RewardType(self._getString(10))

    def setRewardType(self, value):
        self._setString(10, value.value)

    def getBoxRewardsCount(self):
        return self._getNumber(11)

    def setBoxRewardsCount(self, value):
        self._setNumber(11, value)

    def _initialize(self):
        super(OneTimeGiftRewardViewModel, self)._initialize()
        self._addViewModelProperty('vehicleRewards', UserListModel())
        self._addStringProperty('rewardType')
        self._addNumberProperty('boxRewardsCount', 0)
