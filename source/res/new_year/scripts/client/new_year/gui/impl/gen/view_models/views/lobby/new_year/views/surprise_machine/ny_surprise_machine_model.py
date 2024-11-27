# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/surprise_machine/ny_surprise_machine_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.surprise_machine.video_reward_view_model import VideoRewardViewModel

class MachineViews(Enum):
    GET_TOKENS = 'getTokens'
    SPEND_TOKENS = 'spendTokens'
    SPEND_TOKENS_ACTIVE = 'spendTokensActive'


class PurchaseFormState(Enum):
    AVAILABLE = 'available'
    NOT_AVAILABLE = 'notAvailable'
    ERROR = 'error'


class NySurpriseMachineModel(ViewModel):
    __slots__ = ('onBuyBtnClick', 'onButtonPress', 'goToMachineMain', 'goToBuyTokens', 'goToQuest', 'onMouseOver3dScene', 'onMoveSpace')

    def __init__(self, properties=5, commands=7):
        super(NySurpriseMachineModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleReward(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleRewardType():
        return VideoRewardViewModel

    def getMachineViews(self):
        return MachineViews(self._getString(1))

    def setMachineViews(self, value):
        self._setString(1, value.value)

    def getPurchaseFormState(self):
        return PurchaseFormState(self._getString(2))

    def setPurchaseFormState(self, value):
        self._setString(2, value.value)

    def getExchangeRate(self):
        return self._getNumber(3)

    def setExchangeRate(self, value):
        self._setNumber(3, value)

    def getIsBtnHovered(self):
        return self._getBool(4)

    def setIsBtnHovered(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(NySurpriseMachineModel, self)._initialize()
        self._addViewModelProperty('vehicleReward', VideoRewardViewModel())
        self._addStringProperty('machineViews')
        self._addStringProperty('purchaseFormState')
        self._addNumberProperty('exchangeRate', 0)
        self._addBoolProperty('isBtnHovered', False)
        self.onBuyBtnClick = self._addCommand('onBuyBtnClick')
        self.onButtonPress = self._addCommand('onButtonPress')
        self.goToMachineMain = self._addCommand('goToMachineMain')
        self.goToBuyTokens = self._addCommand('goToBuyTokens')
        self.goToQuest = self._addCommand('goToQuest')
        self.onMouseOver3dScene = self._addCommand('onMouseOver3dScene')
        self.onMoveSpace = self._addCommand('onMoveSpace')
