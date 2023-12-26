# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/advent_calendar/advent_calendar_reward_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class AwardDayState(Enum):
    REGULARDAY = 'regularDay'
    LASTDOORDAY = 'lastDoorDay'
    PROGRESSIONQUEST = 'progressionQuest'


class OpenDoorStatus(Enum):
    OPEN_DOOR_SUCCESS = 'openDoorSuccess'
    OPEN_DOOR_FAILED = 'openDoorFailed'
    OPEN_DOOR_UNDEFINED = 'openDoorUndefined'


class AdventCalendarRewardViewModel(ViewModel):
    __slots__ = ('onCloseBtnClick', 'onGoToBoxesBtnClick', 'onRewardsShown', 'onSetBlur')

    def __init__(self, properties=7, commands=4):
        super(AdventCalendarRewardViewModel, self).__init__(properties=properties, commands=commands)

    def getDayId(self):
        return self._getNumber(0)

    def setDayId(self, value):
        self._setNumber(0, value)

    def getDoorsOpenedAm(self):
        return self._getNumber(1)

    def setDoorsOpenedAm(self, value):
        self._setNumber(1, value)

    def getBonuses(self):
        return self._getArray(2)

    def setBonuses(self, value):
        self._setArray(2, value)

    @staticmethod
    def getBonusesType():
        return BonusModel

    def getAwardDayState(self):
        return AwardDayState(self._getString(3))

    def setAwardDayState(self, value):
        self._setString(3, value.value)

    def getShowBoxesButton(self):
        return self._getBool(4)

    def setShowBoxesButton(self, value):
        self._setBool(4, value)

    def getOpenDoorStatus(self):
        return OpenDoorStatus(self._getString(5))

    def setOpenDoorStatus(self, value):
        self._setString(5, value.value)

    def getIsAnimationEnabled(self):
        return self._getBool(6)

    def setIsAnimationEnabled(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(AdventCalendarRewardViewModel, self)._initialize()
        self._addNumberProperty('dayId', 0)
        self._addNumberProperty('doorsOpenedAm', 0)
        self._addArrayProperty('bonuses', Array())
        self._addStringProperty('awardDayState')
        self._addBoolProperty('showBoxesButton', False)
        self._addStringProperty('openDoorStatus')
        self._addBoolProperty('isAnimationEnabled', False)
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
        self.onGoToBoxesBtnClick = self._addCommand('onGoToBoxesBtnClick')
        self.onRewardsShown = self._addCommand('onRewardsShown')
        self.onSetBlur = self._addCommand('onSetBlur')
