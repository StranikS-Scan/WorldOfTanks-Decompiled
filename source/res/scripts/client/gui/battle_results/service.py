# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/service.py
import logging
import Event
from adisp import async, process
from constants import PREMIUM_TYPE
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_WARNING
from gui import SystemMessages
from gui.Scaleform.locale.BATTLE_RESULTS import BATTLE_RESULTS
from gui.battle_results import composer
from gui.battle_results import emblems
from gui.battle_results import context
from gui.battle_results import reusable
from gui.battle_results import stored_sorting
from gui.battle_results.composer import StatsComposer
from gui.battle_results.settings import PREMIUM_STATE
from gui.shared import event_dispatcher
from gui.shared import g_eventBus, events
from gui.shared.utils import decorators
from gui.shared.gui_items.processors.common import BattleResultsGetter, PremiumBonusApplier
from helpers import dependency
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class BattleResultsService(IBattleResultsService):
    itemsCache = dependency.descriptor(IItemsCache)
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    lobbyContext = dependency.descriptor(ILobbyContext)
    __slots__ = ('__composers', '__buy', '__eventsManager', 'onResultPosted', '__appliedAddXPBonus')

    def __init__(self):
        super(BattleResultsService, self).__init__()
        self.__composers = {}
        self.__buy = set()
        self.__appliedAddXPBonus = set()
        self.__eventsManager = Event.EventManager()
        self.onResultPosted = Event.Event(self.__eventsManager)

    def init(self):
        g_eventBus.addListener(events.GUICommonEvent.LOBBY_VIEW_LOADED, self.__handleLobbyViewLoaded)
        g_eventBus.addListener(events.LobbySimpleEvent.PREMIUM_BOUGHT, self.__onPremiumBought)

    def fini(self):
        g_eventBus.removeListener(events.GUICommonEvent.LOBBY_VIEW_LOADED, self.__handleLobbyViewLoaded)
        g_eventBus.removeListener(events.LobbySimpleEvent.PREMIUM_BOUGHT, self.__onPremiumBought)
        self.clear()

    def clear(self):
        while self.__composers:
            _, item = self.__composers.popitem()
            item.clear()

        self.__eventsManager.clear()

    @async
    @process
    def requestResults(self, ctx, callback=None):
        arenaUniqueID = ctx.getArenaUniqueID()
        if ctx.needToShowImmediately():
            event_dispatcher.showBattleResultsWindow(arenaUniqueID)
        if not ctx.resetCache() and arenaUniqueID in self.__composers:
            isSuccess = True

            def dummy(callback=None):
                if callback is not None:
                    callback(None)
                return

            yield dummy
            self.__notifyBattleResultsPosted(arenaUniqueID, needToShowUI=ctx.needToShowIfPosted())
        else:
            results = yield BattleResultsGetter(arenaUniqueID).request()
            isSuccess = results.success
            if not results.success or not self.postResult(results.auxData, ctx.needToShowIfPosted()):
                self.__composers.pop(arenaUniqueID, None)
                event_dispatcher.hideBattleResults()
        if callback is not None:
            callback(isSuccess)
        return

    @async
    def requestEmblem(self, ctx, callback=None):
        fetcher = emblems.createFetcher(ctx)
        if fetcher is not None:
            fetcher.fetch(callback)
        else:
            LOG_WARNING('Icon fetcher is not found', ctx)
            if callback is not None:
                callback(None)
        return

    def postResult(self, result, needToShowUI=True):
        reusableInfo = reusable.createReusableInfo(result)
        if reusableInfo is None:
            SystemMessages.pushI18nMessage(BATTLE_RESULTS.NODATA, type=SystemMessages.SM_TYPE.Warning)
            return False
        else:
            self.__updateReusableInfo(reusableInfo)
            arenaUniqueID = reusableInfo.arenaUniqueID
            composerObj = composer.createComposer(reusableInfo)
            composerObj.setResults(result, reusableInfo)
            self.__composers[arenaUniqueID] = composerObj
            self.onResultPosted(reusableInfo, composerObj)
            self.__notifyBattleResultsPosted(arenaUniqueID, needToShowUI=needToShowUI)
            return True

    def areResultsPosted(self, arenaUniqueID):
        return arenaUniqueID in self.__composers

    def getResultsVO(self, arenaUniqueID):
        if arenaUniqueID in self.__composers:
            found = self.__composers[arenaUniqueID]
            vo = found.getVO()
        else:
            vo = None
        return vo

    def popResultsAnimation(self, arenaUniqueID):
        if arenaUniqueID in self.__composers:
            found = self.__composers[arenaUniqueID]
            vo = found.popAnimation()
        else:
            vo = None
        return vo

    def saveStatsSorting(self, bonusType, iconType, sortDirection):
        stored_sorting.writeStatsSorting(bonusType, iconType, sortDirection)

    @decorators.process('updating')
    def applyAdditionalBonus(self, arenaUniqueID):
        arenaInfo = self.__getAdditionalXPBattles().get(arenaUniqueID)
        if arenaInfo is None:
            return
        else:
            result = yield PremiumBonusApplier(arenaUniqueID, arenaInfo.vehicleID).request()
            if result and result.userMsg:
                SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
            if result.success:
                self.__appliedAddXPBonus.add(arenaUniqueID)
                self.__updateComposer(arenaUniqueID)
                self.__onAddXPBonusChanged()
            return

    def isAddXPBonusApplied(self, arenaUniqueID):
        return arenaUniqueID in self.__appliedAddXPBonus

    def isAddXPBonusEnabled(self, arenaUniqueID):
        return arenaUniqueID in self.__getAdditionalXPBattles() and self.itemsCache.items.stats.isPremium

    def getAdditionalXPValue(self, arenaUniqueID):
        arenaInfo = self.__getAdditionalXPBattles().get(arenaUniqueID)
        return 0 if arenaInfo is None else arenaInfo.extraXP

    def isCrewSameForArena(self, arenaUniqueID):
        arenaInfo = self.__getAdditionalXPBattles().get(arenaUniqueID)
        vehicle = self.getVehicleForArena(arenaUniqueID)
        if arenaInfo is not None and vehicle is not None:
            currentCrew = set((tankman.invID for _, tankman in vehicle.crew if tankman is not None))
            lastCrew = set((tankmanID for tankmanID, _ in arenaInfo.extraTmenXP))
            return currentCrew == lastCrew
        else:
            return False

    def isXPToTManSameForArena(self, arenaUniqueID):
        arenaInfo = self.__getAdditionalXPBattles().get(arenaUniqueID)
        vehicle = self.getVehicleForArena(arenaUniqueID)
        return vehicle.isXPToTman == arenaInfo.isXPToTMan if arenaInfo is not None and vehicle is not None else False

    def getVehicleForArena(self, arenaUniqueID):
        arenaInfo = self.__getAdditionalXPBattles().get(arenaUniqueID)
        return self.itemsCache.items.getItemByCD(arenaInfo.vehicleID) if arenaInfo is not None else None

    def __getAdditionalXPBattles(self):
        return self.itemsCache.items.stats.additionalXPCache

    @process
    def __showResults(self, ctx):
        yield self.requestResults(ctx)

    @staticmethod
    def __notifyBattleResultsPosted(arenaUniqueID, needToShowUI=False):
        if needToShowUI:
            event_dispatcher.showBattleResultsWindow(arenaUniqueID)
        event_dispatcher.notifyBattleResultsPosted(arenaUniqueID)

    def __handleLobbyViewLoaded(self, _):
        battleCtx = self.sessionProvider.getCtx()
        arenaUniqueID = battleCtx.lastArenaUniqueID
        if arenaUniqueID:
            try:
                self.__showResults(context.RequestResultsContext(arenaUniqueID))
            except Exception:
                LOG_CURRENT_EXCEPTION()

            battleCtx.lastArenaUniqueID = None
        return

    @process
    def __updateComposer(self, arenaUniqueID):
        results = yield BattleResultsGetter(arenaUniqueID).request()
        if results.success:
            result = results.auxData
            reusableInfo = reusable.createReusableInfo(result)
            if reusableInfo is None:
                SystemMessages.pushI18nMessage(BATTLE_RESULTS.NODATA, type=SystemMessages.SM_TYPE.Warning)
                return
            self.__updateReusableInfo(reusableInfo)
            arenaUniqueID = reusableInfo.arenaUniqueID
            composerObj = composer.createComposer(reusableInfo)
            composerObj.setResults(result, reusableInfo)
            self.__composers[arenaUniqueID] = composerObj
        return

    def __updateReusableInfo(self, reusableInfo):
        arenaUniqueID = reusableInfo.arenaUniqueID
        reusableInfo.premiumState = self.__makePremiumState(arenaUniqueID, PREMIUM_TYPE.BASIC)
        reusableInfo.premiumPlusState = self.__makePremiumState(arenaUniqueID, PREMIUM_TYPE.PLUS)
        reusableInfo.isAddXPBonusApplied = self.isAddXPBonusApplied(arenaUniqueID)
        reusableInfo.clientIndex = self.lobbyContext.getClientIDByArenaUniqueID(arenaUniqueID)

    def __onPremiumBought(self, event):
        ctx = event.ctx
        arenaUniqueID = event.ctx['arenaUniqueID']
        becomePremium = event.ctx['becomePremium']
        if becomePremium and arenaUniqueID:
            self.__buy.add(arenaUniqueID)
            event_dispatcher.hideBattleResults()
            self.__showResults(context.RequestResultsContext(arenaUniqueID, resetCache=True))

    def __makePremiumState(self, arenaUniqueID, premType=PREMIUM_TYPE.BASIC):
        state = PREMIUM_STATE.NONE
        settings = self.lobbyContext.getServerSettings()
        if settings is not None and settings.isPremiumInPostBattleEnabled():
            state |= PREMIUM_STATE.BUY_ENABLED
        if self.itemsCache.items.stats.isActivePremium(premType):
            state |= PREMIUM_STATE.HAS_ALREADY
        if arenaUniqueID in self.__buy:
            state |= PREMIUM_STATE.BOUGHT
        return state

    def __onAddXPBonusChanged(self):
        g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.PREMIUM_XP_BONUS_CHANGED))
