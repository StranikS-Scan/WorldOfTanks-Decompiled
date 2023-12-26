# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/advent_calendar/tooltips/advent_calendar_big_lootbox_tooltip_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.advent_calendar.tooltips.loot_box_bonus_view_model import LootBoxBonusViewModel

class ProgressionState(Enum):
    REWARD_RECEIVED = 'rewardReceived'
    REWARD_IN_PROGRESS = 'rewardInProgress'
    REWARD_LOCKED = 'rewardLocked'


class AdventCalendarBigLootboxTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(AdventCalendarBigLootboxTooltipModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return ProgressionState(self._getString(0))

    def setState(self, value):
        self._setString(0, value.value)

    def getDoorsToOpenAmount(self):
        return self._getNumber(1)

    def setDoorsToOpenAmount(self, value):
        self._setNumber(1, value)

    def getIsPostEvent(self):
        return self._getBool(2)

    def setIsPostEvent(self, value):
        self._setBool(2, value)

    def getBoxName(self):
        return self._getString(3)

    def setBoxName(self, value):
        self._setString(3, value)

    def getBoxCategory(self):
        return self._getString(4)

    def setBoxCategory(self, value):
        self._setString(4, value)

    def getIsShowStatus(self):
        return self._getBool(5)

    def setIsShowStatus(self, value):
        self._setBool(5, value)

    def getBonuses(self):
        return self._getArray(6)

    def setBonuses(self, value):
        self._setArray(6, value)

    @staticmethod
    def getBonusesType():
        return LootBoxBonusViewModel

    def _initialize(self):
        super(AdventCalendarBigLootboxTooltipModel, self)._initialize()
        self._addStringProperty('state')
        self._addNumberProperty('doorsToOpenAmount', 0)
        self._addBoolProperty('isPostEvent', False)
        self._addStringProperty('boxName', '')
        self._addStringProperty('boxCategory', '')
        self._addBoolProperty('isShowStatus', False)
        self._addArrayProperty('bonuses', Array())
