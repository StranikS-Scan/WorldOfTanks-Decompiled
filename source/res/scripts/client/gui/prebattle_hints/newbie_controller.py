# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prebattle_hints/newbie_controller.py
import random
from logging import getLogger
import typing
from account_helpers import AccountSettings
from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
from account_helpers.settings_core.settings_constants import GAME
from gui.shared import g_eventBus, events
from gui.shared.event_dispatcher import showPrebattleHintsConfirmWindow
from helpers import dependency
from hints_common.prebattle.newbie.consts import BATTLES_TYPES
from hints_common.prebattle.newbie.schemas import NewbieHintModel, hintSchema, configSchema
from skeletons.account_helpers.settings_core import ISettingsCore, ISettingsCache
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.prebattle_hints.controller import IPrebattleHintsController
from skeletons.gui.prebattle_hints.newbie_controller import INewbiePrebattleHintsController
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from hints_common.prebattle.schemas import BaseHintModel
IS_NEWBIE_MAX_BATTLES = 10
_PREFS_NAME = 'prebattle'
_PREFS_DISPLAY_COUNT = 'display_count'
_PREFS_CONFIRMATION = 'confirmation'
_COMPLETED_DISPLAY_COUNT = -1
_DISABLE_HISTORY_THRESHOLD = 50
_logger = getLogger(__name__)

class NewbiePrebattleHintsController(INewbiePrebattleHintsController):
    __hintsCtrl = dependency.descriptor(IPrebattleHintsController)
    __settings = dependency.descriptor(ISettingsCore)
    __settingsCache = dependency.descriptor(ISettingsCache)
    __itemsCache = dependency.descriptor(IItemsCache)
    __connMgr = dependency.descriptor(IConnectionManager)

    def __init__(self):
        super(NewbiePrebattleHintsController, self).__init__()
        self.__battlesCount = 0
        for arenaBonusType in BATTLES_TYPES:
            self.__hintsCtrl.addControlStrategy(arenaBonusType, self)

        g_eventBus.addListener(events.GUICommonEvent.LOBBY_VIEW_LOADED, self.__onLobbyInited)
        self.__connMgr.onDisconnected += self.__onDisconnected
        self.__itemsCache.onSyncCompleted += self.__onItemsCacheSynced

    def fini(self):
        for arenaBonusType in BATTLES_TYPES:
            self.__hintsCtrl.removeControlStrategy(arenaBonusType)

        g_eventBus.removeListener(events.GUICommonEvent.LOBBY_VIEW_LOADED, self.__onLobbyInited)
        self.__connMgr.onDisconnected -= self.__onDisconnected
        self.__itemsCache.onSyncCompleted -= self.__onItemsCacheSynced

    def hasHintToShow(self, _):
        return self.isEnabled() and self.__isUserSettingEnabled() and len(hintSchema.hints) > 0

    def getHintToShow(self, _):
        hintsCount = len(hintSchema.hints)
        if not hintsCount:
            return None
        else:
            displayCount = self.__setDefaultPrefs()[_PREFS_DISPLAY_COUNT]
            return hintSchema.hints[int(displayCount % hintsCount)] if displayCount != _COMPLETED_DISPLAY_COUNT else random.choice(hintSchema.hints)

    def onShowHintsWindowSuccess(self, hint):
        if not isinstance(hint, NewbieHintModel):
            return
        prefs = AccountSettings.getNewbieHints(_PREFS_NAME)
        displayCount = prefs[_PREFS_DISPLAY_COUNT]
        if displayCount != _COMPLETED_DISPLAY_COUNT:
            displayCount += 1
            if displayCount >= len(hintSchema.hints) * configSchema.getModel().hintDisplayCount:
                displayCount = _COMPLETED_DISPLAY_COUNT
                self.__settings.serverSettings.setSectionSettings(SETTINGS_SECTIONS.GAME_EXTENDED_2, {GAME.NEWBIE_PREBATTLE_HINTS: 0})
            prefs[_PREFS_DISPLAY_COUNT] = displayCount
            AccountSettings.setNewbieHints(_PREFS_NAME, prefs)

    def onConfirmationWindowShown(self):
        prefs = AccountSettings.getNewbieHints(_PREFS_NAME)
        prefs[_PREFS_CONFIRMATION] = True
        AccountSettings.setNewbieHints(_PREFS_NAME, prefs)

    def isEnabled(self):
        config = configSchema.getModel()
        return bool(config and config.enabled and self.__hintsCtrl.isEnabled())

    def __isUserSettingEnabled(self):
        return self.__settingsCache.isSynced() and self.__settings.getSetting(GAME.NEWBIE_PREBATTLE_HINTS)

    def __setDefaultPrefs(self):
        prefs = AccountSettings.getNewbieHints(_PREFS_NAME)
        if prefs is None:
            prefs = {_PREFS_DISPLAY_COUNT: 0,
             _PREFS_CONFIRMATION: False}
            if self.__battlesCount > _DISABLE_HISTORY_THRESHOLD:
                prefs[_PREFS_DISPLAY_COUNT] = _COMPLETED_DISPLAY_COUNT
                prefs[_PREFS_CONFIRMATION] = True
            AccountSettings.setNewbieHints(_PREFS_NAME, prefs)
        return prefs

    def __onLobbyInited(self, _):
        prefs = AccountSettings.getNewbieHints(_PREFS_NAME)
        if prefs is not None and prefs[_PREFS_DISPLAY_COUNT] == _COMPLETED_DISPLAY_COUNT and not prefs[_PREFS_CONFIRMATION]:
            showPrebattleHintsConfirmWindow()
        return

    def __onItemsCacheSynced(self, *_, **__):
        self.__battlesCount = self.__itemsCache.items.getAccountDossier().getTotalStats().getBattlesCount()

    def __onDisconnected(self):
        self.__battlesCount = 0
