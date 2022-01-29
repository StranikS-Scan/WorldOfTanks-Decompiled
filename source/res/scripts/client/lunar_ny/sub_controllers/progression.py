# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/lunar_ny/sub_controllers/progression.py
import typing
import Event
from constants import EVENT_CLIENT_DATA
from gui.ClientUpdateManager import g_clientUpdateManager
from gifts.gifts_common import LUNAR_NY_PROGRESSION_QUEST_TOKEN
from helpers import dependency
from lunar_ny.lunar_ny_progression_config import isLunarNYProgressionQuest, LunarNYProgressionConfig
from lunar_ny.sub_controllers import IBaseLunarSubController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from lunar_ny import LunarNYProgressionLevel

class ProgressionSubController(IBaseLunarSubController):
    __slots__ = ('__progressionConfig', 'onProgressionUpdated')
    __eventCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, eManager):
        self.onProgressionUpdated = Event.Event(eManager)
        self.__progressionConfig = None
        return

    def start(self):
        self.__progressionConfig = LunarNYProgressionConfig(self.__eventCache.getHiddenQuests(filterFunc=lambda quest: isLunarNYProgressionQuest(quest.getID())))
        g_clientUpdateManager.addCallback('tokens', self.__onTokensUpdate)
        g_clientUpdateManager.addCallback('eventsData', self.__onEventsDataUpdated)

    def stop(self):
        g_clientUpdateManager.removeObjectCallbacks(self)

    def getSentEnvelopesCount(self):
        return self.__itemsCache.items.tokens.getTokenCount(LUNAR_NY_PROGRESSION_QUEST_TOKEN)

    def getProgressionConfig(self):
        return self.__progressionConfig

    def getCurrentProgressionLevel(self):
        sentEnvelopesCount = self.getSentEnvelopesCount()
        for level in self.__progressionConfig.getLevels():
            minEnvelopes, maxEnvelopes = level.getEnvelopesRange()
            if minEnvelopes <= sentEnvelopesCount <= maxEnvelopes:
                return level

        return None

    def __onEventsDataUpdated(self, diff):
        if EVENT_CLIENT_DATA.QUEST in diff:
            self.__progressionConfig = LunarNYProgressionConfig(self.__eventCache.getHiddenQuests(filterFunc=lambda quest: isLunarNYProgressionQuest(quest.getID())))
            self.onProgressionUpdated()

    def __onTokensUpdate(self, diff):
        if LUNAR_NY_PROGRESSION_QUEST_TOKEN in diff:
            self.onProgressionUpdated()
