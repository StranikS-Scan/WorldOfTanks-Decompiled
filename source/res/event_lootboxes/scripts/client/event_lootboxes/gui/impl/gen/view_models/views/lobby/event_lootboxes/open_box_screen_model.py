# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: event_lootboxes/scripts/client/event_lootboxes/gui/impl/gen/view_models/views/lobby/event_lootboxes/open_box_screen_model.py
from enum import Enum, IntEnum
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from event_lootboxes.gui.impl.gen.view_models.views.lobby.event_lootboxes.reward_model import RewardModel
from event_lootboxes.gui.impl.gen.view_models.views.lobby.event_lootboxes.vehicle_model import VehicleModel

class BoxType(Enum):
    COMMON = 'event_common'
    PREMIUM = 'event_premium'


class OSBit(IntEnum):
    X86 = 1
    X64 = 2
    UNKNOWN = 3


class OpenBoxScreenModel(ViewModel):
    __slots__ = ('changeAnimationState', 'openNextBox', 'buyBox', 'showVehicleInHangar', 'hideWaiting', 'onClose')

    def __init__(self, properties=16, commands=6):
        super(OpenBoxScreenModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewards(self):
        return self._getViewModel(0)

    @staticmethod
    def getRewardsType():
        return RewardModel

    @property
    def vehicle(self):
        return self._getViewModel(1)

    @staticmethod
    def getVehicleType():
        return VehicleModel

    def getIsAnimationActive(self):
        return self._getBool(2)

    def setIsAnimationActive(self, value):
        self._setBool(2, value)

    def getHasVehicle(self):
        return self._getBool(3)

    def setHasVehicle(self, value):
        self._setBool(3, value)

    def getPurchasesLeft(self):
        return self._getNumber(4)

    def setPurchasesLeft(self, value):
        self._setNumber(4, value)

    def getBoxCount(self):
        return self._getNumber(5)

    def setBoxCount(self, value):
        self._setNumber(5, value)

    def getBoxType(self):
        return BoxType(self._getString(6))

    def setBoxType(self, value):
        self._setString(6, value.value)

    def getTimeLeft(self):
        return self._getNumber(7)

    def setTimeLeft(self, value):
        self._setNumber(7, value)

    def getIsLastDay(self):
        return self._getBool(8)

    def setIsLastDay(self, value):
        self._setBool(8, value)

    def getDayLimit(self):
        return self._getNumber(9)

    def setDayLimit(self, value):
        self._setNumber(9, value)

    def getIsBuyAvailable(self):
        return self._getBool(10)

    def setIsBuyAvailable(self, value):
        self._setBool(10, value)

    def getIsLootBoxAvailable(self):
        return self._getBool(11)

    def setIsLootBoxAvailable(self, value):
        self._setBool(11, value)

    def getOsBit(self):
        return OSBit(self._getNumber(12))

    def setOsBit(self, value):
        self._setNumber(12, value.value)

    def getMainRewardBoxesLeft(self):
        return self._getNumber(13)

    def setMainRewardBoxesLeft(self, value):
        self._setNumber(13, value)

    def getGuaranteedLimit(self):
        return self._getNumber(14)

    def setGuaranteedLimit(self, value):
        self._setNumber(14, value)

    def getUseExternalShop(self):
        return self._getBool(15)

    def setUseExternalShop(self, value):
        self._setBool(15, value)

    def _initialize(self):
        super(OpenBoxScreenModel, self)._initialize()
        self._addViewModelProperty('rewards', UserListModel())
        self._addViewModelProperty('vehicle', VehicleModel())
        self._addBoolProperty('isAnimationActive', True)
        self._addBoolProperty('hasVehicle', False)
        self._addNumberProperty('purchasesLeft', 0)
        self._addNumberProperty('boxCount', 0)
        self._addStringProperty('boxType')
        self._addNumberProperty('timeLeft', 0)
        self._addBoolProperty('isLastDay', False)
        self._addNumberProperty('dayLimit', 0)
        self._addBoolProperty('isBuyAvailable', False)
        self._addBoolProperty('isLootBoxAvailable', True)
        self._addNumberProperty('osBit')
        self._addNumberProperty('mainRewardBoxesLeft', 0)
        self._addNumberProperty('guaranteedLimit', 0)
        self._addBoolProperty('useExternalShop', False)
        self.changeAnimationState = self._addCommand('changeAnimationState')
        self.openNextBox = self._addCommand('openNextBox')
        self.buyBox = self._addCommand('buyBox')
        self.showVehicleInHangar = self._addCommand('showVehicleInHangar')
        self.hideWaiting = self._addCommand('hideWaiting')
        self.onClose = self._addCommand('onClose')
