# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_gift_machine_token_tooltip_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class ProgressionState(Enum):
    REWARD_RECEIVED = 'rewardReceived'
    REWARD_IN_PROGRESS = 'rewardInProgress'
    REWARD_LOCKED = 'rewardLocked'


class NyGiftMachineTokenTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(NyGiftMachineTokenTooltipModel, self).__init__(properties=properties, commands=commands)

    def getTokenCount(self):
        return self._getNumber(0)

    def setTokenCount(self, value):
        self._setNumber(0, value)

    def getAdventCalendarState(self):
        return ProgressionState(self._getString(1))

    def setAdventCalendarState(self, value):
        self._setString(1, value.value)

    def getAdventCalendarDoorsToOpenAmount(self):
        return self._getNumber(2)

    def setAdventCalendarDoorsToOpenAmount(self, value):
        self._setNumber(2, value)

    def getIsAdventCalendarPostEvent(self):
        return self._getBool(3)

    def setIsAdventCalendarPostEvent(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(NyGiftMachineTokenTooltipModel, self)._initialize()
        self._addNumberProperty('tokenCount', 0)
        self._addStringProperty('adventCalendarState')
        self._addNumberProperty('adventCalendarDoorsToOpenAmount', 0)
        self._addBoolProperty('isAdventCalendarPostEvent', False)
