# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/gen/view_models/views/lobby/feature/armory_yard_buy_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel
from gui.impl.gen.view_models.common.price_model import PriceModel
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_buy_step_config import ArmoryYardBuyStepConfig
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_rewards_vehicle_model import ArmoryYardRewardsVehicleModel

class ParentAlias(Enum):
    MAINVIEW = 'mainView'
    VEHICLEPREVIEW = 'vehiclePreview'


class ArmoryYardBuyViewModel(ViewModel):
    __slots__ = ('onChangeSelectedStep', 'onBuySteps', 'onCancel', 'onBack', 'onShowVehiclePreview')
    STEP_VEHICLE_TOOLTIP_TYPE = 'stepVehicle'
    FINAL_REWARD_TOOLTIP_TYPE = 'finalReward'
    MERGED_REWARD_TOOLTIP_TYPE = 'mergedReward'
    MAX_VISIBLE_REWARDS = 10

    def __init__(self, properties=9, commands=5):
        super(ArmoryYardBuyViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def finalReward(self):
        return self._getViewModel(0)

    @staticmethod
    def getFinalRewardType():
        return ArmoryYardRewardsVehicleModel

    @property
    def price(self):
        return self._getViewModel(1)

    @staticmethod
    def getPriceType():
        return PriceModel

    def getStepSelected(self):
        return self._getNumber(2)

    def setStepSelected(self, value):
        self._setNumber(2, value)

    def getStepsPassed(self):
        return self._getNumber(3)

    def setStepsPassed(self, value):
        self._setNumber(3, value)

    def getParentAlias(self):
        return ParentAlias(self._getString(4))

    def setParentAlias(self, value):
        self._setString(4, value.value)

    def getRewards(self):
        return self._getArray(5)

    def setRewards(self, value):
        self._setArray(5, value)

    @staticmethod
    def getRewardsType():
        return ItemBonusModel

    def getSteps(self):
        return self._getArray(6)

    def setSteps(self, value):
        self._setArray(6, value)

    @staticmethod
    def getStepsType():
        return ArmoryYardBuyStepConfig

    def getIsWalletAvailable(self):
        return self._getBool(7)

    def setIsWalletAvailable(self, value):
        self._setBool(7, value)

    def getIsBlurEnabled(self):
        return self._getBool(8)

    def setIsBlurEnabled(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(ArmoryYardBuyViewModel, self)._initialize()
        self._addViewModelProperty('finalReward', ArmoryYardRewardsVehicleModel())
        self._addViewModelProperty('price', PriceModel())
        self._addNumberProperty('stepSelected', 0)
        self._addNumberProperty('stepsPassed', 0)
        self._addStringProperty('parentAlias')
        self._addArrayProperty('rewards', Array())
        self._addArrayProperty('steps', Array())
        self._addBoolProperty('isWalletAvailable', True)
        self._addBoolProperty('isBlurEnabled', False)
        self.onChangeSelectedStep = self._addCommand('onChangeSelectedStep')
        self.onBuySteps = self._addCommand('onBuySteps')
        self.onCancel = self._addCommand('onCancel')
        self.onBack = self._addCommand('onBack')
        self.onShowVehiclePreview = self._addCommand('onShowVehiclePreview')
