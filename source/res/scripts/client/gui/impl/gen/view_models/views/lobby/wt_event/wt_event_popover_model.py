# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_event_popover_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class BoxTypeEnum(Enum):
    WTHUNTER = 'wt_hunter'
    WTBOSS = 'wt_boss'


class WTPortalStatus(Enum):
    ONLYPORTALOPEN = 'only_portal_open'
    ALLCLOSED = 'all_closed'
    ALLOPEN = 'all_open'
    ONLYSHOPOPEN = 'only_shop_open'
    EVENTENDED = 'event_ended'
    UNOPENEDLOOTBOXES = 'unopened_lootboxes'
    ERROR = 'server_error'
    NOUNOPENEDLOOTBOXES = 'no_unopened_lootboxes'
    NOPRIMETIME = 'no_prime_time'


class WtEventPopoverModel(ViewModel):
    __slots__ = ('onOpenBtnClick', 'onBuyBtnClick', 'onEventBtnClick')

    def __init__(self, properties=17, commands=3):
        super(WtEventPopoverModel, self).__init__(properties=properties, commands=commands)

    def getWtPortalStatus(self):
        return WTPortalStatus(self._getString(0))

    def setWtPortalStatus(self, value):
        self._setString(0, value.value)

    def getBoxType(self):
        return BoxTypeEnum(self._getString(1))

    def setBoxType(self, value):
        self._setString(1, value.value)

    def getIsHunterLootBox(self):
        return self._getBool(2)

    def setIsHunterLootBox(self, value):
        self._setBool(2, value)

    def getEventExpireTime(self):
        return self._getNumber(3)

    def setEventExpireTime(self, value):
        self._setNumber(3, value)

    def getCount(self):
        return self._getNumber(4)

    def setCount(self, value):
        self._setNumber(4, value)

    def getIsOpenAvailable(self):
        return self._getBool(5)

    def setIsOpenAvailable(self, value):
        self._setBool(5, value)

    def getIsBuyAvailable(self):
        return self._getBool(6)

    def setIsBuyAvailable(self, value):
        self._setBool(6, value)

    def getMainRewardBoxesLeft(self):
        return self._getNumber(7)

    def setMainRewardBoxesLeft(self, value):
        self._setNumber(7, value)

    def getMaxBoxesAvailableToBuy(self):
        return self._getNumber(8)

    def setMaxBoxesAvailableToBuy(self, value):
        self._setNumber(8, value)

    def getBoxesAvailableToBuy(self):
        return self._getNumber(9)

    def setBoxesAvailableToBuy(self, value):
        self._setNumber(9, value)

    def getGuaranteedLimit(self):
        return self._getNumber(10)

    def setGuaranteedLimit(self, value):
        self._setNumber(10, value)

    def getBuyingEnableTime(self):
        return self._getNumber(11)

    def setBuyingEnableTime(self, value):
        self._setNumber(11, value)

    def getIsLastEventDay(self):
        return self._getBool(12)

    def setIsLastEventDay(self, value):
        self._setBool(12, value)

    def getHasErrors(self):
        return self._getBool(13)

    def setHasErrors(self, value):
        self._setBool(13, value)

    def getUseExternalShop(self):
        return self._getBool(14)

    def setUseExternalShop(self, value):
        self._setBool(14, value)

    def getCeaseFireEndTime(self):
        return self._getNumber(15)

    def setCeaseFireEndTime(self, value):
        self._setNumber(15, value)

    def getIsGuaranteedAwardIgnored(self):
        return self._getBool(16)

    def setIsGuaranteedAwardIgnored(self, value):
        self._setBool(16, value)

    def _initialize(self):
        super(WtEventPopoverModel, self)._initialize()
        self._addStringProperty('wtPortalStatus')
        self._addStringProperty('boxType')
        self._addBoolProperty('isHunterLootBox', False)
        self._addNumberProperty('eventExpireTime', 0)
        self._addNumberProperty('count', 0)
        self._addBoolProperty('isOpenAvailable', True)
        self._addBoolProperty('isBuyAvailable', True)
        self._addNumberProperty('mainRewardBoxesLeft', 0)
        self._addNumberProperty('maxBoxesAvailableToBuy', 0)
        self._addNumberProperty('boxesAvailableToBuy', 0)
        self._addNumberProperty('guaranteedLimit', 0)
        self._addNumberProperty('buyingEnableTime', 0)
        self._addBoolProperty('isLastEventDay', False)
        self._addBoolProperty('hasErrors', False)
        self._addBoolProperty('useExternalShop', False)
        self._addNumberProperty('ceaseFireEndTime', 0)
        self._addBoolProperty('isGuaranteedAwardIgnored', False)
        self.onOpenBtnClick = self._addCommand('onOpenBtnClick')
        self.onBuyBtnClick = self._addCommand('onBuyBtnClick')
        self.onEventBtnClick = self._addCommand('onEventBtnClick')
