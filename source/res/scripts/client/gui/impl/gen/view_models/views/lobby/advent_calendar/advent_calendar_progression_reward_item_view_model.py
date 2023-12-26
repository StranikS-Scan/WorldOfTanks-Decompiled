# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/advent_calendar/advent_calendar_progression_reward_item_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class ProgressionState(Enum):
    REWARD_RECEIVED = 'rewardReceived'
    REWARD_IN_PROGRESS = 'rewardInProgress'
    REWARD_LOCKED = 'rewardLocked'


class RewardType(Enum):
    GIFT_MACHINE_TOKEN = 'giftMachineToken'
    CREW_MEMBER = 'crewMember'
    BIG_LOOTBOX = 'lootBox'


class AdventCalendarProgressionRewardItemViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(AdventCalendarProgressionRewardItemViewModel, self).__init__(properties=properties, commands=commands)

    def getRequiredOpenedDoorsAmount(self):
        return self._getNumber(0)

    def setRequiredOpenedDoorsAmount(self, value):
        self._setNumber(0, value)

    def getActualOpenedDoorsAmount(self):
        return self._getNumber(1)

    def setActualOpenedDoorsAmount(self, value):
        self._setNumber(1, value)

    def getState(self):
        return ProgressionState(self._getString(2))

    def setState(self, value):
        self._setString(2, value.value)

    def getTooltipContentId(self):
        return self._getNumber(3)

    def setTooltipContentId(self, value):
        self._setNumber(3, value)

    def getRewardType(self):
        return RewardType(self._getString(4))

    def setRewardType(self, value):
        self._setString(4, value.value)

    def _initialize(self):
        super(AdventCalendarProgressionRewardItemViewModel, self)._initialize()
        self._addNumberProperty('requiredOpenedDoorsAmount', 0)
        self._addNumberProperty('actualOpenedDoorsAmount', 0)
        self._addStringProperty('state')
        self._addNumberProperty('tooltipContentId', 0)
        self._addStringProperty('rewardType')
