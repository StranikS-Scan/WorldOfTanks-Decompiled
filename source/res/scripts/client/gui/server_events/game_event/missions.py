# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/game_event/missions.py
import logging
import time
import BigWorld
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
from Event import Event, EventManager
from gui.server_events.conditions import getTokenNeededCountInCondition, getTokenReceivedCountInCondition
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events.conditions import getProgressFromQuestWithSingleAccumulative
from helpers import time_utils, i18n
from gui.server_events.bonuses import TokensBonus
_logger = logging.getLogger(__name__)
_INITIAL_MISSION_ID = 1
_QUEST_GROUP_PREFIX = 'he19_mission'
_QUEST_MISSION_SEPARATOR = ':'
_QUEST_MISSION_ITEM_SEPARATOR = '_'
_UNLOCK_TOKEN_NAME = '{}_unlock'
_MAX_PROGRESS_VALUE = 100

class EventMissions(object):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        self.needToShowAward = False
        self._app = None
        self._em = EventManager()
        self.onUpdated = Event(self._em)
        self._missions = {}
        return

    def start(self):
        self._missions = self._getMissions()
        self.eventsCache.onSyncCompleted += self._onSyncCompleted

    def stop(self):
        self._em.clear()
        self.eventsCache.onSyncCompleted -= self._onSyncCompleted

    def isEnabled(self):
        return bool(self._missions)

    def isCompleted(self):
        return all((mission.isCompleted() for mission in self._missions.itervalues()))

    def getMaxMissionID(self):
        return None if not self._missions else max((mission.getID() for mission in self._missions.itervalues()))

    def getMissionByID(self, missionID):
        return self._missions[missionID] if missionID in self._missions else None

    def getMissions(self):
        return self._missions

    def getItemWithBonusToken(self, tokenID):
        for mission in self._missions.itervalues():
            for item in mission.getItems():
                for bonus in item.getBonuses():
                    if not isinstance(bonus, TokensBonus):
                        continue
                    if tokenID in bonus.getTokens():
                        return item

        return None

    def getQuest(self, questID):
        return self._getQuests().get(questID, None)

    def _onSyncCompleted(self):
        self._missions = self._getMissions()
        self.onUpdated()

    def _getQuests(self):
        return self.eventsCache.getHiddenQuests()

    def _getMissions(self):
        missions = {}
        for quest in self._getQuests().itervalues():
            groupID = quest.getGroupID()
            if groupID:
                if groupID.startswith(_QUEST_GROUP_PREFIX):
                    groupID = int(groupID.split(_QUEST_MISSION_SEPARATOR)[-1])
                    if groupID not in missions:
                        missions[groupID] = [quest]
                    else:
                        missions[groupID].append(quest)
            _logger.warning('Quest "%s" without right group', quest.getID())

        return {mission.getID():mission for mission in (Mission(quests) for quests in missions.itervalues())}


class Mission(object):

    def __init__(self, quests):
        super(Mission, self).__init__()
        self._items = sorted((MissionItem(quest) for quest in quests), key=lambda x: x.getID())

    def getItems(self):
        return self._items

    def isCompleted(self):
        return all((item.isCompleted() for item in self._items))

    def getID(self):
        return self._items[0].getMissionID() if self._items else None

    def getIcon(self, size):
        return backport.image(R.images.gui.maps.icons.event.missions.dyn('missionIcon{}{}'.format(size, self.getID()))())

    def getName(self):
        return backport.text(R.strings.event.missions.mission.num(self.getID()).header())

    def getSelectedItem(self):
        return None if not self.getItems() else next((item for item in self.getItems() if item.isAvailable() and not item.isCompleted()), self.getItems()[-1])


class MissionItem(object):

    def __init__(self, quest):
        super(MissionItem, self).__init__()
        self._quest = quest
        self._unlockTokenName = _UNLOCK_TOKEN_NAME.format(self._quest.getID())

    def getQuest(self):
        return self._quest

    def getQuestID(self):
        return self._quest.getID()

    def getID(self):
        return int(self._quest.getID().split(_QUEST_MISSION_ITEM_SEPARATOR)[-1])

    def getMissionID(self):
        return int(self._quest.getGroupID().split(_QUEST_MISSION_SEPARATOR)[-1])

    def isCompleted(self):
        return self._quest.isCompleted()

    def isAvailable(self):
        isAvailable, _ = self._isAvailable()
        return isAvailable

    def getBonuses(self):
        return self._quest.getBonuses()

    def getDescr(self):
        quest = self.getQuest()
        desc = quest.getDescription()
        if desc:
            return desc
        desc = R.strings.event.missions.mission.num(self.getMissionID()).item.num(self.getID()).desc()
        _, totalProgress = getProgressFromQuestWithSingleAccumulative(quest)
        return backport.text(desc, maxCount=backport.getIntegralFormat(totalProgress)) if totalProgress and totalProgress > 1 else backport.text(desc)

    def getStatusLocalized(self):
        _, status = self._isAvailable()
        statusRes = R.strings.event.missions.status.dyn(status)
        if status == 'willBeUnlockedAt':
            return backport.text(statusRes(), time=backport.getDateTimeFormat(self._quest.getStartTime()))
        if status in ('dailyAvailable', 'dailyCompleted'):
            resetTime = self.getDailyResetTime()
            if resetTime:
                return backport.text(statusRes(), time=resetTime)
            return ''
        return backport.text(statusRes())

    def isDaily(self):
        return self._quest.bonusCond.isDaily()

    def getDailyResetTime(self):
        resetHourUTC = self._getDailyProgressResetTimeUTC() / time_utils.ONE_HOUR
        return time.strftime(i18n.makeString('#quests:details/conditions/postBattle/dailyReset/timeFmt'), time_utils.getTimeStructInLocal(time_utils.getTimeTodayForUTC(hour=resetHourUTC))) if resetHourUTC >= 0 else None

    @classmethod
    def _getDailyProgressResetTimeUTC(cls):
        regionalSettings = BigWorld.player().serverSettings['regional_settings']
        if 'starting_time_of_a_new_game_day' in regionalSettings:
            newDayUTC = regionalSettings['starting_time_of_a_new_game_day']
        elif 'starting_time_of_a_new_day' in regionalSettings:
            newDayUTC = regionalSettings['starting_time_of_a_new_day']
        else:
            newDayUTC = 0
        return newDayUTC

    def _isAvailable(self):
        if self.isCompleted():
            if self.isDaily():
                return (True, 'dailyCompleted')
            return (True, 'completed')
        needed = getTokenNeededCountInCondition(self._quest, self._unlockTokenName)
        if getTokenReceivedCountInCondition(self._quest, self._unlockTokenName) < needed:
            return (False, 'locked')
        if self._quest.getStartTimeLeft() > 0:
            return (False, 'willBeAvailableAt')
        return (True, 'dailyAvailable') if self.isDaily() else (True, 'available')
