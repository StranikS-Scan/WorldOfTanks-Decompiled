# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/impl/gen/view_models/views/lobby/views/winback_reward_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel

class RewardWindowType(Enum):
    WELCOME = 'welcome'
    PROGRESSION_STEP = 'progressionStep'
    SELECTED_REWARDS = 'selectedRewards'
    PROGRESSION_COMPLETED = 'progressionCompleted'


class RewardName(Enum):
    VEHICLE_FOR_GIFT = 'vehicleForGift'
    VEHICLE_DISCOUNT = 'vehicleDiscount'
    VEHICLE_FOR_RENT = 'vehicleForRent'
    SELECTABLE_VEHICLE_FOR_GIFT = 'selectableVehicleForGift'
    SELECTABLE_VEHICLE_DISCOUNT = 'selectableVehicleDiscount'


class WinbackRewardViewModel(ViewModel):
    __slots__ = ('onSelectReward', 'onClose', 'showInHangar', 'showQuests')
    ARG_TOOLTIP_ID = 'tooltipId'

    def __init__(self, properties=5, commands=4):
        super(WinbackRewardViewModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return RewardWindowType(self._getString(0))

    def setState(self, value):
        self._setString(0, value.value)

    def getIsFirstProgressionStep(self):
        return self._getBool(1)

    def setIsFirstProgressionStep(self, value):
        self._setBool(1, value)

    def getRewards(self):
        return self._getArray(2)

    def setRewards(self, value):
        self._setArray(2, value)

    @staticmethod
    def getRewardsType():
        return ItemBonusModel

    def getStageNumber(self):
        return self._getNumber(3)

    def setStageNumber(self, value):
        self._setNumber(3, value)

    def getProgressionName(self):
        return self._getString(4)

    def setProgressionName(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(WinbackRewardViewModel, self)._initialize()
        self._addStringProperty('state')
        self._addBoolProperty('isFirstProgressionStep', False)
        self._addArrayProperty('rewards', Array())
        self._addNumberProperty('stageNumber', 0)
        self._addStringProperty('progressionName', '')
        self.onSelectReward = self._addCommand('onSelectReward')
        self.onClose = self._addCommand('onClose')
        self.showInHangar = self._addCommand('showInHangar')
        self.showQuests = self._addCommand('showQuests')
