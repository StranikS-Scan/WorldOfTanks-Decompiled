# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/play_streak_controller.py
from skeletons.gui.game_control import IPlayStreakController
from gui.ClientUpdateManager import g_clientUpdateManager
from helpers.events_handler import EventsHandler
from Event import EventManager, Event
from constants import Configs
from play_streak.play_streak_constants import PERIODIC_SKIP_DAY_TOKEN, ACCUMULATIVE_SKIP_DAY_TOKEN, STREAK_LENGTH_TOKEN
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IWotPlusController
from gui.server_events.bonuses import SimpleBonus, getNonQuestBonuses
from helpers.server_settings import serverSettingsChangeListener
from helpers import dependency
from typing import List, Tuple, Union
SKIP_DAY_TOKENS = [PERIODIC_SKIP_DAY_TOKEN, ACCUMULATIVE_SKIP_DAY_TOKEN]
SUBS_TOKENS = {PERIODIC_SKIP_DAY_TOKEN, ACCUMULATIVE_SKIP_DAY_TOKEN, STREAK_LENGTH_TOKEN}
ADDITIONAL_INFO_TYPES = {'tokens', 'vehicles'}

class PlayStreakController(IPlayStreakController, EventsHandler):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __subscription = dependency.descriptor(IWotPlusController)

    def __init__(self):
        super(PlayStreakController, self).__init__()
        self.__eventsManager = EventManager()
        self.onDataUpdated = Event(self.__eventsManager)
        self.__skipDayCount = 0
        self.__battleTypes = []
        self.__rewardsCalendar = []

    def getSkipDayCount(self):
        return self.__skipDayCount

    def getStreakProgress(self):
        return self.__itemsCache.items.tokens.getTokenCount(STREAK_LENGTH_TOKEN)

    def getRewardsCalendar(self):
        return self.__rewardsCalendar

    def getBattleTypes(self):
        return self.__battleTypes

    def getIsBlocked(self):
        return bool(self.__itemsCache.items.playStreak.getRedemptionDay())

    def __updateData(self):
        if not self.__lobbyContext.getServerSettings().playStreakConfig.isEnabled:
            return
        settings = self.__lobbyContext.getServerSettings().playStreakConfig
        tokenCount = 0
        for token in SKIP_DAY_TOKENS:
            tokenCount += self.__itemsCache.items.tokens.getTokenCount(token)

        self.__skipDayCount = tokenCount
        self.__rewardsCalendar = []
        for day, rewards in settings.rewardsCalendar.iteritems():
            dayRewards = []
            tags = []
            additionalInfo = []
            for bonusType, bonusValue in rewards['bonus'].iteritems():
                bonus = getNonQuestBonuses(bonusType, bonusValue)
                dayRewards += bonus
                if bonusType in ('vehicles', 'tokens'):
                    additionalInfo = bonusValue.keys()

            if 'tags' in rewards:
                tags = rewards['tags']
            self.__rewardsCalendar.append((day,
             dayRewards,
             tags,
             additionalInfo))

        self.onDataUpdated()

    def __onTokensUpdate(self, diff):
        if SUBS_TOKENS.intersection(diff.keys()):
            self.__updateData()

    @serverSettingsChangeListener(Configs.PLAY_STREAK_CONFIG.value)
    def __onServerSettingsChanged(self, diff):
        self.__updateData()

    def _getEvents(self):
        return ((self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged), (self.__itemsCache.onSyncCompleted, self.__onSyncCompleted))

    def __onSyncCompleted(self, *args):
        self.__updateData()

    def onLobbyInited(self, event):
        self._subscribe()
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate,
         'playStreak': self.__onSyncCompleted})
        self.__updateData()

    def onAccountBecomeNonPlayer(self):
        self._unsubscribe()
        self.__eventsManager.clear()
        g_clientUpdateManager.removeObjectCallbacks(self)

    def fini(self):
        self._unsubscribe()
        self.__eventsManager.clear()
        g_clientUpdateManager.removeObjectCallbacks(self)
