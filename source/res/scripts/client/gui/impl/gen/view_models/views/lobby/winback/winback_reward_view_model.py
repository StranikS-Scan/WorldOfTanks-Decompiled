# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/winback/winback_reward_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel

class RewardWindowType(Enum):
    WELCOME = 'welcome'
    PROGRESSION_STEP = 'progressionStep'
    SELECTED_REWARDS = 'selectedRewards'
    WINBACK_PROGRESSION_COMPLETED = 'winbackProgressionCompleted'
    REGULAR_PROGRESSION_COMPLETED = 'regularProgressionCompleted'


class RewardName(Enum):
    VEHICLE_FOR_GIFT = 'vehicleForGift'
    VEHICLE_DISCOUNT = 'vehicleDiscount'
    VEHICLE_FOR_RENT = 'vehicleForRent'
    SELECTABLE_VEHICLE_FOR_GIFT = 'selectableVehicleForGift'
    SELECTABLE_VEHICLE_DISCOUNT = 'selectableVehicleDiscount'


class WinbackRewardViewModel(ViewModel):
    __slots__ = ('onSelectReward', 'onClose', 'showInHangar', 'showQuests')
    ARG_TOOLTIP_ID = 'tooltipId'

    def __init__(self, properties=4, commands=4):
        super(WinbackRewardViewModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return RewardWindowType(self._getString(0))

    def setState(self, value):
        self._setString(0, value.value)

    def getIsFirstProgressionStep(self):
        return self._getBool(1)

    def setIsFirstProgressionStep(self, value):
        self._setBool(1, value)

    def getIsSelectableAwardAvailable(self):
        return self._getBool(2)

    def setIsSelectableAwardAvailable(self, value):
        self._setBool(2, value)

    def getRewards(self):
        return self._getArray(3)

    def setRewards(self, value):
        self._setArray(3, value)

    @staticmethod
    def getRewardsType():
        return ItemBonusModel

    def _initialize(self):
        super(WinbackRewardViewModel, self)._initialize()
        self._addStringProperty('state')
        self._addBoolProperty('isFirstProgressionStep', False)
        self._addBoolProperty('isSelectableAwardAvailable', False)
        self._addArrayProperty('rewards', Array())
        self.onSelectReward = self._addCommand('onSelectReward')
        self.onClose = self._addCommand('onClose')
        self.showInHangar = self._addCommand('showInHangar')
        self.showQuests = self._addCommand('showQuests')
