# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/seniority_awards_controller.py
import typing
import BigWorld
import Event
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.Waiting import Waiting
from helpers import dependency, time_utils
from skeletons.gui.game_control import ISeniorityAwardsController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from helpers.server_settings import SeniorityAwardsConfig
SACOIN = 'sacoin'

class SeniorityAwardsController(ISeniorityAwardsController):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        super(SeniorityAwardsController, self).__init__()
        self.onUpdated = Event.Event()

    @property
    def isEnabled(self):
        return self._config.enabled

    @property
    def timeLeft(self):
        return self._config.endTime - time_utils.getServerUTCTime() if self.isEnabled else -1

    @property
    def isRewardReceived(self):
        return self.__itemsCache.items.tokens.isTokenAvailable(self._config.receivedRewardsToken)

    @property
    def seniorityQuestPrefix(self):
        return self._config.rewardQuestsPrefix

    @property
    def isEligibleToReward(self):
        return self.isEnabled and self.__itemsCache.items.tokens.isTokenAvailable(self._config.rewardEligibilityToken)

    @property
    def isNeedToShowRewardNotification(self):
        return self.isEnabled and self.__hangarSpace.spaceInited and self._config.showRewardNotification and self.isEligibleToReward

    @property
    def clockOnNotification(self):
        return self._config.clockOnNotification

    def getSACoin(self):
        return self.__itemsCache.items.stats.dynamicCurrencies.get(SACOIN, 0)

    @property
    def pendingReminderTimestamp(self):
        if not self.isEnabled:
            return None
        else:
            timestamp = time_utils.getServerUTCTime()
            reminders = self._config.reminders
            pendingNotifications = [ reminderTS for reminderTS in reminders if reminderTS < timestamp ]
            return max(pendingNotifications) if pendingNotifications else None

    def claimReward(self):
        Waiting.show('claimSeniorityAwards')
        BigWorld.player().requestSingleToken(self._config.claimRewardToken)

    def markRewardReceived(self):
        Waiting.hide('claimSeniorityAwards')

    def onLobbyInited(self, event):
        super(SeniorityAwardsController, self).onLobbyInited(event)
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onSettingsChanged
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})
        if self.__hangarSpace.spaceInited:
            self.__update()
        else:
            self.__hangarSpace.onSpaceCreate += self.__onHangarLoaded

    def onAccountBecomeNonPlayer(self):
        super(SeniorityAwardsController, self).onAccountBecomeNonPlayer()
        self.__clear()

    def fini(self):
        self.onUpdated.clear()
        self.__clear()
        super(SeniorityAwardsController, self).fini()

    def onDisconnected(self):
        self.__clear()
        super(SeniorityAwardsController, self).onDisconnected()

    def onAvatarBecomePlayer(self):
        self.__removeListeners()
        super(SeniorityAwardsController, self).onAvatarBecomePlayer()

    @property
    def _config(self):
        return self.__lobbyContext.getServerSettings().getSeniorityAwardsConfig() if self.__lobbyContext else SeniorityAwardsConfig()

    def __onHangarLoaded(self):
        self.__update()

    def __clear(self):
        self.__removeListeners()
        self.__endTimestamp = None
        self.__clockOnNotification = None
        return

    def __removeListeners(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onSettingsChanged
        self.__hangarSpace.onSpaceCreate -= self.__onHangarLoaded
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __onTokensUpdate(self, diff):
        eligibilityToken = self._config.rewardEligibilityToken
        if eligibilityToken and eligibilityToken in diff:
            self.__update()

    def __onSettingsChanged(self, diff):
        if 'seniority_awards_config' in diff:
            self.__update()

    def __update(self):
        self.onUpdated()
