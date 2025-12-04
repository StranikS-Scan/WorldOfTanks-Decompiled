# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/daily/daily_quests_view_model.py
from enum import Enum, IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.daily.play_streak.play_streak_view_model import PlayStreakViewModel

class DailyTypes(Enum):
    DEFAULT = 'default'


class DailyTabs(IntEnum):
    QUESTS = 0
    PREMIUM = 1
    SERIAL = 2
    NYQUESTS = 3


class DailyQuestsViewModel(ViewModel):
    __slots__ = ('onClose', 'onTabClick', 'onInfoClick', 'onShowInfo', 'onNyInfoClick', 'changePersonVoicesEnabled', 'onStartStopPersonVoice', 'onInfoToggle', 'onBuyPremiumBtnClick', 'onRerollEnabled', 'onClaimRewards')

    def __init__(self, properties=12, commands=11):
        super(DailyQuestsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def playStreak(self):
        return self._getViewModel(0)

    @staticmethod
    def getPlayStreakType():
        return PlayStreakViewModel

    def getDailyType(self):
        return DailyTypes(self._getString(1))

    def setDailyType(self, value):
        self._setString(1, value.value)

    def getIsDailyRegularEnabled(self):
        return self._getBool(2)

    def setIsDailyRegularEnabled(self, value):
        self._setBool(2, value)

    def getIsDailyPremEnabled(self):
        return self._getBool(3)

    def setIsDailyPremEnabled(self, value):
        self._setBool(3, value)

    def getIsSerialEnterEnabled(self):
        return self._getBool(4)

    def setIsSerialEnterEnabled(self, value):
        self._setBool(4, value)

    def getDailyBattleTypes(self):
        return self._getArray(5)

    def setDailyBattleTypes(self, value):
        self._setArray(5, value)

    @staticmethod
    def getDailyBattleTypesType():
        return unicode

    def getNyBattleTypes(self):
        return self._getArray(6)

    def setNyBattleTypes(self, value):
        self._setArray(6, value)

    @staticmethod
    def getNyBattleTypesType():
        return unicode

    def getSerialEnterBattleTypes(self):
        return self._getArray(7)

    def setSerialEnterBattleTypes(self, value):
        self._setArray(7, value)

    @staticmethod
    def getSerialEnterBattleTypesType():
        return unicode

    def getCurrentTabIdx(self):
        return self._getNumber(8)

    def setCurrentTabIdx(self, value):
        self._setNumber(8, value)

    def getIntroSeen(self):
        return self._getBool(9)

    def setIntroSeen(self, value):
        self._setBool(9, value)

    def getIsPersonVoicesNowPlaying(self):
        return self._getBool(10)

    def setIsPersonVoicesNowPlaying(self, value):
        self._setBool(10, value)

    def getIsPersonVoicesEnabled(self):
        return self._getBool(11)

    def setIsPersonVoicesEnabled(self, value):
        self._setBool(11, value)

    def _initialize(self):
        super(DailyQuestsViewModel, self)._initialize()
        self._addViewModelProperty('playStreak', PlayStreakViewModel())
        self._addStringProperty('dailyType')
        self._addBoolProperty('isDailyRegularEnabled', False)
        self._addBoolProperty('isDailyPremEnabled', False)
        self._addBoolProperty('isSerialEnterEnabled', False)
        self._addArrayProperty('dailyBattleTypes', Array())
        self._addArrayProperty('nyBattleTypes', Array())
        self._addArrayProperty('serialEnterBattleTypes', Array())
        self._addNumberProperty('currentTabIdx', 0)
        self._addBoolProperty('introSeen', False)
        self._addBoolProperty('isPersonVoicesNowPlaying', False)
        self._addBoolProperty('isPersonVoicesEnabled', False)
        self.onClose = self._addCommand('onClose')
        self.onTabClick = self._addCommand('onTabClick')
        self.onInfoClick = self._addCommand('onInfoClick')
        self.onShowInfo = self._addCommand('onShowInfo')
        self.onNyInfoClick = self._addCommand('onNyInfoClick')
        self.changePersonVoicesEnabled = self._addCommand('changePersonVoicesEnabled')
        self.onStartStopPersonVoice = self._addCommand('onStartStopPersonVoice')
        self.onInfoToggle = self._addCommand('onInfoToggle')
        self.onBuyPremiumBtnClick = self._addCommand('onBuyPremiumBtnClick')
        self.onRerollEnabled = self._addCommand('onRerollEnabled')
        self.onClaimRewards = self._addCommand('onClaimRewards')
