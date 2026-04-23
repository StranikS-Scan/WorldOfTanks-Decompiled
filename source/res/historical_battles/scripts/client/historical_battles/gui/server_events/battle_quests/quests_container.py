# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/server_events/battle_quests/quests_container.py
import enum
import typing
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
from historical_battles_common.hb_constants_extension import FRONT_BONUS_TYPES
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
if typing.TYPE_CHECKING:
    from typing import List, Callable
    from gui.server_events.event_items import Quest

class EventQuestsContainer(object):
    _eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, eventQuestsPrefix):
        super(EventQuestsContainer, self).__init__()
        self.__prefix = eventQuestsPrefix

    def getQuests(self):
        return self._getQuests([])

    def _getGroupQuests(self, groupID):
        return self._getQuests([self._getGroupFilter(groupID)])

    def _getQuests(self, filters):

        def questFilter(quest):
            if not (self._eventFilter(quest) and self._timeFilter(quest)):
                return False
            for filter in filters:
                if not filter(quest):
                    return False

            return True

        return self._eventsCache.getAllQuests(questFilter).items()

    def _eventFilter(self, quest):
        return quest.getID().startswith(self.__prefix) and quest.accountReqs.isAvailable()

    def _timeFilter(self, quest):
        return quest.isStarted() and not quest.isOutOfDate()

    def _getGroupFilter(self, groupID):
        fullGroupID = '{}:{}'.format(self.__prefix, groupID)
        return lambda q: q.getGroupID() == fullGroupID


class HBQuestGroup(enum.Enum):
    DAILY = 'daily_quests'
    ALL_DAYS = 'all_days_quests'
    SPECIAL = 'special_quests'


class HBQuestsContainer(EventQuestsContainer):
    __QUESTS_PREFIX = 'hb26'
    __gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self):
        super(HBQuestsContainer, self).__init__(self.__QUESTS_PREFIX)

    def isDailyQuest(self, quest):
        filter = self._getGroupFilter(HBQuestGroup.DAILY.value)
        return filter(quest)

    def getDailyQuests(self, bonusType=None, allowCompleted=False):
        quests = self._getQuests([self._getGroupFilter(HBQuestGroup.DAILY.value), lambda q: bonusType is None or q.hasBonusType(bonusType), lambda q: allowCompleted or not q.isCompleted()])
        return sorted(quests, key=lambda item: item[1].getStartTime(), reverse=True)

    def getAllDaysQuests(self):
        return self._getGroupQuests(HBQuestGroup.ALL_DAYS.value)

    def getSpecialQuests(self):
        return self._getGroupQuests(HBQuestGroup.SPECIAL.value)

    def getQuestsByGroups(self, bonusType, allowCompleted=False):
        return {HBQuestGroup.DAILY: self.getDailyQuests(bonusType, allowCompleted),
         HBQuestGroup.ALL_DAYS: self.getAllDaysQuests(),
         HBQuestGroup.SPECIAL: self.getSpecialQuests()}

    def getCurrentFrontQuestsByGroups(self, allowCompleted=False):
        front = self.__gameEventController.frontController.getSelectedFront()
        bonusType = FRONT_BONUS_TYPES.get(front.getName())
        return self.getQuestsByGroups(bonusType, allowCompleted)


def getHBQuestsContainer():
    return HBQuestsContainer()
