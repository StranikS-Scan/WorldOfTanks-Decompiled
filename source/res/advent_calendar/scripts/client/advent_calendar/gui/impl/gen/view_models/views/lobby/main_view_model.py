# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/gui/impl/gen/view_models/views/lobby/main_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from advent_calendar.gui.impl.gen.view_models.views.lobby.components.advent_calendar_events import AdventCalendarEvents
from advent_calendar.gui.impl.gen.view_models.views.lobby.door_view_model import DoorViewModel
from advent_calendar.gui.impl.gen.view_models.views.lobby.progression_rewards_view_model import ProgressionRewardsViewModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_resources_balance_model import NyResourcesBalanceModel

class StatePhase(Enum):
    ACTIVE_PHASE = 'activePhase'
    POST_ACTIVE_PHASE = 'postActivePhase'


class MainViewModel(ViewModel):
    __slots__ = ('onClose', 'onOpenDoorAnimStarted', 'onOpenDoorAnimEnded', 'onShowPurchaseDialog', 'onAnimationCompleted', 'onOpenDownloadLink', 'onInfoClick')

    def __init__(self, properties=14, commands=7):
        super(MainViewModel, self).__init__(properties=properties, commands=commands)

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
        return ProgressionRewardsViewModel

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

    def getHolidayOpsStartTime(self):
        return self._getNumber(5)

    def setHolidayOpsStartTime(self, value):
        self._setNumber(5, value)

    def getShowBlur(self):
        return self._getBool(6)

    def setShowBlur(self, value):
        self._setBool(6, value)

    def getPostEventStartDate(self):
        return self._getNumber(7)

    def setPostEventStartDate(self, value):
        self._setNumber(7, value)

    def getPostEventEndDate(self):
        return self._getNumber(8)

    def setPostEventEndDate(self, value):
        self._setNumber(8, value)

    def getDoors(self):
        return self._getArray(9)

    def setDoors(self, value):
        self._setArray(9, value)

    @staticmethod
    def getDoorsType():
        return DoorViewModel

    def getDoorOpenBlocked(self):
        return self._getBool(10)

    def setDoorOpenBlocked(self, value):
        self._setBool(10, value)

    def getIsAnimationEnabled(self):
        return self._getBool(11)

    def setIsAnimationEnabled(self, value):
        self._setBool(11, value)

    def getIsCalendarCompleted(self):
        return self._getBool(12)

    def setIsCalendarCompleted(self, value):
        self._setBool(12, value)

    def getIsIntroScreenVisible(self):
        return self._getBool(13)

    def setIsIntroScreenVisible(self, value):
        self._setBool(13, value)

    def _initialize(self):
        super(MainViewModel, self)._initialize()
        self._addViewModelProperty('balance', NyResourcesBalanceModel())
        self._addViewModelProperty('progressionRewards', ProgressionRewardsViewModel())
        self._addViewModelProperty('event', AdventCalendarEvents())
        self._addStringProperty('statePhase', StatePhase.ACTIVE_PHASE.value)
        self._addNumberProperty('startTime', 0)
        self._addNumberProperty('holidayOpsStartTime', 0)
        self._addBoolProperty('showBlur', False)
        self._addNumberProperty('postEventStartDate', 0)
        self._addNumberProperty('postEventEndDate', 0)
        self._addArrayProperty('doors', Array())
        self._addBoolProperty('doorOpenBlocked', False)
        self._addBoolProperty('isAnimationEnabled', False)
        self._addBoolProperty('isCalendarCompleted', False)
        self._addBoolProperty('isIntroScreenVisible', False)
        self.onClose = self._addCommand('onClose')
        self.onOpenDoorAnimStarted = self._addCommand('onOpenDoorAnimStarted')
        self.onOpenDoorAnimEnded = self._addCommand('onOpenDoorAnimEnded')
        self.onShowPurchaseDialog = self._addCommand('onShowPurchaseDialog')
        self.onAnimationCompleted = self._addCommand('onAnimationCompleted')
        self.onOpenDownloadLink = self._addCommand('onOpenDownloadLink')
        self.onInfoClick = self._addCommand('onInfoClick')
