# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hangar_widget/providers/user_mission_item.py
from abc import ABCMeta
from typing import TYPE_CHECKING
from gui.server_events.events_helpers import EventInfoModel
from gui.impl.lobby.user_missions.hangar_widget.utils import DailyMissionItemPacker, WeeklyMissionItemPacker
from gui.shared.missions.packers.bonus import getDailyMissionsBonusPacker, getWeeklyMissionsBonusPacker, weeklyBonusSort
if TYPE_CHECKING:
    from gui.server_events.event_items import DailyQuest

class MissionItem(object):
    __metaclass__ = ABCMeta
    __slots__ = ('itemId', 'itemType', 'weight', 'secondaryKey', '_rawData', '_isCompleted')

    def __init__(self, itemId, itemType, weight=0, secondaryKey=None):
        self.itemId = itemId
        self.itemType = itemType
        self.weight = weight
        self.secondaryKey = tuple(secondaryKey) if secondaryKey else ()
        self._rawData = None
        self._isCompleted = False
        return

    @property
    def rawData(self):
        return self._rawData

    @rawData.setter
    def rawData(self, value):
        self._rawData = value

    @property
    def isCompleted(self):
        return self._isCompleted

    @isCompleted.setter
    def isCompleted(self, value):
        self._isCompleted = value

    @property
    def countdown(self):
        pass

    def getMissionPacker(self):
        raise NotImplementedError

    def getBonusPacker(self):
        raise NotImplementedError

    def getRewardsSortFunc(self):
        raise NotImplementedError

    def getAnimationId(self):
        raise NotImplementedError


class DailyQuestMissionItem(MissionItem):
    __slots__ = ('difficulty',)
    _TYPE = 'daily'

    def __init__(self, itemId, weight, difficulty):
        super(DailyQuestMissionItem, self).__init__(itemId, self._TYPE, weight)
        self.difficulty = difficulty

    def __repr__(self):
        return 'DailyQuest(id={}, type={}, weight={}, difficulty={})'.format(self.itemId, self.itemType, self.weight, self.difficulty)

    def setItemType(self, value):
        self.itemType = value

    @property
    def countdown(self):
        dailyQuest = self._rawData
        return EventInfoModel.getDailyProgressResetTimeDelta() if dailyQuest.isBonus() else super(DailyQuestMissionItem, self).countdown

    def getMissionPacker(self):
        return DailyMissionItemPacker()

    def getBonusPacker(self):
        return getDailyMissionsBonusPacker()

    def getRewardsSortFunc(self):
        return None

    def getAnimationId(self):
        return '%s::%s' % (self._TYPE, self.difficulty)


class PremiumDailyQuestMissionItem(MissionItem):
    __slots__ = ()
    _TYPE = 'premium_daily'

    def __init__(self, itemId, weight):
        super(PremiumDailyQuestMissionItem, self).__init__(itemId, self._TYPE, weight)

    def __repr__(self):
        return 'PremiumDailyQuest(id={}, type={}, weight={})'.format(self.itemId, self.itemType, self.weight)

    def getMissionPacker(self):
        return DailyMissionItemPacker()

    def getBonusPacker(self):
        return getDailyMissionsBonusPacker()

    def getRewardsSortFunc(self):
        return None

    def getAnimationId(self):
        return self.itemId


class WeeklyQuestMissionItem(MissionItem):
    __slots__ = ('_commonConditionId', '_specialConditionIds', '_questId')
    _TYPE = 'weekly'

    def __init__(self, itemId, weight, questId):
        super(WeeklyQuestMissionItem, self).__init__(itemId, self._TYPE, weight)
        self._commonConditionId = 0
        self._specialConditionIds = []
        self._questId = questId

    def __repr__(self):
        return 'WeeklyQuest(id={}, type={}, weight={}, _commonConditionId={}, _specialConditionIds={})'.format(self.itemId, self.itemType, self.weight, self._commonConditionId, self._specialConditionIds)

    @property
    def commonConditionId(self):
        return self._commonConditionId

    @commonConditionId.setter
    def commonConditionId(self, value):
        self._commonConditionId = value

    @property
    def specialConditionIds(self):
        return self._specialConditionIds

    @specialConditionIds.setter
    def specialConditionIds(self, value):
        self._specialConditionIds = value

    def getMissionPacker(self):
        return WeeklyMissionItemPacker()

    def getBonusPacker(self):
        return getWeeklyMissionsBonusPacker()

    def getRewardsSortFunc(self):
        return weeklyBonusSort

    def getAnimationId(self):
        return '%s::%s' % (self._TYPE, self._questId)
