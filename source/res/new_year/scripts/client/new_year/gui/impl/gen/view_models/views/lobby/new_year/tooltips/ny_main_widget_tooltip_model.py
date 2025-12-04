# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_main_widget_tooltip_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from new_year.gui.impl.gen.view_models.common.ny_event_state_model import NyEventStateModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.tooltips.pet_stats_model import PetStatsModel

class WidgetBlock(Enum):
    MAINBLOCK = 'mainBlock'
    PROGRESSBLOCK = 'progressBlock'
    BONUSBLOCK = 'bonusBlock'
    SURPRISEMACHINE = 'surpriseMachine'


class NyMainWidgetTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=16, commands=0):
        super(NyMainWidgetTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def eventState(self):
        return self._getViewModel(0)

    @staticmethod
    def getEventStateType():
        return NyEventStateModel

    def getCurrentLevel(self):
        return self._getNumber(1)

    def setCurrentLevel(self, value):
        self._setNumber(1, value)

    def getCurrentPoints(self):
        return self._getNumber(2)

    def setCurrentPoints(self, value):
        self._setNumber(2, value)

    def getNextLevelPoints(self):
        return self._getNumber(3)

    def setNextLevelPoints(self, value):
        self._setNumber(3, value)

    def getTimeLeft(self):
        return self._getNumber(4)

    def setTimeLeft(self, value):
        self._setNumber(4, value)

    def getIsNeedTimer(self):
        return self._getBool(5)

    def setIsNeedTimer(self, value):
        self._setBool(5, value)

    def getBonuses(self):
        return self._getArray(6)

    def setBonuses(self, value):
        self._setArray(6, value)

    @staticmethod
    def getBonusesType():
        return PetStatsModel

    def getBonus(self):
        return self._getNumber(7)

    def setBonus(self, value):
        self._setNumber(7, value)

    def getMaxBonus(self):
        return self._getNumber(8)

    def setMaxBonus(self, value):
        self._setNumber(8, value)

    def getMails(self):
        return self._getNumber(9)

    def setMails(self, value):
        self._setNumber(9, value)

    def getRewardsCount(self):
        return self._getNumber(10)

    def setRewardsCount(self, value):
        self._setNumber(10, value)

    def getIsPetPaused(self):
        return self._getBool(11)

    def setIsPetPaused(self, value):
        self._setBool(11, value)

    def getIsWithLeaderboard(self):
        return self._getBool(12)

    def setIsWithLeaderboard(self, value):
        self._setBool(12, value)

    def getIsProgressPaused(self):
        return self._getBool(13)

    def setIsProgressPaused(self, value):
        self._setBool(13, value)

    def getIsFirstEntry(self):
        return self._getBool(14)

    def setIsFirstEntry(self, value):
        self._setBool(14, value)

    def getBlockState(self):
        return WidgetBlock(self._getString(15))

    def setBlockState(self, value):
        self._setString(15, value.value)

    def _initialize(self):
        super(NyMainWidgetTooltipModel, self)._initialize()
        self._addViewModelProperty('eventState', NyEventStateModel())
        self._addNumberProperty('currentLevel', 1)
        self._addNumberProperty('currentPoints', 0)
        self._addNumberProperty('nextLevelPoints', 0)
        self._addNumberProperty('timeLeft', 0)
        self._addBoolProperty('isNeedTimer', False)
        self._addArrayProperty('bonuses', Array())
        self._addNumberProperty('bonus', 0)
        self._addNumberProperty('maxBonus', 0)
        self._addNumberProperty('mails', 0)
        self._addNumberProperty('rewardsCount', 0)
        self._addBoolProperty('isPetPaused', False)
        self._addBoolProperty('isWithLeaderboard', True)
        self._addBoolProperty('isProgressPaused', False)
        self._addBoolProperty('isFirstEntry', False)
        self._addStringProperty('blockState')
