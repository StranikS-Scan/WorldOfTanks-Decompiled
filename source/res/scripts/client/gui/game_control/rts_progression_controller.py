# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/rts_progression_controller.py
import logging
import typing
import Event
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.prb_control.entities.listener import IGlobalListener
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.game_control import IRTSProgressionController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from constants import Configs
from gui.doc_loaders.rts_settings_loader import getEventSettings
from gui.server_events.event_items import Quest
from gui.server_events.events_helpers import isRts
from gui.server_events.events_helpers import isRTSStrategistQuest, isRTSTankerQuest
if typing.TYPE_CHECKING:
    from helpers.server_settings import _RtsProgressionConfig
    from gui.shared.utils import ValidationResult
_logger = logging.getLogger(__name__)

class RTSProgressionController(IRTSProgressionController, IGlobalListener):
    __itemsCache = dependency.descriptor(IItemsCache)
    __eventsCache = dependency.descriptor(IEventsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(RTSProgressionController, self).__init__()
        self.__serverSettings = None
        self.onUpdated = Event.Event()
        self.onProgressUpdated = Event.Event()
        return

    def fini(self):
        self.onUpdated.clear()
        self.onProgressUpdated.clear()
        self.__clear()
        super(RTSProgressionController, self).fini()

    def onLobbyInited(self, ctx):
        super(RTSProgressionController, self).onLobbyInited(ctx)
        self.startGlobalListening()
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})

    def onLobbyStarted(self, ctx):
        super(RTSProgressionController, self).onLobbyStarted(ctx)
        self.onUpdated()

    def onAccountBecomePlayer(self):
        super(RTSProgressionController, self).onAccountBecomePlayer()
        self.__onServerSettingsChanged(self.__lobbyContext.getServerSettings())

    def onDisconnected(self):
        super(RTSProgressionController, self).onDisconnected()
        self.__clear()

    def onAvatarBecomePlayer(self):
        super(RTSProgressionController, self).onAvatarBecomePlayer()
        self.__clear()

    def isEnabled(self):
        return self.getConfig().isEnabled

    def getConfig(self):
        return self.__serverSettings.rtsProgressionConfig if self.__serverSettings is not None else None

    def getCollection(self):
        return getEventSettings().collection

    def getCollectionSize(self):
        return len(self.getCollection())

    def getCollectionProgress(self):
        config = self.getConfig()
        return self.__itemsCache.items.tokens.getTokenCount(config.rtsCollectionToken)

    def getProgressLeftToNextStage(self):
        progression = self.getConfig().progression
        progress = self.getCollectionProgress()
        left = 0
        for stage in progression:
            itemsCount = stage['itemsCount']
            if progress < itemsCount:
                left = itemsCount - progress
                break

        return left

    def getQuestRewards(self, questID):
        quests = self.__eventsCache.getAllQuests(lambda quest: quest.getID() == questID)
        return quests[questID].getBonuses() if questID in quests else {}

    def getQuests(self, isCommander=None, includeFuture=True):

        def questFilter(quest):
            isValid = isRts(quest.getID()) and quest.shouldBeShown() and self.filterForSubmode(quest, isCommander)
            if isValid:
                available = quest.isAvailable()
                isAvailable = available.isValid or available.reason == 'dailyComplete' or includeFuture and available.reason == 'in_future'
                return isAvailable
            return False

        return self.__eventsCache.getBattleQuests(questFilter).values()

    def getItemsProgression(self):
        result = [(0, {})]
        for data in self.getConfig().progression:
            rewards = self.getQuestRewards(data.get('quest', ''))
            result.append((data.get('itemsCount', 0), rewards))

        return result

    def hasCurrentProgressRewards(self):
        currentProgress = self.getCollectionProgress()
        progression = self.getItemsProgression()
        for level, _ in progression:
            if currentProgress == level:
                return True

        return False

    @staticmethod
    def filterForSubmode(quest, isCommander):
        if isCommander is None:
            return True
        else:
            qIDstr = str(quest.getID())
            return isRTSStrategistQuest(qIDstr) if isCommander else isRTSTankerQuest(qIDstr)

    def __onTokensUpdate(self, diff):
        config = self.getConfig()
        if config.rtsCollectionToken in diff:
            self.onProgressUpdated()

    def __onServerSettingsChanged(self, serverSettings):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__updateRTSProgressionsSetting
        self.__serverSettings = serverSettings
        self.__serverSettings.onServerSettingsChange += self.__updateRTSProgressionsSetting
        return

    def __updateRTSProgressionsSetting(self, diff):
        if Configs.RTS_PROGRESSION_CONFIG.value in diff:
            self.onUpdated()

    def __clear(self):
        self.stopGlobalListening()
        g_clientUpdateManager.removeObjectCallbacks(self)
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__updateRTSProgressionsSetting
        self.__serverSettings = None
        return
