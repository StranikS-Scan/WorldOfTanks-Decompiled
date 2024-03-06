# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/winback_controller.py
from enum import Enum
import typing
import Event
from account_helpers.AccountSettings import Winback
from constants import Configs
from gui.impl.lobby.winback.winback_helpers import getLevelFromSelectableToken, WinbackQuestTypes, TOKEN_TO_REWARD_MAPPING, getNonCompensationToken
from gui.macroses import getLanguageCode
from gui.server_events.event_items import Quest
from gui.server_events.events_helpers import getIdxFromQuestID
from gui.winback.winback_helpers import getWinbackSetting, setWinbackSetting
from helpers import dependency
from shared_utils import first
from skeletons.gui.game_control import IWinbackController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Optional
    from helpers.server_settings import WinbackConfig

class _WinbackState(Enum):
    NOT_STARTED = 0
    IN_PROGRESS = 1
    FINISHED = 2


class WinbackController(IWinbackController):
    __slots__ = ('__state',)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        super(WinbackController, self).__init__()
        self.onConfigUpdated = Event.Event()
        self.onStateUpdated = Event.Event()
        self.__state = None
        return

    @property
    def winbackConfig(self):
        return self.__lobbyContext.getServerSettings().winbackConfig

    @property
    def winbackQuests(self):
        return self.__eventsCache.getAllQuests(self.isWinbackQuest)

    @property
    def winbackPromoURL(self):
        return self.winbackConfig.winbackPromoURL.format(languageCode=getLanguageCode())

    def fini(self):
        self.__clearListeners()

    def onLobbyStarted(self, *_):
        self.__addListeners()
        self.__updateState()
        self.__updateWinbackSettings()

    def onAccountBecomeNonPlayer(self):
        self.__clearListeners()

    def isEnabled(self):
        return self.winbackConfig.isEnabled and self.__hasAccessToken()

    def isModeAvailable(self):
        return self.winbackConfig.isEnabled and self.winbackConfig.isModeEnabled and self.__hasModeAccessToken() and self.getWinbackBattlesCountLeft() > 0

    def isProgressionAvailable(self):
        return self.winbackConfig.isEnabled and self.winbackConfig.isProgressionEnabled and not self.isFinished()

    def isFinished(self):
        return self.__itemsCache.items.tokens.getTokenCount(self.winbackConfig.lastQuestEnabler) <= 0

    def parseOfferToken(self, token):
        if not token or not self.isWinbackOfferToken(token):
            return None
        else:
            token = getNonCompensationToken(token)
            offerType = token.split(':')[2]
            offerLevel = getLevelFromSelectableToken(token)
            return {'name': TOKEN_TO_REWARD_MAPPING[offerType],
             'level': offerLevel,
             'token': token}

    def isWinbackQuest(self, quest):
        if quest is None or not self.winbackConfig.isEnabled:
            return False
        else:
            questId = quest if isinstance(quest, str) else quest.getID()
            return questId.startswith(self.winbackConfig.tokenQuestPrefix)

    def getQuestIdx(self, quest):
        if quest is None:
            return -1
        else:
            return getIdxFromQuestID(quest) if isinstance(quest, str) else getIdxFromQuestID(quest.getID())

    def getQuestType(self, questID):
        parts = questID.split('_')
        try:
            result = WinbackQuestTypes(parts[-2])
        except ValueError:
            result = WinbackQuestTypes.NORMAL

        return result

    def isWinbackOfferToken(self, offerToken):
        return False if not self.winbackConfig.isEnabled else offerToken.startswith(self.winbackConfig.offerTokenPrefix)

    def hasWinbackOfferToken(self):
        tokens = self.__itemsCache.items.tokens.getTokens()
        for token in tokens:
            if self.isWinbackOfferToken(token) and token.endswith('_gift'):
                return True

        return False

    def getWinbackBattlesCountLeft(self):
        return self.__itemsCache.items.tokens.getTokenCount(self.__getWinbackBattlesCountToken())

    def isPromoEnabled(self):
        return self.isEnabled() and self.winbackConfig.isWhatsNewEnabled and self.__hasPromoToken()

    def __getWinbackBattlesCountToken(self):
        return self.winbackConfig.winbackBattlesCountToken

    def __addListeners(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsUpdate
        self.__itemsCache.onSyncCompleted += self.__updateState
        self.__eventsCache.onSyncCompleted += self.__updateState

    def __clearListeners(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsUpdate
        self.__itemsCache.onSyncCompleted -= self.__updateState
        self.__eventsCache.onSyncCompleted -= self.__updateState

    def __onServerSettingsUpdate(self, diff):
        if Configs.WINBACK_CONFIG.value in diff:
            self.onConfigUpdated()

    def __hasAccessToken(self):
        return self.__itemsCache.items.tokens.isTokenAvailable(self.winbackConfig.winbackAccessToken)

    def __hasModeAccessToken(self):
        return any((self.__itemsCache.items.tokens.isTokenAvailable(token) for token in self.winbackConfig.winbackModeAccessTokens))

    def __hasPromoToken(self):
        return self.__itemsCache.items.tokens.isTokenAvailable(self.winbackConfig.winbackShowPromoToken)

    def __updateState(self, *_):
        if self.isFinished():
            newState = _WinbackState.FINISHED
        elif self.__hasAccessToken():
            newState = _WinbackState.IN_PROGRESS
        else:
            newState = _WinbackState.NOT_STARTED
        if newState != self.__state:
            self.__state = newState
            self.__updateWinbackSettings()
            self.onStateUpdated()

    def __updateWinbackSettings(self):
        startingQuest = first(self.__eventsCache.getAllQuests(lambda q: q.getID() == self.winbackConfig.winbackStartingQuest).values())
        if startingQuest is None:
            return
        else:
            questBonusCount = startingQuest.getBonusCount()
            savedQuestBonusCount = getWinbackSetting(Winback.COMPLETED_STARTING_QUEST_COUNT)
            if questBonusCount > savedQuestBonusCount:
                setWinbackSetting(Winback.COMPLETED_STARTING_QUEST_COUNT, questBonusCount)
                setWinbackSetting(Winback.INTRO_SHOWN, False)
                setWinbackSetting(Winback.BATTLE_SELECTOR_SETTINGS_BULLET_SHOWN, False)
            return
