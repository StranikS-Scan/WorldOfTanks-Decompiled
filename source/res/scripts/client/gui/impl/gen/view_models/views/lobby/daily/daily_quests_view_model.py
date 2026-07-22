# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/daily/daily_quests_view_model.py
from enum import Enum, IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class DailyTypes(Enum):
    DEFAULT = 'default'


class DailyTabs(IntEnum):
    QUESTS = 0
    PREMIUM = 1
    SERIAL = 2


class DailyQuestsViewModel(ViewModel):
    __slots__ = ('onClose', 'onTabClick', 'onInfoClick', 'onShowInfo', 'onInfoToggle', 'onBuyPremiumBtnClick', 'onRerollEnabled', 'onClaimRewards')

    def __init__(self, properties=8, commands=8):
        super(DailyQuestsViewModel, self).__init__(properties=properties, commands=commands)

    def getDailyType(self):
        return DailyTypes(self._getString(0))

    def setDailyType(self, value):
        self._setString(0, value.value)

    def getIsDailyRegularEnabled(self):
        return self._getBool(1)

    def setIsDailyRegularEnabled(self, value):
        self._setBool(1, value)

    def getIsDailyPremEnabled(self):
        return self._getBool(2)

    def setIsDailyPremEnabled(self, value):
        self._setBool(2, value)

    def getIsSerialEnterEnabled(self):
        return self._getBool(3)

    def setIsSerialEnterEnabled(self, value):
        self._setBool(3, value)

    def getDailyBattleTypes(self):
        return self._getArray(4)

    def setDailyBattleTypes(self, value):
        self._setArray(4, value)

    @staticmethod
    def getDailyBattleTypesType():
        return unicode

    def getSerialEnterBattleTypes(self):
        return self._getArray(5)

    def setSerialEnterBattleTypes(self, value):
        self._setArray(5, value)

    @staticmethod
    def getSerialEnterBattleTypesType():
        return unicode

    def getCurrentTabIdx(self):
        return self._getNumber(6)

    def setCurrentTabIdx(self, value):
        self._setNumber(6, value)

    def getIntroSeen(self):
        return self._getBool(7)

    def setIntroSeen(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(DailyQuestsViewModel, self)._initialize()
        self._addStringProperty('dailyType')
        self._addBoolProperty('isDailyRegularEnabled', False)
        self._addBoolProperty('isDailyPremEnabled', False)
        self._addBoolProperty('isSerialEnterEnabled', False)
        self._addArrayProperty('dailyBattleTypes', Array())
        self._addArrayProperty('serialEnterBattleTypes', Array())
        self._addNumberProperty('currentTabIdx', 0)
        self._addBoolProperty('introSeen', False)
        self.onClose = self._addCommand('onClose')
        self.onTabClick = self._addCommand('onTabClick')
        self.onInfoClick = self._addCommand('onInfoClick')
        self.onShowInfo = self._addCommand('onShowInfo')
        self.onInfoToggle = self._addCommand('onInfoToggle')
        self.onBuyPremiumBtnClick = self._addCommand('onBuyPremiumBtnClick')
        self.onRerollEnabled = self._addCommand('onRerollEnabled')
        self.onClaimRewards = self._addCommand('onClaimRewards')
