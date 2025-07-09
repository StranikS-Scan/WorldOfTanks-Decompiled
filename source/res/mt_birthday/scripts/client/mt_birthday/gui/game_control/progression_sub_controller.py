# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/game_control/progression_sub_controller.py
import typing
from collections import OrderedDict
import Event
from constants import EVENT_CLIENT_DATA
from gui.ClientUpdateManager import g_clientUpdateManager
from shared_utils import first, _logger
from helpers import dependency
from mt_birthday.skeletons.sub_controllers import ITanksBirthdayProgressionSubController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from mt_birthday_common.constants import MT_BIRTHDAY_QUEST_PROGRESSION_ID, MT_BIRTHDAY_QUEST_PROGRESSION_ID_FORMAT, MT_BIRTHDAY_PROGRESSION_TOKEN, MT_BIRTHDAY_INFINITY_PROGRESSION_TOKEN
if typing.TYPE_CHECKING:
    from gui.server_events.event_items import Quest
    from typing import Dict, Tuple, List

class TanksBirthdayProgressionSubController(ITanksBirthdayProgressionSubController):
    __eventsCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, eManager):
        self.onProgressionUpdated = Event.Event(eManager)
        self.__progressionConfig = None
        return

    def start(self):
        g_clientUpdateManager.addCallback('tokens', self.__onTokensUpdate)
        g_clientUpdateManager.addCallback('eventsData', self.__onEventsDataUpdated)

    def stop(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__progressionConfig = None
        return

    def parseQuests(self):
        progressionConfig = self.__parseEventData(self.__eventsCache.getHiddenQuests(filterFunc=lambda quest: self.isBirthdayProgressionQuest(quest.getID())))
        return progressionConfig

    @property
    def progressionConfig(self):
        if self.__progressionConfig is None:
            self.__progressionConfig = self.parseQuests()
        return self.__progressionConfig

    def __parseEventData(self, eventData):
        levels = OrderedDict()
        lastRequiredProgressionPoints = 0
        maxLevelIdx = len(eventData)
        for levelIdx in range(1, maxLevelIdx + 1):
            if levelIdx < maxLevelIdx:
                isInfinity = False
            else:
                isInfinity = True
            if levelIdx <= len(eventData):
                quest = eventData.get(MT_BIRTHDAY_QUEST_PROGRESSION_ID_FORMAT.format(levelIdx), None)
                if quest is None:
                    _logger.error('Wrong MT_BIRTHDAY progression level quest format!')
                    return {}
                requiredProgressionPoints = self.getProgressionPointsRequiredFromQuest(quest)
            else:
                quest = None
                requiredProgressionPoints = float('inf')
            if requiredProgressionPoints < 1:
                _logger.error('Wrong MT_BIRTHDAY progression level quest format!')
                return {}
            if quest is not None:
                bonuses = quest.getBonuses()
            else:
                bonuses = None
            levels[levelIdx] = {'minProgressionPoints': lastRequiredProgressionPoints,
             'maxProgressionPoints': requiredProgressionPoints,
             'bonuses': bonuses,
             'isInfinity': isInfinity}
            lastRequiredProgressionPoints = requiredProgressionPoints

        return levels

    @staticmethod
    def isBirthdayProgressionQuest(qID):
        return qID.startswith(MT_BIRTHDAY_QUEST_PROGRESSION_ID)

    @staticmethod
    def getProgressionPointsRequiredFromQuest(questData):
        return first((t.getNeededCount() for t in questData.accountReqs.getTokens() if t.getID() == MT_BIRTHDAY_PROGRESSION_TOKEN), default=0)

    def __onEventsDataUpdated(self, diff):
        if EVENT_CLIENT_DATA.QUEST in diff:
            self.__progressionConfig = None
            self.onProgressionUpdated()
        return

    def __onTokensUpdate(self, diff):
        if MT_BIRTHDAY_PROGRESSION_TOKEN in diff or MT_BIRTHDAY_INFINITY_PROGRESSION_TOKEN in diff:
            self.onProgressionUpdated()

    def getProgressionTokensCount(self):
        return self.__itemsCache.items.tokens.getTokenCount(MT_BIRTHDAY_PROGRESSION_TOKEN)

    def isInfinityLevel(self):
        return bool(self.__itemsCache.items.tokens.getTokenCount(MT_BIRTHDAY_INFINITY_PROGRESSION_TOKEN))

    def getCurrentProgressionLevel(self):
        progressionTokenCount = self.getProgressionTokensCount()
        for level, value in self.progressionConfig.iteritems():
            if value['minProgressionPoints'] <= progressionTokenCount < value['maxProgressionPoints']:
                return (level, self.progressionConfig[level])

        return (None, None)

    def getLevelByPoints(self, points):
        for level, value in self.progressionConfig.iteritems():
            if value['minProgressionPoints'] <= points < value['maxProgressionPoints']:
                return (level, self.progressionConfig[level])

        return (None, None)

    def getInfinityLevel(self):
        for levelIdx, levelQuest in self.progressionConfig.iteritems():
            if levelQuest['isInfinity']:
                return (levelIdx, levelQuest)

    def getSimpleLevels(self):
        levels = []
        for levelIdx, levelQuest in self.progressionConfig.iteritems():
            if not levelQuest['isInfinity']:
                levels.append((levelIdx, levelQuest))

        return levels
