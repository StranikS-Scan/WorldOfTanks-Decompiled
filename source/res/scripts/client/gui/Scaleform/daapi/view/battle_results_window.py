# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle_results_window.py
import logging
from functools import partial
import BigWorld
import constants
from adisp import adisp_process
from constants import PremiumConfigs
from gui import SystemMessages
from gui import makeHtmlString
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.customization.progression_helpers import parseEventID
from gui.Scaleform.daapi.view.lobby.customization.sound_constants import SOUNDS
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBuyPremiumUrl
from gui.Scaleform.daapi.view.meta.BattleResultsMeta import BattleResultsMeta
from gui.Scaleform.framework.entities.View import ViewKey
from gui.battle_results import RequestEmblemContext, EMBLEM_TYPE
from gui.battle_results.settings import PROGRESS_ACTION
from gui.prb_control.dispatcher import g_prbLoader
from gui.server_events import events_dispatcher as quests_events
from gui.server_events.events_helpers import isC11nQuest
from gui.shared import event_bus_handlers, events, EVENT_BUS_SCOPE, g_eventBus
from gui.shared import event_dispatcher
from gui.shared.event_dispatcher import showProgressiveRewardWindow, showShop
from gui.shared.events import ViewEventType
from gui.sounds.ambients import BattleResultsEnv
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.game_control import IGameSessionController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
_logger = logging.getLogger(__name__)

def _wrapEmblemUrl(emblemUrl):
    return makeHtmlString('html_templates:lobby/battleResult', 'emblemUrl', {'url': emblemUrl})


class BattleResultsWindow(BattleResultsMeta):
    __battleResults = dependency.descriptor(IBattleResultsService)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __gameSession = dependency.descriptor(IGameSessionController)
    __appLoader = dependency.descriptor(IAppLoader)
    __itemsCache = dependency.descriptor(IItemsCache)
    __sound_env__ = BattleResultsEnv
    __metaclass__ = event_bus_handlers.EventBusListener

    def __init__(self, ctx):
        super(BattleResultsWindow, self).__init__()
        if 'arenaUniqueID' not in ctx:
            raise SoftException('Key "arenaUniqueID" is not found in context', ctx)
        if not ctx['arenaUniqueID']:
            raise SoftException('Value of "arenaUniqueID" must be greater than 0')
        self.__arenaUniqueID = ctx['arenaUniqueID']
        self.__dataSet = False

    def _onRegisterFlashComponent(self, viewPy, alias):
        viewPy.updateQuestsInfo(arenaUniqueID=self.__arenaUniqueID)

    def onWindowClose(self):
        self.destroy()

    @adisp_process
    def showEventsWindow(self, eID, eventType):
        if self.__canNavigate():
            if eventType == constants.EVENT_TYPE.C11N_PROGRESSION or isC11nQuest(eID):
                app = self.__appLoader.getApp()
                view = app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY_CUSTOMIZATION))
                if view is None:
                    lobbyHeaderNavigationPossible = yield self.__lobbyContext.isHeaderNavigationPossible()
                    if not lobbyHeaderNavigationPossible:
                        return
                if eventType == constants.EVENT_TYPE.C11N_PROGRESSION:
                    _, vehicleIntCD = parseEventID(eID)
                    vehicle = self.__itemsCache.items.getVehicleCopyByCD(vehicleIntCD)
                    if not vehicle.isCustomizationEnabled():
                        _logger.warning('Trying to open customization from PBS for incompatible vehicle.')
                        return
                    self.soundManager.playInstantSound(SOUNDS.SELECT)
            else:
                lobbyHeaderNavigationPossible = yield self.__lobbyContext.isHeaderNavigationPossible()
                if not lobbyHeaderNavigationPossible:
                    return
            quests_events.showMission(eID, eventType)
            self.destroy()
        return

    def saveSorting(self, iconType, sortDirection, bonusType):
        self.__battleResults.saveStatsSorting(bonusType, iconType, sortDirection)

    def getClanEmblem(self, textureID, clanDBID):
        self.__requestClanEmblem(textureID, clanDBID)

    def startCSAnimationSound(self, soundEffectID='cs_animation_league_up'):
        self.app.soundManager.playEffectSound(soundEffectID)

    def onResultsSharingBtnPress(self):
        raise NotImplementedError('This feature is not longer supported')

    def showUnlockWindow(self, itemID, unlockType):
        if not self.__canNavigate():
            return
        if unlockType in (PROGRESS_ACTION.RESEARCH_UNLOCK_TYPE, PROGRESS_ACTION.PURCHASE_UNLOCK_TYPE):
            event_dispatcher.showResearchView(itemID)
            self.onWindowClose()
        elif unlockType in (PROGRESS_ACTION.NEW_SKILL_UNLOCK_TYPE, PROGRESS_ACTION.NEW_FREE_SKILL_UNLOCK_TYPE):
            event_dispatcher.showPersonalCase(itemID)

    def showDogTagWindow(self, itemID):
        if self.__canNavigate():
            event_dispatcher.showDogTags(itemID, False)
            self.destroy()

    def showProgressiveRewardView(self):
        showProgressiveRewardWindow()

    def onAppliedPremiumBonus(self):
        self.__battleResults.applyAdditionalBonus(self.__arenaUniqueID)

    def onShowDetailsPremium(self):
        if self.__canNavigate():
            url = getBuyPremiumUrl()
            BigWorld.callback(0.0, partial(showShop, url))
            self.destroy()

    def _populate(self):
        super(BattleResultsWindow, self)._populate()
        g_eventBus.addListener(events.LobbySimpleEvent.PREMIUM_XP_BONUS_CHANGED, self.__updateVO)
        g_eventBus.addListener(events.LobbySimpleEvent.BATTLE_RESULTS_SHOW_QUEST, self.__onBattleResultWindowShowQuest)
        g_eventBus.addListener(ViewEventType.LOAD_VIEW, self.__loadViewHandler, EVENT_BUS_SCOPE.LOBBY)
        g_clientUpdateManager.addCallbacks({'account._additionalXPCache': self.__updateVO,
         'inventory.1': self.__updateVO,
         'inventory.8': self.__updateVO,
         'cache.vehsLock': self.__updateVO})
        self.__gameSession.onPremiumTypeChanged += self.__onPremiumStateChanged
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        if self.__battleResults.areResultsPosted(self.__arenaUniqueID):
            self.__setBattleResults()

    def _dispose(self):
        g_eventBus.removeListener(events.LobbySimpleEvent.PREMIUM_XP_BONUS_CHANGED, self.__updateVO)
        g_eventBus.removeListener(events.LobbySimpleEvent.BATTLE_RESULTS_SHOW_QUEST, self.__onBattleResultWindowShowQuest)
        g_eventBus.removeListener(ViewEventType.LOAD_VIEW, self.__loadViewHandler, EVENT_BUS_SCOPE.LOBBY)
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__gameSession.onPremiumTypeChanged -= self.__onPremiumStateChanged
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange

    def __loadViewHandler(self, event):
        if event.alias == VIEW_ALIAS.BATTLE_QUEUE:
            self.as_setIsInBattleQueueS(True)
        elif event.alias == VIEW_ALIAS.LOBBY_HANGAR:
            self.as_setIsInBattleQueueS(False)

    @adisp_process
    def __requestClanEmblem(self, textureID, clanDBID):
        emblemID = yield self.__battleResults.requestEmblem(RequestEmblemContext(EMBLEM_TYPE.CLAN, clanDBID, textureID))
        if not self.isDisposed():
            self.as_setClanEmblemS(textureID, _wrapEmblemUrl(emblemID))

    def __setBattleResults(self):
        if not self.__dataSet:
            battleResultsVO = self.__battleResults.getResultsVO(self.__arenaUniqueID)
            self.as_setDataS(battleResultsVO)
            self.__dataSet = True

    @event_bus_handlers.eventBusHandler(events.LobbySimpleEvent.BATTLE_RESULTS_POSTED, EVENT_BUS_SCOPE.LOBBY)
    def __handleBattleResultsPosted(self, event):
        ctx = event.ctx
        if 'arenaUniqueID' not in ctx:
            raise SoftException('Key "arenaUniqueID" is not found in context', ctx)
        if not ctx['arenaUniqueID']:
            raise SoftException('Value of "arenaUniqueID" must be greater than 0')
        if self.__arenaUniqueID == ctx['arenaUniqueID']:
            self.__setBattleResults()

    @event_bus_handlers.eventBusHandler(events.HideWindowEvent.HIDE_BATTLE_RESULT_WINDOW, EVENT_BUS_SCOPE.LOBBY)
    def __handleBattleResultsClose(self, _):
        self.destroy()

    @classmethod
    def __canNavigate(cls):
        prbDispatcher = g_prbLoader.getDispatcher()
        if prbDispatcher is not None and prbDispatcher.getFunctionalState().isNavigationDisabled():
            SystemMessages.pushI18nMessage('#system_messages:queue/isInQueue', type=SystemMessages.SM_TYPE.Error)
            return False
        else:
            return True

    def __onPremiumStateChanged(self, *_):
        self.__updateVO()

    def __onBattleResultWindowShowQuest(self, event):
        ctx = event.ctx if event is not None else None
        if ctx is None:
            return
        else:
            if 'questId' in ctx and 'eventType' in ctx:
                self.showEventsWindow(ctx['questId'], ctx['eventType'])
            return

    def __updateVO(self, _=None):
        battleResultsVO = self.__battleResults.getResultsVO(self.__arenaUniqueID)
        self.as_setDataS(battleResultsVO)

    def __onServerSettingsChange(self, diff):
        if PremiumConfigs.DAILY_BONUS in diff:
            self.__updateVO()
