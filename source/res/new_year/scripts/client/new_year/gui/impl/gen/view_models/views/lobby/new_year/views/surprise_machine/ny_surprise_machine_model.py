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
    __slots__ = ('onBuyBtnClick', 'onButtonPress', 'goToMachineMain', 'goToBuyTokens', 'goToQuest')

    def __init__(self, properties=7, commands=5):
        super(NySurpriseMachineModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleReward(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleRewardType():
        return VideoRewardViewModel

    def getCurrentAtmosphereLevel(self):
        return self._getNumber(1)

    def setCurrentAtmosphereLevel(self, value):
        self._setNumber(1, value)

    def getMachineViews(self):
        return MachineViews(self._getString(2))

    def setMachineViews(self, value):
        self._setString(2, value.value)

    def getPurchaseFormState(self):
        return PurchaseFormState(self._getString(3))

    def setPurchaseFormState(self, value):
        self._setString(3, value.value)

    def getExchangeRate(self):
        return self._getNumber(4)

    def setExchangeRate(self, value):
        self._setNumber(4, value)

    def getIsBtnHovered(self):
        return self._getBool(5)

    def setIsBtnHovered(self, value):
        self._setBool(5, value)

    def getIsBuyBtnLoading(self):
        return self._getBool(6)

    def setIsBuyBtnLoading(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(NySurpriseMachineModel, self)._initialize()
        self._addViewModelProperty('vehicleReward', VideoRewardViewModel())
        self._addNumberProperty('currentAtmosphereLevel', 9)
        self._addStringProperty('machineViews')
        self._addStringProperty('purchaseFormState')
        self._addNumberProperty('exchangeRate', 0)
        self._addBoolProperty('isBtnHovered', False)
        self._addBoolProperty('isBuyBtnLoading', False)
        self.onBuyBtnClick = self._addCommand('onBuyBtnClick')
        self.onButtonPress = self._addCommand('onButtonPress')
        self.goToMachineMain = self._addCommand('goToMachineMain')
        self.goToBuyTokens = self._addCommand('goToBuyTokens')
        self.goToQuest = self._addCommand('goToQuest')
