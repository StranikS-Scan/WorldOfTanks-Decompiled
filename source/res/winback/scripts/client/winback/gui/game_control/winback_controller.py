# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/game_control/winback_controller.py
from enum import Enum
import logging
import typing
import Event
from PlayerEvents import g_playerEvents
from account_helpers.AccountSettings import Winback
from constants import Configs, WINBACK_SELECTOR_HINT_TOKEN
from gui.impl import backport
from gui.impl.gen import R
from gui.macroses import getLanguageCode
from gui.prb_control.entities.listener import IGlobalListener
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.daapi.view.lobby.hangar.hangar_header import HangarHeader, getFlagIconAndLabel
from gui.server_events.event_items import Quest
from helpers import dependency
from helpers import time_utils
from skeletons.gui.game_control import IWinbackController, IVersusAIController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from winback.gui.game_control.winback_hints_controller import WinbackHintsController
from winback.gui.game_control.winback_progression_controller import WinbackProgressionController
from winback.gui.shared.event_dispatcher import showWinbackIntroView
from winback.gui.winback_helpers import getWinbackSetting, setWinbackSetting
if typing.TYPE_CHECKING:
    from helpers.server_settings import WinbackConfig
_logger = logging.getLogger(__name__)

class _WinbackState(Enum):
    NOT_STARTED = 0
    IN_PROGRESS = 1
    FINISHED = 2


class WinbackController(IWinbackController, IGlobalListener):
    __slots__ = ('__state', '__activeProgressionKey', '__winbackProgressionController', '__winbackHintsController')
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __eventsCache = dependency.descriptor(IEventsCache)
    __versusAIController = dependency.descriptor(IVersusAIController)

    def __init__(self):
        super(WinbackController, self).__init__()
        self.onConfigUpdated = Event.Event()
        self.onStateUpdated = Event.Event()
        self.onTokensUpdated = Event.Event()
        self.__winbackProgressionController = WinbackProgressionController(self)
        self.__winbackHintsController = WinbackHintsController()
        self.__state = None
        self.__activeProgressionKey = None
        return

    def init(self):
        super(WinbackController, self).init()
        self.__winbackProgressionController.init()
        self.__addWidgetHandler()
        g_playerEvents.onClientUpdated += self.__onTokensUpdate

    def fini(self):
        self.__winbackProgressionController.fini()
        self.__winbackHintsController.fini()
        self.__winbackHintsController = None
        self.__clearListeners()
        self.__removeWidgetHandler()
        g_playerEvents.onClientUpdated -= self.__onTokensUpdate
        super(WinbackController, self).fini()
        return

    def onLobbyInited(self, event):
        self.startGlobalListening()
        self.__showIntroIfNeeded()

    def onLobbyStarted(self, *_):
        self.__addListeners()
        self.__updateSettings()
        self.__updateWinbackAccountSettings()

    def onAccountBecomeNonPlayer(self):
        self.stopGlobalListening()
        self.__clearListeners()

    def onPrbEntitySwitched(self):
        if not self.isVersusAIPrbActive():
            if self.__hasSelectorHintToken():
                self.__winbackHintsController.markSelectorHintAsSeen()
            if self.__hasVersusAIIsDefaultModeToken():
                setWinbackSetting(Winback.HAS_LEFT_VERSUS_AI_FROM_WINBACK, True)

    @property
    def winbackConfig(self):
        return self.__lobbyContext.getServerSettings().winbackConfig

    @property
    def activeProgressionConfig(self):
        return self.winbackConfig.progressions.get(self.__activeProgressionKey, {})

    @property
    def winbackProgression(self):
        return self.__winbackProgressionController

    @property
    def winbackQuests(self):
        return self.winbackProgression.questContainer.getQuests()

    @property
    def progressionName(self):
        return self.activeProgressionConfig.get('progressionName')

    @property
    def winbackPromoURL(self):
        return self.activeProgressionConfig.get('promoURL', '').format(languageCode=getLanguageCode())

    @property
    def winbackInfoPageURL(self):
        return self.activeProgressionConfig.get('infoPageUrl', '').format(languageCode=getLanguageCode())

    @property
    def accessToken(self):
        return self.activeProgressionConfig.get('accessToken')

    @property
    def progressionToken(self):
        return self.activeProgressionConfig.get('progressionToken')

    def isEnabled(self):
        return self.winbackConfig.isEnabled and self.__versusAIController.isEnabled()

    def isWidgetEnabled(self):
        return self.isEnabled() and self.isVersusAIPrbActive()

    def isProgressionEnabled(self):
        return self.__winbackProgressionController.isEnabled

    def isVersusAIPrbActive(self):
        return self.__versusAIController.isVersusAIPrbActive()

    def isFinished(self):
        return self.__winbackProgressionController.isFinished

    def isWinbackQuest(self, quest):
        if quest is None or not self.winbackConfig.isEnabled:
            return False
        else:
            questId = quest if isinstance(quest, str) else quest.getID()
            return self.__winbackProgressionController.questContainer.hasQuestId(questId)

    def isWinbackOfferToken(self, offerToken):
        if not self.winbackConfig.isEnabled:
            return False
        offerTokenPrefix = self.activeProgressionConfig.get('offerTokenPrefix')
        return offerToken.startswith(offerTokenPrefix) if offerTokenPrefix else False

    def hasWinbackOfferGiftToken(self):
        tokens = self.__itemsCache.items.tokens.getTokens()
        return any((self._isWinbackOfferGiftToken(token) for token in tokens))

    def winbackOfferGiftTokenCount(self):
        tokens = self.__itemsCache.items.tokens.getTokens()
        return sum((1 for token in tokens if self._isWinbackOfferGiftToken(token)))

    def isPromoEnabled(self):
        return self.isEnabled() and self.isProgressionEnabled() and self.__hasPromoToken() and not self.__isInQueue()

    def versusAIModeShouldBeDefault(self):
        return not getWinbackSetting(Winback.HAS_LEFT_VERSUS_AI_FROM_WINBACK) and self.winbackConfig.isEnabled and self.__versusAIController.isEnabled() and self.__hasVersusAIIsDefaultModeToken()

    def getHeaderFlagState(self):
        if not self.isEnabled():
            return {'visible': False}
        quests = self.__winbackProgressionController.questContainer.getAvailableQuests()
        totalCount = len(quests)
        completedQuests = len([ q for q in quests.itervalues() if q.isCompleted() ])
        flagIcon, label = getFlagIconAndLabel(totalCount, completedQuests)
        return {'visible': True,
         'enable': self.isProgressionEnabled() and totalCount > 0,
         'flagIcon': flagIcon,
         'flagLabel': label,
         'flagMain': self.__getHangarFlag(),
         'tooltip': TOOLTIPS_CONSTANTS.WINBACK_QUESTS_PREVIEW}

    def __getHangarFlag(self):
        imageName = 'versus_ai_{}'.format(self.progressionName)
        image = R.images.gui.maps.icons.library.hangarFlag.dyn(imageName)
        return backport.image(image()) if image.isValid() else None

    def _isWinbackOfferGiftToken(self, token):
        return self.isWinbackOfferToken(token) and token.endswith('_gift')

    def __addListeners(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsUpdate
        self.__itemsCache.onSyncCompleted += self.__onSyncCompleted
        self.__eventsCache.onSyncCompleted += self.__onSyncCompleted
        self.__eventsCache.onSyncCompleted += self.__updateWinbackAccountSettings

    def __clearListeners(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsUpdate
        self.__itemsCache.onSyncCompleted -= self.__onSyncCompleted
        self.__eventsCache.onSyncCompleted -= self.__onSyncCompleted
        self.__eventsCache.onSyncCompleted -= self.__updateWinbackAccountSettings

    def __onTokensUpdate(self, diff, _):
        tokens = diff.get('tokens', {})
        if not tokens:
            return
        else:
            if self.winbackConfig.versusAIIsDefaultModeToken in tokens and tokens[self.winbackConfig.versusAIIsDefaultModeToken] is None:
                self.__resetLeftVersusAIMarker()
            if any((token.endswith(':access') for token in tokens.keys())):
                self.__updateSettings()
            self.onTokensUpdated(tokens)
            return

    def __onServerSettingsUpdate(self, diff):
        if Configs.WINBACK_CONFIG.value in diff:
            self.__updateSettings(force=True)
            self.onConfigUpdated()

    def __onSyncCompleted(self, *_):
        self.__updateSettings()

    def __updateSettings(self, force=False):
        activeProgressionKey = self.__getActiveProgressionKey()
        isProgressionSwitched = False
        if self.__activeProgressionKey != activeProgressionKey:
            self.__activeProgressionKey = activeProgressionKey
            isProgressionSwitched = True
        isProgressionSwitched = isProgressionSwitched or self.isProgressionEnabled() != self.activeProgressionConfig.get('isProgressionEnabled', False)
        if force or isProgressionSwitched:
            self.__winbackProgressionController.setSettings(self.activeProgressionConfig, isProgressionSwitched)
        self.__updateWinbackHintController()
        self.__updateState()

    def __updateWinbackHintController(self):
        isActive = self.isEnabled() and self.isProgressionEnabled() and self.__hasSelectorHintToken()
        self.__winbackHintsController.updateState(isActive)

    @classmethod
    def __hasSelectorHintToken(cls):
        return cls.__itemsCache.items.tokens.isTokenAvailable(WINBACK_SELECTOR_HINT_TOKEN)

    def __getActiveProgressionKey(self):
        for key, item in self.winbackConfig.progressions.items():
            accessToken = item.get('accessToken')
            if accessToken and self.__itemsCache.items.tokens.isTokenAvailable(accessToken):
                return key

        return self.winbackConfig.defaultProgression

    def __hasAccessToken(self):
        return self.__itemsCache.items.tokens.isTokenAvailable(self.accessToken)

    def __hasVersusAIIsDefaultModeToken(self):
        return self.__itemsCache.items.tokens.isTokenAvailable(self.winbackConfig.versusAIIsDefaultModeToken)

    def __hasPromoToken(self):
        promoToken = self.activeProgressionConfig.get('showPromoToken')
        return self.__itemsCache.items.tokens.isTokenAvailable(promoToken)

    def __updateState(self):
        if self.isFinished():
            newState = _WinbackState.FINISHED
        elif self.__hasAccessToken():
            newState = _WinbackState.IN_PROGRESS
        else:
            newState = _WinbackState.NOT_STARTED
        if newState != self.__state:
            self.__state = newState
            self.onStateUpdated()

    def __showIntroIfNeeded(self):
        if getWinbackSetting(Winback.NEED_SHOW_INTRO) and self.isEnabled() and self.__hasAccessToken() and self.isVersusAIPrbActive():
            self.__showIntroWindow()
            setWinbackSetting(Winback.NEED_SHOW_INTRO, False)

    @staticmethod
    def __showIntroWindow():
        from gui.shared.utils.HangarSpace import g_execute_after_hangar_space_inited

        @g_execute_after_hangar_space_inited
        @dependency.replace_none_kwargs(guiLoader=IGuiLoader)
        def loadIntroView(guiLoader=None):
            view = guiLoader.windowsManager.getViewByLayoutID(R.views.winback.lobby.WinbackIntroView())
            if view is None:
                showWinbackIntroView()
            return

        loadIntroView()
        return

    def __updateWinbackAccountSettings(self, *_):
        if not self.isEnabled() or not self.__hasAccessToken() or self.__winbackProgressionController.getCurPoints() > 0:
            return
        currentTime = time_utils.getServerUTCTime()
        deltaTime = currentTime - getWinbackSetting(Winback.INTRO_LAST_TIME_SHOWN)
        if deltaTime > time_utils.ONE_WEEK:
            setWinbackSetting(Winback.INTRO_LAST_TIME_SHOWN, currentTime)
            self.__resetLeftVersusAIMarker()

    @staticmethod
    def __resetLeftVersusAIMarker():
        setWinbackSetting(Winback.NEED_SHOW_INTRO, True)
        setWinbackSetting(Winback.HAS_LEFT_VERSUS_AI_FROM_WINBACK, False)

    def __isInQueue(self):
        return self.prbEntity and self.prbEntity.isInQueue()

    def __addWidgetHandler(self):

        def decorator(fn):

            def wrapper(_):
                return fn()

            return wrapper

        HangarHeader.addExternalWidgetHandler(HANGAR_ALIASES.WINBACK_WIDGET, decorator(self.isWidgetEnabled))

    @staticmethod
    def __removeWidgetHandler():
        HangarHeader.removeExternalWidgetHandler(HANGAR_ALIASES.WINBACK_WIDGET)
