# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/gift_machine/ny_gift_machine_view_model.py
from enum import Enum
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_resource_model import NyResourceModel
from gui.impl.gen.view_models.views.lobby.new_year.views.base.ny_scene_rotatable_view import NySceneRotatableView
from gui.impl.gen.view_models.views.lobby.new_year.views.gift_machine.gift_machine_vehicle_preview_model import GiftMachineVehiclePreviewModel

class MachineState(Enum):
    IDLE = 'idle'
    REWARD = 'reward'
    REWARDPREQUEL = 'rewardPrequel'
    SPECIALREWARD = 'specialReward'
    SPECIALREWARDPREQUEL = 'specialRewardPrequel'
    SPECIALREWARDPREVIEW = 'specialRewardPreview'
    SKIPREWARDPREQUEL = 'skipRewardPrequel'
    SKIPSPECIALREWARDPREQUEL = 'skipSpecialRewardPrequel'
    ERROR = 'error'
    BUYTOKENS = 'buyTokens'


class NyGiftMachineViewModel(NySceneRotatableView):
    __slots__ = ('onGoToBuyTokens', 'onGoToIdle', 'onSkipAnimation', 'onBuyTokens', 'onGoToGlade', 'onGoToChallengeGuestA', 'onGoToChallengeGuestM', 'onGoToChallenge', 'onCloseInfoBlock', 'onBackFromVehiclePreview', 'onGoToHangar')

    def __init__(self, properties=15, commands=13):
        super(NyGiftMachineViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehiclePreview(self):
        return self._getViewModel(1)

    @staticmethod
    def getVehiclePreviewType():
        return GiftMachineVehiclePreviewModel

    def getIsInSquad(self):
        return self._getBool(2)

    def setIsInSquad(self, value):
        self._setBool(2, value)

    def getMachineState(self):
        return MachineState(self._getString(3))

    def setMachineState(self, value):
        self._setString(3, value.value)

    def getTokenCount(self):
        return self._getNumber(4)

    def setTokenCount(self, value):
        self._setNumber(4, value)

    def getIsCameraSwitching(self):
        return self._getBool(5)

    def setIsCameraSwitching(self, value):
        self._setBool(5, value)

    def getIsInRequest(self):
        return self._getBool(6)

    def setIsInRequest(self, value):
        self._setBool(6, value)

    def getIsWaitRequest(self):
        return self._getBool(7)

    def setIsWaitRequest(self, value):
        self._setBool(7, value)

    def getTokenPrice(self):
        return self._getArray(8)

    def setTokenPrice(self, value):
        self._setArray(8, value)

    @staticmethod
    def getTokenPriceType():
        return NyResourceModel

    def getResources(self):
        return self._getArray(9)

    def setResources(self, value):
        self._setArray(9, value)

    @staticmethod
    def getResourcesType():
        return NyResourceModel

    def getIsMaxAtmosphereLevel(self):
        return self._getBool(10)

    def setIsMaxAtmosphereLevel(self, value):
        self._setBool(10, value)

    def getIsChallengeCompetedGuestA(self):
        return self._getBool(11)

    def setIsChallengeCompetedGuestA(self, value):
        self._setBool(11, value)

    def getIsChallengeCompetedGuestM(self):
        return self._getBool(12)

    def setIsChallengeCompetedGuestM(self, value):
        self._setBool(12, value)

    def getIsAllMainQuestsCompleted(self):
        return self._getBool(13)

    def setIsAllMainQuestsCompleted(self, value):
        self._setBool(13, value)

    def getIsInfoBlockButtonAlreadyClicked(self):
        return self._getBool(14)

    def setIsInfoBlockButtonAlreadyClicked(self, value):
        self._setBool(14, value)

    def _initialize(self):
        super(NyGiftMachineViewModel, self)._initialize()
        self._addViewModelProperty('vehiclePreview', GiftMachineVehiclePreviewModel())
        self._addBoolProperty('isInSquad', False)
        self._addStringProperty('machineState')
        self._addNumberProperty('tokenCount', 0)
        self._addBoolProperty('isCameraSwitching', False)
        self._addBoolProperty('isInRequest', False)
        self._addBoolProperty('isWaitRequest', False)
        self._addArrayProperty('tokenPrice', Array())
        self._addArrayProperty('resources', Array())
        self._addBoolProperty('isMaxAtmosphereLevel', False)
        self._addBoolProperty('isChallengeCompetedGuestA', False)
        self._addBoolProperty('isChallengeCompetedGuestM', False)
        self._addBoolProperty('isAllMainQuestsCompleted', False)
        self._addBoolProperty('isInfoBlockButtonAlreadyClicked', False)
        self.onGoToBuyTokens = self._addCommand('onGoToBuyTokens')
        self.onGoToIdle = self._addCommand('onGoToIdle')
        self.onSkipAnimation = self._addCommand('onSkipAnimation')
        self.onBuyTokens = self._addCommand('onBuyTokens')
        self.onGoToGlade = self._addCommand('onGoToGlade')
        self.onGoToChallengeGuestA = self._addCommand('onGoToChallengeGuestA')
        self.onGoToChallengeGuestM = self._addCommand('onGoToChallengeGuestM')
        self.onGoToChallenge = self._addCommand('onGoToChallenge')
        self.onCloseInfoBlock = self._addCommand('onCloseInfoBlock')
        self.onBackFromVehiclePreview = self._addCommand('onBackFromVehiclePreview')
        self.onGoToHangar = self._addCommand('onGoToHangar')
