# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/service.py
import logging
import typing
import BigWorld
import Event
import personal_missions
from Account import PlayerAccount
from adisp import adisp_async, adisp_process
from constants import ARENA_BONUS_TYPE, PREMIUM_TYPE
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_WARNING
from gui import SystemMessages
from gui.Scaleform.locale.BATTLE_RESULTS import BATTLE_RESULTS
from gui.battle_results import composer, context, emblems, reusable, stored_sorting
from gui.battle_results.components.progress import VehicleProgressHelper
from gui.battle_results.composer import StatsComposer
from gui.battle_results.settings import PREMIUM_STATE
from gui.shared import event_dispatcher, events, g_eventBus
from gui.shared.gui_items.processors.common import BattleResultsGetter, PremiumBonusApplier
from gui.shared.utils import decorators
from helpers import dependency
from shared_utils import first
from shared_utils.account_helpers.battle_results_helpers import getEmptyClientPB20UXStats
from skeletons.gui.battle_matters import IBattleMattersController
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
from gui.battle_results.presenter.presenter import DataPresenter
_logger = logging.getLogger(__name__)

class BattleResultsService(IBattleResultsService):
    battleMatters = dependency.descriptor(IBattleMattersController)
    eventsCache = dependency.descriptor(IEventsCache)
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __slots__ = ('__composers', '__buy', '__eventsManager', 'onResultPosted', '__appliedAddXPBonus', '__presenter')

    def __init__(self):
        super(BattleResultsService, self).__init__()
        self.__composers = {}
        self.__buy = set()
        self.__appliedAddXPBonus = set()
        self.__eventsManager = Event.EventManager()
        self.onResultPosted = Event.Event(self.__eventsManager)
        self.__presenter = None
        return

    def init(self):
        self.__presenter = DataPresenter()
        g_eventBus.addListener(events.GUICommonEvent.LOBBY_VIEW_LOADED, self.__handleLobbyViewLoaded)
        g_eventBus.addListener(events.LobbySimpleEvent.PREMIUM_BOUGHT, self.__onPremiumBought)

    def fini(self):
        g_eventBus.removeListener(events.GUICommonEvent.LOBBY_VIEW_LOADED, self.__handleLobbyViewLoaded)
        g_eventBus.removeListener(events.LobbySimpleEvent.PREMIUM_BOUGHT, self.__onPremiumBought)
        self.clear()
        self.__presenter.fini()
        self.__presenter = None
        return

    def clear(self):
        while self.__composers:
            _, item = self.__composers.popitem()
            item.clear()

        self.__eventsManager.clear()
        self.__presenter.clear()

    @adisp_async
    @adisp_process
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
            if not results.success and ctx.getArenaBonusType() == ARENA_BONUS_TYPE.MAPS_TRAINING:
                results = yield self.waitForBattleResults(arenaUniqueID)
            isSuccess = results.success
            if not isSuccess or not self.postResult(results.auxData, ctx.needToShowIfPosted()):
                self.__composers.pop(arenaUniqueID, None)
                event_dispatcher.hideBattleResults()
        if callback is not None:
            callback(isSuccess)
        return

    @adisp_async
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
            self.__presenter.addBattleResult(reusableInfo, result)
            self.__composers[arenaUniqueID] = composerObj
            resultsWindow = self.__notifyBattleResultsPosted(arenaUniqueID, needToShowUI=needToShowUI)
            self.onResultPosted(reusableInfo, composerObj, resultsWindow)
            self.__postStatistics(reusableInfo, result)
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

    @property
    def presenter(self):
        return self.__presenter

    def popResultsAnimation(self, arenaUniqueID):
        if arenaUniqueID in self.__composers:
            found = self.__composers[arenaUniqueID]
            vo = found.popAnimation()
        else:
            vo = None
        return vo

    def saveStatsSorting(self, bonusType, iconType, sortDirection):
        stored_sorting.writeStatsSorting(bonusType, iconType, sortDirection)

    @decorators.adisp_process('updating')
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
                yield self.__updateComposer(arenaUniqueID, arenaInfo)
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

    def __postStatistics(self, reusableInfo, result):
        playerAccount = BigWorld.player()
        if playerAccount is None or not isinstance(playerAccount, PlayerAccount):
            raise SoftException('Could not post afterbattle statistics, possible not in hangar')
        if reusableInfo.common.arenaBonusType != ARENA_BONUS_TYPE.REGULAR:
            _logger.debug('Only random battles results are logging')
            return
        else:
            statisticsResult = getEmptyClientPB20UXStats()
            vehTypeCompDescr, vData = first(reusableInfo.personal.getVehicleCDsIterator(result['personal']))
            statisticsResult['vehTypeCompDescr'] = vehTypeCompDescr
            if reusableInfo.isPostBattlePremiumPlus:
                statisticsResult['premiumType'] = PREMIUM_TYPE.PLUS
            elif reusableInfo.isPostBattlePremium:
                statisticsResult['premiumType'] = PREMIUM_TYPE.BASIC
            else:
                statisticsResult['premiumType'] = PREMIUM_TYPE.NONE
            statisticsResult['timestamp'] = result['common'].get('arenaCreateTime', 0)
            statisticsResult['arenaTypeID'] = reusableInfo.common.arenaTypeID
            personalMissions = {}
            questsProgress = reusableInfo.personal.getQuestsProgress()
            if questsProgress:
                premiumQuests = self.eventsCache.getPremiumQuests()
                allCommonQuests = self.eventsCache.getQuests()
                allCommonQuests.update(self.eventsCache.getHiddenQuests(lambda q: q.isShowedPostBattle()))
                for qID, qProgress in questsProgress.iteritems():
                    _, pPrev, pCur = qProgress
                    isCompleted = pCur.get('bonusCount', 0) - pPrev.get('bonusCount', 0) > 0
                    if qID in allCommonQuests:
                        if qID in premiumQuests:
                            questType = 'premium'
                        else:
                            questType = 'other'
                        if isCompleted:
                            statisticsResult[questType + 'QuestsCompleted'] += 1
                        else:
                            statisticsResult[questType + 'QuestsInProgress'] += 1
                    if personal_missions.g_cache.isPersonalMission(qID):
                        pqID = personal_missions.g_cache.getPersonalMissionIDByUniqueID(qID)
                        questsCache = self.eventsCache.getPersonalMissions()
                        quest = questsCache.getAllQuests()[pqID]
                        personalMissions.setdefault(quest, {})[qID] = isCompleted

            pm2Progress = reusableInfo.personal.getPM2Progress()
            if pm2Progress:
                quests = self.eventsCache.getPersonalMissions().getAllQuests()
                for qID, data in pm2Progress.iteritems():
                    personalMissions.setdefault(quests[qID], {}).update(data)

            pmCompletedMain = 0
            pmCompletedFull = 0
            for quest, data in personalMissions.items():
                if data.get(quest.getAddQuestID(), False):
                    pmCompletedFull += 1
                if data.get(quest.getMainQuestID(), False):
                    pmCompletedMain += 1

            statisticsResult['personalMissionsInProgress'] = len(personalMissions) - pmCompletedMain - pmCompletedFull
            statisticsResult['personalMissionsCompletedFull'] = pmCompletedFull
            statisticsResult['personalMissionsCompletedMain'] = pmCompletedMain
            vehicleBattleXp = vData.get('xp', 0)
            pureCreditsReceived = vData.get('pureCreditsReceived', 0)
            tmenXps = dict(vData.get('xpByTmen', []))
            helper = VehicleProgressHelper(vehTypeCompDescr)
            ready2UnlockVehicles, ready2UnlockModules = helper.getReady2UnlockItems(vehicleBattleXp)
            ready2BuyVehicles, ready2BuyModules = helper.getReady2BuyItems(pureCreditsReceived)
            tankmen = helper.getNewSkilledTankmen(tmenXps)
            statisticsResult['vehicleProgressReady2UnlockVehicles'] = len(ready2UnlockVehicles)
            statisticsResult['vehicleProgressReady2UnlockModules'] = len(ready2UnlockModules)
            statisticsResult['vehicleProgressReady2BuyVehicles'] = len(ready2BuyVehicles)
            statisticsResult['vehicleProgressReady2BuyModules'] = len(ready2BuyModules)
            statisticsResult['vehicleProgressTankmen'] = len(tankmen)
            playerAccount.logClientPB20UXStats(statisticsResult)
            return

    def __getAdditionalXPBattles(self):
        return self.itemsCache.items.stats.additionalXPCache

    @adisp_process
    def __showResults(self, ctx):
        yield self.requestResults(ctx)

    def __notifyBattleResultsPosted(self, arenaUniqueID, needToShowUI=False):
        composerObj = self.__composers[arenaUniqueID]
        window = None
        if needToShowUI:
            window = composerObj.onShowResults(arenaUniqueID)
        composerObj.onResultsPosted(arenaUniqueID)
        return window

    def __handleLobbyViewLoaded(self, _):
        battleCtx = self.sessionProvider.getCtx()
        arenaUniqueID = battleCtx.lastArenaUniqueID
        arenaBonusType = battleCtx.lastArenaBonusType or ARENA_BONUS_TYPE.UNKNOWN
        if arenaUniqueID:
            try:
                self.__showResults(context.RequestResultsContext(arenaUniqueID, arenaBonusType))
            except Exception:
                LOG_CURRENT_EXCEPTION()

            battleCtx.lastArenaUniqueID = None
            battleCtx.lastArenaBonusType = None
        return

    @adisp_async
    @adisp_process
    def __updateComposer(self, arenaUniqueID, xpBonusData, callback):
        results = yield BattleResultsGetter(arenaUniqueID).request()
        if results.success:
            result = results.auxData
            reusableInfo = reusable.createReusableInfo(result)
            if reusableInfo is None:
                SystemMessages.pushI18nMessage(BATTLE_RESULTS.NODATA, type=SystemMessages.SM_TYPE.Warning)
                callback(False)
            self.__updateReusableInfo(reusableInfo, xpBonusData)
            arenaUniqueID = reusableInfo.arenaUniqueID
            composerObj = composer.createComposer(reusableInfo)
            composerObj.setResults(result, reusableInfo)
            self.__composers[arenaUniqueID] = composerObj
            self.__presenter.updateBattleResult(reusableInfo, result)
        callback(True)
        return

    def __updateReusableInfo(self, reusableInfo, xpBonusData=None):
        arenaUniqueID = reusableInfo.arenaUniqueID
        reusableInfo.premiumState = self.__makePremiumState(arenaUniqueID, PREMIUM_TYPE.BASIC)
        reusableInfo.premiumPlusState = self.__makePremiumState(arenaUniqueID, PREMIUM_TYPE.PLUS)
        isXPBonusApplied = self.isAddXPBonusApplied(arenaUniqueID)
        reusableInfo.isAddXPBonusApplied = isXPBonusApplied
        if xpBonusData:
            reusableInfo.updateXPEarnings(xpBonusData)
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

    @adisp_async
    @adisp_process
    def waitForBattleResults(self, arenaUniqueID, callback=None):

        @adisp_async
        def wait(t, callback):
            BigWorld.callback(t, lambda : callback(None))

        isSuccess = False
        results = None
        while not isSuccess:
            yield wait(1)
            results = yield BattleResultsGetter(arenaUniqueID).request()
            isSuccess = results.success

        if callback is not None:
            callback(results)
        return
