# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/advent_calendar/advent_calendar_main_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.advent_calendar.advent_calendar_door_view_model import AdventCalendarDoorViewModel
from gui.impl.gen.view_models.views.lobby.advent_calendar.advent_calendar_progression_rewards_view_model import AdventCalendarProgressionRewardsViewModel
from gui.impl.gen.view_models.views.lobby.advent_calendar.components.advent_calendar_events import AdventCalendarEvents
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_resources_balance_model import NyResourcesBalanceModel

class StatePhase(Enum):
    ACTIVE_PHASE = 'activePhase'
    POST_ACTIVE_PHASE = 'postActivePhase'


class AdventCalendarMainViewModel(ViewModel):
    __slots__ = ('onClose', 'onOpenDoor', 'onShowReward', 'onShowPurchaseDialog', 'onAnimationCompleted')

    def __init__(self, properties=12, commands=5):
        super(AdventCalendarMainViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def balance(self):
        return self._getViewModel(0)

    @staticmethod
    def getBalanceType():
        return NyResourcesBalanceModel

    @property
    def progressionRewards(self):
        return self._getViewModel(1)

    @staticmethod
    def getProgressionRewardsType():
        return AdventCalendarProgressionRewardsViewModel

    @property
    def event(self):
        return self._getViewModel(2)

    @staticmethod
    def getEventType():
        return AdventCalendarEvents

    def getStatePhase(self):
        return StatePhase(self._getString(3))

    def setStatePhase(self, value):
        self._setString(3, value.value)

    def getStartTime(self):
        return self._getNumber(4)

    def setStartTime(self, value):
        self._setNumber(4, value)

    def getShowBlur(self):
        return self._getBool(5)

    def setShowBlur(self, value):
        self._setBool(5, value)

    def getActivePhaseEndTime(self):
        return self._getNumber(6)

    def setActivePhaseEndTime(self, value):
        self._setNumber(6, value)

    def getPostActivePhaseEndTime(self):
        return self._getNumber(7)

    def setPostActivePhaseEndTime(self, value):
        self._setNumber(7, value)

    def getDoors(self):
        return self._getArray(8)

    def setDoors(self, value):
        self._setArray(8, value)

    @staticmethod
    def getDoorsType():
        return AdventCalendarDoorViewModel

    def getDoorOpenBlocked(self):
        return self._getBool(9)

    def setDoorOpenBlocked(self, value):
        self._setBool(9, value)

    def getIsAnimationEnabled(self):
        return self._getBool(10)

    def setIsAnimationEnabled(self, value):
        self._setBool(10, value)

    def getIsCalendarComplited(self):
        return self._getBool(11)

    def setIsCalendarComplited(self, value):
        self._setBool(11, value)

    def _initialize(self):
        super(AdventCalendarMainViewModel, self)._initialize()
        self._addViewModelProperty('balance', NyResourcesBalanceModel())
        self._addViewModelProperty('progressionRewards', AdventCalendarProgressionRewardsViewModel())
        self._addViewModelProperty('event', AdventCalendarEvents())
        self._addStringProperty('statePhase', StatePhase.ACTIVE_PHASE.value)
        self._addNumberProperty('startTime', 0)
        self._addBoolProperty('showBlur', False)
        self._addNumberProperty('activePhaseEndTime', 0)
        self._addNumberProperty('postActivePhaseEndTime', 0)
        self._addArrayProperty('doors', Array())
        self._addBoolProperty('doorOpenBlocked', False)
        self._addBoolProperty('isAnimationEnabled', False)
        self._addBoolProperty('isCalendarComplited', False)
        self.onClose = self._addCommand('onClose')
        self.onOpenDoor = self._addCommand('onOpenDoor')
        self.onShowReward = self._addCommand('onShowReward')
        self.onShowPurchaseDialog = self._addCommand('onShowPurchaseDialog')
        self.onAnimationCompleted = self._addCommand('onAnimationCompleted')
