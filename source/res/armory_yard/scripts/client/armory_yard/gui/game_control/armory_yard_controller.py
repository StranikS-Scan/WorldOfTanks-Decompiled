# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/game_control/armory_yard_controller.py
import logging
import typing
from enum import Enum
from functools import partial
from typing import Dict
import adisp
import BigWorld
from account_helpers.AccountSettings import ArmoryYard, AccountSettings
from armory_yard.gui.server_events.events_helpers import getQuestsCompletedFunc
from armory_yard.skeletons.armory_yard_reroll_controller import IArmoryYardRerollController
from armory_yard_constants import getProgressionToken, getGroupName, getStageToken, getEndToken, getBundleBlockToken, PROGRESSION_LEVEL_PDATA_KEY, State, PDATA_KEY_ARMORY_YARD, INTRO_VIDEO, MAX_BUNDLE_TOKENS, isArmoryYardStyleQuest, DAY_BEFORE_END_STYLE_QUEST, VEHICLE_NAME, getPurchaseStagePaidEntitlement, getSubtrahendStageToken, getPostProgressionToken, getPostProgressionGroupName, POST_PROGRESSION_GROUP_PREFIX, CLAIMED_PROGRESSION_REWARD, CLAIMED_POST_PROGRESSION_REWARD, CONDITION_PREFIX, ARMORY_YARD_QUEST_PREFIX
from armory_yard.gui.window_events import showArmoryYardIntroWindow, showArmoryYardWaiting, hideArmoryYardWaiting, showArmoryYardVehiclePreview, showArmoryYardStylePreview
from armory_yard.gui.impl.lobby.feature.armory_yard_main_view import ArmoryYardMainView
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_main_view_model import TabId
from armory_yard.managers.sound_manager import setSoundDroneMode
from armory_yard.managers.camera_manager import CameraManager
from armory_yard.managers.scene_loading_manager import SceneLoadingManager
from constants import Configs, EVENT_TYPE
from gui.server_events.events_helpers import isArmoryYardQuest
from gui.shared.events import ArmoryYardEvent
from gui.shared.money import Money, Currency, ZERO_MONEY
from helpers import dependency, time_utils
from Event import Event, EventManager
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.server_events.event_items import Group
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.game_control.season_provider import SeasonProvider
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.scheduled_notifications import AcyclicNotifier, Notifiable, SimpleNotifier
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
from gui.Scaleform.framework import ScopeTemplates
from gui.clientgw.shop.contexts import ShopStorefrontProductsCtx
from helpers.server_settings import serverSettingsChangeListener
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.game_control import IArmoryYardController, IEntitlementsController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.gui.web import IWebController
from shared_utils import first
from armory_yard.managers.stage_manager import showVideo
from gui.impl.gen import R
from items import vehicles
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.impl import backport
from gui.shared.utils.functions import makeTooltip
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Tuple, Callable, List, Optional
    from season_common import GameSeason
    from armory_yard.gui.shared.armory_dynamic_quest import ArmoryDynamicQuest
    from gui.server_events.event_items import Quest
_logger = logging.getLogger(__name__)

class BundleState(Enum):
    EMPTY = 0
    FILLING = 1
    FILL = 2


class ArmoryYardController(IArmoryYardController):
    __eventsCache = dependency.descriptor(IEventsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __connectionMgr = dependency.descriptor(IConnectionManager)
    __appLoader = dependency.descriptor(IAppLoader)
    __webCtrl = dependency.descriptor(IWebController)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __entitlementsController = dependency.descriptor(IEntitlementsController)
    __rerollController = dependency.descriptor(IArmoryYardRerollController)
    __c11nService = dependency.descriptor(ICustomizationService)
    __BACKGROUND_ALPHA = 0

    def __init__(self):
        self.__eventManager = EventManager()
        self.onUpdated = Event(self.__eventManager)
        self.onProgressUpdated = Event(self.__eventManager)
        self.onQuestsUpdated = Event(self.__eventManager)
        self.onStatusChange = Event(self.__eventManager)
        self.onCheckNotify = Event(self.__eventManager)
        self.onAnnouncement = Event(self.__eventManager)
        self.onPayed = Event(self.__eventManager)
        self.onServerSwitchChange = Event(self.__eventManager)
        self.onStyleQuestEnds = Event(self.__eventManager)
        self.onCollectReward = Event(self.__eventManager)
        self.onPayedError = Event(self.__eventManager)
        self.onBundleOutTime = Event(self.__eventManager)
        self.onTabIdChanged = Event(self.__eventManager)
        self.onCollectFinalReward = Event(self.__eventManager)
        self.onBundlesDisabled = Event(self.__eventManager)
        self.onAYCoinsUpdate = Event(self.__eventManager)
        self.__serverSettings = _ServerSettings()
        self.__cameraManager = CameraManager()
        self.__sceneLoadingManager = SceneLoadingManager()
        self.__bundlesNotifier = AcyclicNotifier(self.__getBundlesTimer, self.onBundlesDisabled)
        self.__statusChangeNotifier = SimpleNotifier(self.__getTimeToStatusChange, self.__onNotifyStatusChange)
        self.__isPaused = False
        self.__isStarted = False
        self.__isVisiting = False
        self.__bundlesProducts = []
        self.__bundlesState = BundleState.EMPTY
        self.__isFinalQuestCompleted = False
        self.__currentSeason = None
        self.__currentSeasonID = None
        self.__maxNumberOfSteps = None
        self.__startStepOfPostProgression = None
        nationID, vehID = vehicles.g_list.getIDsByName(VEHICLE_NAME)
        self.__vehicleCD = vehicles.makeIntCompactDescrByID('vehicle', nationID, vehID)
        self.__isVehiclePreview = False
        super(ArmoryYardController, self).__init__()
        return

    @property
    def isArmoryVisiting(self):
        return self.__isVisiting

    @property
    def isVehiclePreview(self):
        return self.__isVehiclePreview

    @isVehiclePreview.setter
    def isVehiclePreview(self, value):
        self.__isVehiclePreview = value
        if self.__isVehiclePreview:
            self.__isVisiting = False

    @property
    def serverSettings(self):
        return self.__serverSettings

    @property
    def cameraManager(self):
        return self.__cameraManager

    @property
    def bundlesProducts(self):
        return self.__bundlesProducts

    @property
    def isFinalQuestCompleted(self):
        return self.__isFinalQuestCompleted

    @property
    def currentSeason(self):
        return self.__currentSeason or {}

    @property
    def currentSeasonID(self):
        return self.__currentSeasonID or 0

    @property
    def maxNumberOfSteps(self):
        return self.__maxNumberOfSteps or 0

    @property
    def startStepOfPostProgression(self):
        return self.__startStepOfPostProgression

    @property
    def rerollCtrl(self):
        return self.__rerollController

    def onLobbyInited(self, event):
        self.__serverSettings.start()
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate,
         'quests': self.__onQuestsUpdated,
         PDATA_KEY_ARMORY_YARD: self.__onPdataUpdated,
         'cache': self.__isCoinUpdate})
        self.__entitlementsController.onCacheUpdated += self.__bundlesCheck
        self.__itemsCache.onSyncCompleted += self.__bundlesCheck
        self.__serverSettings.onUpdated += self.__statusChangeNotifier.startNotification
        self.__serverSettings.onUpdated += self.__updateTimers
        self.__statusChangeNotifier.startNotification()
        self.__checkStyleQuest()
        self.__fillSeasonData()
        if self.isEnabled():
            self.__checkSeason()
            self.onCheckNotify()
            self.checkAnnouncement()
            self.__isPaused = self.serverSettings.isPaused
            if self.__bundlesState == BundleState.EMPTY:
                self.__fillBundlesProducts()
            if not self.__isStarted:
                self.__hangarSpace.onHeroTankReady += self.__checkRewards
            if self.isStarterPackAvailable():
                self.__bundlesNotifier.startNotification()
        self.__connectionMgr.onDisconnected += self.__onDisconnected
        self.__isStarted = True
        if self.maxNumberOfSteps == self.getProgressionTokenCount():
            self.__isFinalQuestCompleted = True

    def onAccountBecomeNonPlayer(self):
        self.__serverSettings.stop()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.unloadScene(False)
        self.__sceneLoadingManager.destroy()
        self.__cameraManager.destroy()
        self.__stopNotification()
        self.__entitlementsController.onCacheUpdated -= self.__bundlesCheck
        self.__itemsCache.onSyncCompleted -= self.__bundlesCheck

    def fini(self):
        self.__serverSettings.stop()
        self.__eventManager.clear()
        self.__sceneLoadingManager.destroy()
        self.__cameraManager.destroy()
        self.__stopNotification()
        self.__connectionMgr.onDisconnected -= self.__onDisconnected
        self.__entitlementsController.onCacheUpdated -= self.__bundlesCheck
        self.__itemsCache.onSyncCompleted -= self.__bundlesCheck

    def __onDisconnected(self):
        self.__isStarted = False
        self.__isPaused = False
        self.__isVisiting = False
        self.__bundlesState = BundleState.EMPTY
        self.__bundlesProducts = []
        self.__bundlesNotifier.stopNotification()

    def __fillSeasonData(self):
        self.__currentSeason = self.__serverSettings.getCurrentSeason()
        if self.__currentSeason:
            self.__currentSeasonID = self.__currentSeason.getSeasonID()
            self.__maxNumberOfSteps = self.__serverSettings.getModeSettings().rewards.get(self.currentSeasonID, {}).get('maxNumberOfSteps', 0)
            self.__startStepOfPostProgression = self.__serverSettings.getModeSettings().rewards.get(self.currentSeasonID, {}).get('startStepOfPostProgression', 0)

    def __isCoinUpdate(self, diff):
        if not self.currentSeason:
            return
        if getPurchaseStagePaidEntitlement(self.currentSeasonID) in diff.get('entitlements', {}):
            self.onAYCoinsUpdate()

    def isActive(self):
        return self.getState() not in (State.DISABLED, State.BEFOREPROGRESSION)

    def isQuestActive(self):
        return self.getState() not in (State.DISABLED, State.BEFOREPROGRESSION, State.PURCHASESTAGE)

    def isEnabled(self):
        startSeasonDate, _ = self.getSeasonInterval()
        return startSeasonDate is not None and self.__serverSettings.isEnabled()

    @property
    def isPaused(self):
        return self.__isPaused

    def isCompleted(self):
        totalTokens, receivedTokens = self.getTokensInfo()
        return totalTokens <= receivedTokens

    def isClaimedProgressionReward(self):
        data = self.__itemsCache.items.armoryYard.data
        return data is not None and data.get(CLAIMED_PROGRESSION_REWARD, False)

    def isClaimedPostProgressionReward(self):
        data = self.__itemsCache.items.armoryYard.data
        return data is not None and data.get(CLAIMED_POST_PROGRESSION_REWARD, False)

    def isProgressionQuest(self, questID):
        return questID.startswith(CONDITION_PREFIX) or questID.startswith(ARMORY_YARD_QUEST_PREFIX) or questID.startswith(POST_PROGRESSION_GROUP_PREFIX)

    def isPurchaseStageEnabled(self):
        return self.serverSettings.getModeSettings().purchaseStage.get('isEnabled', False)

    @property
    def maxBundleTokens(self):
        return self.serverSettings.getModeSettings().purchaseStage.get('maxBundleTokens', 0)

    def isPurchaseStageActive(self):
        return self.isPurchaseStageEnabled() and self.maxNumberOfSteps == self.getProgressionTokenCount()

    def bundleTokensLeft(self):
        if not self.maxBundleTokens or not self.currentSeason:
            return MAX_BUNDLE_TOKENS
        progressionTokensCount = self.getProgressionTokenCount()
        return max(self.maxBundleTokens - progressionTokensCount, 0)

    def isStarterPackAvailable(self):
        packsSettings = self.serverSettings.getModeSettings().starterPacks
        if not packsSettings.get('isEnabled', False) or not self.__bundlesProducts or self.__itemsCache.items.tokens.getTokenCount(self.getBundleBlockToken()) > 0:
            return False
        return packsSettings.get('startTime', 0) <= time_utils.getServerUTCTime() < packsSettings.get('endTime', 0)

    def iterProgressionQuests(self):
        for cycleID, _ in self.serverSettings.iterAllCycles():
            for quests in self.iterCycleProgressionQuests(cycleID):
                yield (cycleID, quests)

    def iterCycleProgressionQuests(self, cycleID):
        return self._iterProgressionQuests(getGroupName(cycleID))

    def _iterProgressionQuests(self, groupName):
        for questID in self.__eventsCache.getGroups().get(groupName, Group(0, {})).getGroupEvents():
            quest = self.__eventsCache.getQuestByID(questID)
            if quest is not None:
                if self.__rerollController.isRerollEnabled():
                    condQuests = self.__rerollController.getConditionQuestsByTokenQuest(quest)
                    if condQuests is not None:
                        yield condQuests
                elif quest.getType() == EVENT_TYPE.BATTLE_QUEST:
                    yield [quest]

        return

    def iterCyclePostProgressionQuests(self):
        return iter([]) if self.currentSeasonID is None else self._iterProgressionQuests(getPostProgressionGroupName(self.currentSeasonID))

    def isSceneLoaded(self):
        return self.__sceneLoadingManager.sceneIsLoaded()

    def getBundleBlockToken(self):
        return '' if self.currentSeason is None else getBundleBlockToken(self.currentSeasonID)

    def getNextCycle(self, currentTime=None):
        if currentTime is None:
            currentTime = time_utils.getServerUTCTime()
        curSeason = self.__serverSettings.getCurrentSeason()
        allCycles = curSeason.getAllCycles() if curSeason else {}
        for _, cycleData in sorted(allCycles.items()):
            if currentTime < cycleData.startDate:
                return cycleData

        return

    def getCollectableRewards(self):
        return self.getProgressionTokenCount() - self.getProgressionLevel()

    def getProgressionTokenCount(self):
        count = self.__eventsCache.questsProgress.getTokenCount(self.serverSettings.getProgressionToken())
        total = self.maxNumberOfSteps
        return count if count <= total else total

    def getProgressionLevel(self):
        return self.__itemsCache.items.armoryYard.progressionLevel

    def getCurrentProgress(self):
        return self.getProgressionTokenCount()

    @property
    def isPostProgressionState(self):
        return bool(self.__eventsCache.questsProgress.getTokenCount(self.serverSettings.getPostProgressionToken()))

    def getFinalRewardStep(self):
        postProgressionStartStep = self.startStepOfPostProgression
        return self.maxNumberOfSteps if not postProgressionStartStep else postProgressionStartStep

    def getFinalPostProgressionRewardStep(self):
        return 0 if self.currentSeason is None else self.maxNumberOfSteps

    def getStarterPackSettings(self):
        return self.serverSettings.getModeSettings().starterPacks

    def getStepsRewards(self):
        return {} if self.currentSeason is None else self.__serverSettings.getModeSettings().rewards.get(self.currentSeasonID, {}).get('steps', {})

    def getFinalRewardVehicle(self):
        vehicleBonus = self.getStepsRewards().get(self.getFinalRewardStep(), {}).get('vehicles', {})
        vehicleCD = next(iter(vehicleBonus.keys())) if vehicleBonus else None
        return self.__itemsCache.items.getItemByCD(vehicleCD) if vehicleCD is not None else None

    def getFinalProgressionRewardStyle(self):
        styleRewards = self.getStepsRewards().get(self.getFinalPostProgressionRewardStep(), {}).get('customizations', [])
        style = first(styleRewards, {})
        styleID = style.get('id')
        return self.__c11nService.getItemByID(GUI_ITEM_TYPE.STYLE, styleID) if styleID else None

    def getTokenCurrencies(self):
        currencies = self.__serverSettings.getModeSettings().tokenCost.keys()
        sortCurrencies = []
        for currency in Currency.BY_WEIGHT:
            if currency in currencies:
                sortCurrencies.append(currency)

        return sortCurrencies

    def getCurrencyTokenCost(self, currency):
        return Money.makeFrom(currency, self.__serverSettings.getModeSettings().tokenCost[currency]) if currency is not None and currency in self.__serverSettings.getModeSettings().tokenCost else ZERO_MONEY

    def refreshBundle(self):
        self.__fillBundlesProducts()

    def updateVisibilityHangarHeaderMenu(self, isVisible=False):
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.NOTHING if not isVisible else HeaderMenuVisibilityState.ALL}), EVENT_BUS_SCOPE.LOBBY)

    def __bundlesCheck(self, *_):
        if not self.__bundlesProducts:
            return
        bundleTokensLeft = self.bundleTokensLeft()
        idx = 0
        while idx < len(self.__bundlesProducts):
            if self.__bundlesProducts[idx]['tokens'] > bundleTokensLeft:
                self.__bundlesProducts = self.__bundlesProducts[:idx]
                break
            idx += 1

    @adisp.adisp_process
    def __fillBundlesProducts(self):
        if self.__bundlesState == BundleState.FILLING or self.__itemsCache.items.tokens.getTokenCount(self.getBundleBlockToken()) > 0:
            return
        packSettings = self.getStarterPackSettings()
        if not (not packSettings.get('isEnabled', False) or 'storefrontName' not in packSettings):
            if packSettings.get('startTime', 0) > time_utils.getServerUTCTime() >= packSettings.get('endTime', 0):
                return
            if not self.__webCtrl.isEnabled() and self.__webCtrl.isAvailable() and self.__webCtrl.isStarted:
                return
            self.__bundlesState = BundleState.FILLING
            result = yield self.__webCtrl.sendRequest(ctx=ShopStorefrontProductsCtx(storefront=packSettings['storefrontName'], userCountry='ru'))
            self.__bundlesState = BundleState.FILL
            return (not result.isSuccess() or not self.currentSeason) and None
        self.__bundlesProducts = []
        bundleTokensLeft = self.bundleTokensLeft()
        for product in result.getData().get('data', []):
            entitlements = product['entitlements']
            price = product['price']
            cost = float(price['value'])
            promotion = product.get('promotion', {})
            tokens = 0
            tokenName = getProgressionToken(self.currentSeasonID)
            if isinstance(promotion, Dict) and 'discounted_cost' in promotion:
                cost = float(promotion['discounted_cost'])
            for entitlement in entitlements:
                if tokenName == entitlement['cd']:
                    tokens = int(entitlement['amount'])
                    break

            if tokens == 0 or tokens > bundleTokensLeft:
                continue
            self.__bundlesProducts.append({'tokens': tokens,
             'tags': product['tags'],
             'price': Money.makeFrom(price['currency'], cost),
             'productCode': product['code'],
             'id': product['id']})

        self.__bundlesProducts.sort(key=lambda elem: elem['tokens'])

    def isChapterFinished(self, cycleID):
        return bool(self.__eventsCache.questsProgress.getTokenCount(getEndToken(cycleID)))

    def receivedTokensInChapter(self, cycleID):
        return self.__eventsCache.questsProgress.getTokenCount(self.__serverSettings.getStageToken(cycleID))

    def receivedTokensInPostProgressionChapter(self):
        return 0 if not self.isPostProgressionState else self.maxNumberOfSteps - self.startStepOfPostProgression - (self.maxNumberOfSteps - self.getProgressionTokenCount())

    def subtrahendStageToken(self):
        return self.__eventsCache.questsProgress.getTokenCount(getSubtrahendStageToken(self.currentSeasonID)) if self.currentSeason is not None else 0

    def getSeasonInterval(self):
        return (self.currentSeason.getStartDate(), self.currentSeason.getEndDate()) if self.currentSeason else (None, None)

    def getTokensInfo(self):
        return (self.maxNumberOfSteps, self.getProgressionTokenCount())

    def getTokensInfoMainProgression(self):
        return (self.startStepOfPostProgression, self.getProgressionTokenCount())

    def isAllTokensReceived(self):
        for cycleID, _ in self.serverSettings.iterAllCycles():
            if self.totalTokensInChapter(cycleID) > self.receivedTokensInChapter(cycleID) and not self.isChapterFinished(cycleID):
                return False

        return False if self.maxNumberOfSteps > self.getProgressionTokenCount() else True

    def totalTokensInChapter(self, cycleID):
        try:
            return self.serverSettings.getModeSettings().seasonsConfig[self.currentSeasonID][cycleID]['questsCount']
        except KeyError:
            _logger.error('[AY] Invalid SeasonConfig or cycleID')

    def totalTokensInPostProgressionChapter(self):
        try:
            return self.serverSettings.getModeSettings().postProgression[self.currentSeasonID]['questsCount']
        except KeyError:
            _logger.error('[AY] Invalid postProgressionData')

    def getCompensation(self):
        pass

    def getProgressionTimes(self):
        startProgressionTime = 0
        finishProgressionTime = 0
        for _, data in self.serverSettings.iterAllCycles():
            if not startProgressionTime or startProgressionTime > data.startDate:
                startProgressionTime = data.startDate
            if data.endDate > finishProgressionTime:
                finishProgressionTime = data.endDate

        return (startProgressionTime, finishProgressionTime)

    def getPurchaseStageTimes(self):
        startPurchaseStageTime = 0
        for _, data in self.serverSettings.iterAllCycles():
            if startPurchaseStageTime is None or startPurchaseStageTime < data.endDate:
                startPurchaseStageTime = data.endDate

        finishPurchaseStageTime = self.currentSeason.getEndDate()
        return (startPurchaseStageTime, finishPurchaseStageTime)

    def getAvailableQuestsCount(self):
        currentTime = time_utils.getServerUTCTime()
        isPrevChapterFinished = True
        count = 0
        allCycles = self.currentSeason.getAllCycles() if self.currentSeason else {}
        completedFunc = getQuestsCompletedFunc()
        for cycle in sorted(allCycles.values(), key=lambda item: item.ID):
            if currentTime > cycle.startDate and isPrevChapterFinished:
                count += len([ quests for quests in self.iterCycleProgressionQuests(cycle.ID) if not completedFunc(quests) ])
                isPrevChapterFinished = self.isChapterFinished(cycle.ID)

        if self.isPostProgressionState:
            ppCount = len([ quests for quests in self.iterCyclePostProgressionQuests() if not completedFunc(quests) ])
            count += min(ppCount, self.serverSettings.getPostProgressionData().get('availableQuestAtOneTime', 1))
        return count

    def getState(self):
        if self.serverSettings.isPaused or not self.isEnabled():
            return State.DISABLED
        currDate = time_utils.getCurrentLocalServerTimestamp()
        startProgressionTime, finishProgressionTime = self.getProgressionTimes()
        if currDate < startProgressionTime:
            return State.BEFOREPROGRESSION
        return State.PURCHASESTAGE if currDate >= finishProgressionTime else State.ACTIVE

    def goToArmoryYard(self, tabId=TabId.PROGRESS, ctx=None):
        loadShopBuyView = False
        loadBuyView = False
        loadRerollView = {}
        if not self.isActive():
            return
        else:
            if ctx is not None:
                loadShopBuyView = ctx.get('loadShopBuyView', False)
                loadBuyView = ctx.get('loadBuyView', False)
                loadRerollView = ctx.get('loadRerollView', {})
            if self.isCompleted():
                loadBuyView = False
            if self.__isVisiting:
                self.onTabIdChanged({'tabId': tabId})
                if loadBuyView:
                    g_eventBus.handleEvent(ArmoryYardEvent(ArmoryYardEvent.SHOW_ARMORY_YARD_BUY_VIEW), EVENT_BUS_SCOPE.DEFAULT)
                return
            self.isVehiclePreview = False
            app = self.__appLoader.getApp()
            app.setBackgroundAlpha(self.__BACKGROUND_ALPHA)

            def _loadedCallback():
                if loadBuyView:
                    g_eventBus.handleEvent(ArmoryYardEvent(ArmoryYardEvent.SHOW_ARMORY_YARD_BUY_VIEW, ctx={'onLoadedCallback': lambda : BigWorld.callback(0.0, hideArmoryYardWaiting)}), EVENT_BUS_SCOPE.DEFAULT)
                elif loadShopBuyView:
                    g_eventBus.handleEvent(ArmoryYardEvent(ArmoryYardEvent.SHOW_ARMORY_YARD_SHOP_BUY_VIEW, ctx={'productID': ctx.get('productID', 0),
                     'onLoadedCallback': lambda : BigWorld.callback(0.0, hideArmoryYardWaiting)}), EVENT_BUS_SCOPE.DEFAULT)
                elif loadRerollView:
                    g_eventBus.handleEvent(ArmoryYardEvent(ArmoryYardEvent.SHOW_ARMORY_YARD_REROLL_VIEW, ctx={'questId': loadRerollView.get('questId', ''),
                     'questsToSelect': loadRerollView.get('questsToSelect', []),
                     'onLoadedCallback': lambda : BigWorld.callback(0.0, hideArmoryYardWaiting)}), EVENT_BUS_SCOPE.DEFAULT)
                else:
                    BigWorld.callback(0.0, hideArmoryYardWaiting)

            showArmoryYardWaiting()
            if not self.__sceneLoadingManager.isLoading() and not self.__sceneLoadingManager.sceneIsLoaded():
                lastSeasonID = AccountSettings.getArmoryYard(ArmoryYard.ARMORY_YARD_LAST_INTRO_VIEWED) or -1
                isShowIntro = self.currentSeason is not None and lastSeasonID != self.currentSeasonID
                if isShowIntro:
                    showArmoryYardIntroWindow(partial(self.showIntroVideo, tabId))
                self.__sceneLoadingManager.loadScene(partial(self.goToArmoryYard, tabId, ctx) if not isShowIntro else hideArmoryYardWaiting)
                setSoundDroneMode(self.isPostProgressionState)
                return
            self.__isVisiting = True
            g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(R.views.armory_yard.lobby.feature.ArmoryYardMainView(), ArmoryYardMainView, ScopeTemplates.LOBBY_SUB_SCOPE), tabId, _loadedCallback), scope=EVENT_BUS_SCOPE.LOBBY)
            return

    def showIntroVideo(self, tabId):
        if INTRO_VIDEO is None:
            self.goToArmoryYard(tabId)
            return
        else:
            showVideo(INTRO_VIDEO, partial(self.goToArmoryYard, tabId))
            return

    def goToArmoryYardQuests(self):
        if self.isQuestActive():
            rerollContext = self.__rerollController.getRerollContext()
            self.goToArmoryYard(TabId.QUESTS, ctx=rerollContext)

    def goToArmoryYardShop(self):
        self.goToArmoryYard(TabId.SHOP)

    def unloadScene(self, isReload=True):
        self.__sceneLoadingManager.unloadScene(isReload=isReload)

    def onLoadingHangar(self):
        self.__sceneLoadingManager.unloadScene()
        self.__cameraManager.goToHangar()
        self.__cameraManager.destroy()
        self.__isVisiting = False

    def hasCurrentRewards(self):
        stepRewards = self.getStepsRewards()
        if not stepRewards:
            return False
        currentLevel = self.getProgressionLevel()
        nextLevel = currentLevel + self.getCollectableRewards()
        if nextLevel == self.maxNumberOfSteps:
            nextLevel -= 1
        for step in xrange(currentLevel + 1, nextLevel + 1):
            if step in stepRewards and step != self.startStepOfPostProgression:
                return True

        return False

    def update(self):
        self.__fillSeasonData()
        if self.isEnabled():
            self.__checkSeason()
            self.onCheckNotify()
            self.__fillBundlesProducts()
            if self.__isPaused != self.serverSettings.isPaused:
                self.__isPaused = self.serverSettings.isPaused
                self.onServerSwitchChange()
        self.onUpdated()

    def isInAnnouncement(self):
        return self.getState() == State.BEFOREPROGRESSION

    def checkAnnouncement(self):
        if self.getState() == State.BEFOREPROGRESSION:
            startTime, _ = self.getProgressionTimes()
            self.onAnnouncement(startTime)
        if not self.isActive():
            return
        announcementCountdown = self.serverSettings.getModeSettings().announcementCountdown * time_utils.ONE_HOUR
        nowTime = time_utils.getServerUTCTime()
        allCycles = self.currentSeason.getAllCycles() if self.currentSeason else {}
        for cycle in allCycles.values():
            if cycle.startDate > nowTime and cycle.startDate - nowTime <= announcementCountdown:
                self.onAnnouncement(cycle.startDate, cycle)

    def nextCycleStartsSoonProcessor(self, state):
        if state != State.ACTIVE or self.getAvailableQuestsCount() != 0:
            return (state, False)
        else:
            currentTime = time_utils.getServerUTCTime()
            nextCycle = self.getNextCycle(currentTime)
            return (State.ACTIVE, True) if nextCycle is not None and nextCycle.startDate - currentTime <= time_utils.ONE_DAY else (State.COMPLETED, False)

    def getHangarFlagData(self):
        iconsPath = R.images.armory_yard.gui.maps.icons.entry_point
        state = self.getState()
        state, isNextCycleStartsSoon = self.nextCycleStartsSoonProcessor(state)
        if state == State.ACTIVE and not isNextCycleStartsSoon:
            label = str(self.getAvailableQuestsCount())
            stateIcon = ''
        else:
            label = ''
            imageRes = iconsPath.dyn(state.value)
            stateIcon = backport.image(imageRes()) if imageRes.exists() else ''
        enabled = state in (State.ACTIVE, State.COMPLETED)
        return (enabled,
         backport.image(iconsPath.flag_disabled()),
         stateIcon,
         backport.image(iconsPath.anchor() if enabled else iconsPath.anchor_disabled()),
         self.__getFlagTooltip(state),
         label,
         state in (State.ACTIVE, State.COMPLETED, State.BEFOREPROGRESSION))

    def __getFlagTooltip(self, state):
        tooltipTexts = R.strings.armory_yard.entryPoint.tooltips
        if state == State.BEFOREPROGRESSION:
            return TOOLTIPS_CONSTANTS.ARMORY_YARD_ENTRY_POINT_BEFORE_PROGRESSION
        return makeTooltip(header=backport.text(tooltipTexts.disabled.header()), body=backport.text(tooltipTexts.disabled.body())) if state == State.DISABLED else TOOLTIPS_CONSTANTS.ARMORY_YARD_ENTRY_POINT_ACTIVE

    def __checkRewards(self):
        if self.getCollectableRewards() > int(self.isClaimedProgressionReward()):
            self.onCollectReward()
        self.__hangarSpace.onHeroTankReady -= self.__checkRewards

    def __checkSeason(self):
        season = self.serverSettings.getCurrentSeason()
        if not season:
            return
        seasonID = season.getSeasonID()
        if self.__settingsCore.serverSettings.getArmoryYardSeason() != seasonID:
            self.__settingsCore.serverSettings.setArmoryYardProgress(0)
            self.__settingsCore.serverSettings.setArmoryYardSeason(seasonID)
        if AccountSettings.getArmoryYard(ArmoryYard.ARMORY_YARD_CURRENT_SEASON) != seasonID:
            AccountSettings.clearArmoryYard()
            AccountSettings.setArmoryYard(ArmoryYard.ARMORY_YARD_CURRENT_SEASON, seasonID)

    def __checkStyleQuest(self):
        armoryYardStyleQuests = self.__eventsCache.getAllQuests(lambda q: isArmoryYardStyleQuest(q.getID()))
        nowTime = time_utils.getServerUTCTime()
        vehicle = self.__itemsCache.items.getItemByCD(self.__vehicleCD)
        for quest in armoryYardStyleQuests.values():
            isHotTime = 0 < quest.getFinishTime() - nowTime <= DAY_BEFORE_END_STYLE_QUEST * time_utils.ONE_DAY
            if not quest.isCompleted() and vehicle.inventoryCount > 0 and isHotTime:
                self.onStyleQuestEnds(quest.getFinishTime())

    def __onTokensUpdate(self, diff):
        if self.getBundleBlockToken() in diff:
            self.__bundlesProducts = []
        if self.serverSettings.getProgressionToken() in diff:
            if self.maxNumberOfSteps == self.getProgressionTokenCount():
                self.__isFinalQuestCompleted = True
            self.onProgressUpdated()
        for cycleID, _ in self.serverSettings.iterAllCycles():
            if getEndToken(cycleID) in diff or getStageToken(cycleID) in diff:
                self.onQuestsUpdated()
                break

    def getCycleTime(self, cycleID):
        return self.serverSettings.getCycleTime(cycleID)

    def __onPdataUpdated(self, diff):
        if PROGRESSION_LEVEL_PDATA_KEY in diff or CLAIMED_PROGRESSION_REWARD in diff:
            self.__checkSeason()
            self.onProgressUpdated()

    def __onQuestsUpdated(self, diff):
        for quest in diff:
            if isArmoryYardQuest(quest):
                return self.onQuestsUpdated()

    def __getTimeToStatusChange(self):
        self.__fillSeasonData()
        if self.isEnabled():
            nowTime = int(time_utils.getServerUTCTime())
            _, finishTime = self.getSeasonInterval()
            cycleData = self.currentSeason.getNextByTimeCycle(nowTime) if self.currentSeason else None
            if cycleData is not None:
                announcement = self.serverSettings.getModeSettings().announcementCountdown * time_utils.ONE_HOUR
                announcementDate = cycleData.startDate - announcement
                if announcementDate > nowTime:
                    return announcementDate - nowTime + 1
                if cycleData.startDate > nowTime:
                    return cycleData.startDate - nowTime + 1
            delta = self.currentSeason.getLastCycleInfo().endDate - nowTime
            if delta > 0:
                return delta + 1
            delta = finishTime - nowTime
            if delta > 0:
                return delta + 1
        else:
            nextSeason = self.serverSettings.seasonProvider.getNextSeason()
            if nextSeason is not None:
                nowTime = time_utils.getServerUTCTime()
                startTime = nextSeason.getStartDate()
                delta = startTime - nowTime
                if delta > 0:
                    return delta + 1
        return 0

    def __onNotifyStatusChange(self):
        self.__checkSeason()
        self.onStatusChange()
        self.onUpdated()
        self.onCheckNotify()
        self.checkAnnouncement()
        self.__fillBundlesProducts()

    def __stopNotification(self):
        self.__statusChangeNotifier.stopNotification()
        self.__bundlesNotifier.stopNotification()
        self.__serverSettings.onUpdated -= self.__statusChangeNotifier.startNotification
        self.__serverSettings.onUpdated -= self.__updateTimers

    def __getBundlesTimer(self):
        packsSettings = self.getStarterPackSettings()
        return packsSettings['endTime'] - time_utils.getServerUTCTime()

    def __updateTimers(self):
        self.__bundlesNotifier.stopNotification()
        if self.isActive() and self.isStarterPackAvailable():
            self.__bundlesNotifier.startNotification()

    def showVehiclePreview(self, isAnimationActive=False, disableAnimation=None, backCallback=None):
        vehicle = self.getFinalRewardVehicle()
        if vehicle is None:
            return
        else:
            if isAnimationActive:
                disableAnimation()
            self.isVehiclePreview = True
            backCallback = backCallback or self.goToArmoryYard
            showArmoryYardVehiclePreview(vehicle.intCD, backToHangar=False, showHeroTankText=False, previewBackCb=backCallback, backBtnLabel=backport.text(R.strings.armory_yard.buyView.backButton.mainView()))
            self.cameraManager.goToHangar()
            return

    def showStylePreview(self, isAnimationActive=False, disableAnimation=None, backLabel=None, backCallback=None):
        vehicle = self.getFinalRewardVehicle()
        if vehicle is None:
            return
        else:
            style = self.getFinalProgressionRewardStyle()
            if style is None:
                return
            if isAnimationActive:
                disableAnimation()
            self.isVehiclePreview = True
            backCallback = backCallback or self.goToArmoryYard
            backBtnDescrLabel = backLabel or backport.text(R.strings.armory_yard.buyView.backButton.mainView())
            showArmoryYardStylePreview(vehCD=vehicle.intCD, style=style, backCallback=backCallback, backBtnDescrLabel=backBtnDescrLabel)
            self.cameraManager.goToHangar()
            return

    def showShopStylePreview(self, styleID=None, backCallback=None):
        vehicle = self.getFinalRewardVehicle()
        if vehicle is None:
            return
        else:
            self.isVehiclePreview = True
            backCallback = backCallback or self.goToArmoryYardShop
            showArmoryYardStylePreview(style=self.__c11nService.getItemByID(GUI_ITEM_TYPE.STYLE, styleID) if styleID else None, backCallback=backCallback, backBtnDescrLabel=backport.text(R.strings.armory_shop.shopBuyView.backGoto()))
            self.cameraManager.goToHangar()
            return


class _ArmoryYardSeasonProvider(SeasonProvider):
    __slots__ = ('onUpdated', '__notificationManager')
    __armoryYardCtrl = dependency.descriptor(IArmoryYardController)

    def __init__(self):
        super(_ArmoryYardSeasonProvider, self).__init__()
        self.__notificationManager = Notifiable()
        self.__notificationManager.addNotificator(SimpleNotifier(self.getTimer, self.__onPrimeTimeUpdate))
        self.onUpdated = Event()

    def start(self):
        self.__notificationManager.startNotification()

    def stop(self):
        self.__notificationManager.stopNotification()

    def fini(self):
        self.stop()
        self.onUpdated.clear()
        self.__notificationManager.clearNotification()
        self.__notificationManager = None
        return

    def getModeSettings(self):
        return self.__armoryYardCtrl.serverSettings.getModeSettings()

    def getTimer(self, now=None, peripheryID=None):
        stateChange = self.getClosestStateChangeTime(now)
        stateDelta = stateChange - time_utils.getCurrentLocalServerTimestamp()
        return stateDelta + 1 if stateDelta > 0 else 0

    def onSettingsUpdated(self, diff):
        if 'seasons' not in diff and 'cycleTimes' not in diff:
            return
        self.__notificationManager.startNotification()

    def __onPrimeTimeUpdate(self):
        self.onUpdated()
        self.__armoryYardCtrl.update()
        self.__notificationManager.startNotification()


class _ServerSettings(object):
    __slots__ = ('__seasonProvider', 'onUpdated')
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __armoryYardCtrl = dependency.descriptor(IArmoryYardController)

    def __init__(self):
        super(_ServerSettings, self).__init__()
        self.__seasonProvider = _ArmoryYardSeasonProvider()
        self.onUpdated = Event()

    def start(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        self.__seasonProvider.start()

    def stop(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self.__seasonProvider.stop()

    def fini(self):
        self.stop()
        self.onUpdated.clear()
        self.__seasonProvider.fini()
        self.__seasonProvider = None
        return

    @property
    def seasonProvider(self):
        return self.__seasonProvider

    @property
    def isPaused(self):
        return self.getModeSettings().isPaused

    def iterAllCycles(self, now=None):
        curSeason = self.getCurrentSeason(now)
        allCycles = curSeason.getAllCycles() if curSeason else {}
        for cycleID, cycleData in sorted(allCycles.items()):
            yield (cycleID, cycleData)

    def getCycleInfo(self, cycleID, now=None):
        curSeason = self.getCurrentSeason(now)
        return curSeason.getCycleInfo(cycleID) if curSeason else None

    def getCycleTime(self, cycleID, now=None):
        cycleInfo = self.getCycleInfo(cycleID)
        return (cycleInfo.startDate, cycleInfo.endDate) if cycleInfo else (0, 0)

    def getPostProgressionData(self, seasonID=None):
        if seasonID is None:
            curSeason = self.__seasonProvider.getCurrentSeason()
            if curSeason is not None:
                seasonID = curSeason.getSeasonID()
        return self.getModeSettings().postProgression.get(seasonID, {})

    def getCurrentSeason(self, now=None):
        return self.__seasonProvider.getCurrentSeason(now)

    def getNextSeason(self, now=None):
        return self.__seasonProvider.getNextSeason(now)

    def getStageToken(self, cycleID=None):
        cycleID = cycleID or self.__seasonProvider.getCurrentCycleID()
        return '' if cycleID is None else getStageToken(cycleID)

    def getProgressionToken(self, seasonID=None):
        if seasonID is None:
            curSeason = self.__seasonProvider.getCurrentSeason()
            if curSeason is not None:
                seasonID = curSeason.getSeasonID()
        return '' if seasonID is None else getProgressionToken(seasonID)

    def getPostProgressionToken(self, seasonID=None):
        if seasonID is None:
            curSeason = self.__seasonProvider.getCurrentSeason()
            if curSeason is not None:
                seasonID = curSeason.getSeasonID()
        return '' if seasonID is None else getPostProgressionToken(seasonID)

    def isEnabled(self):
        return self.getModeSettings().isEnabled

    def getModeSettings(self):
        return self.__lobbyContext.getServerSettings().armoryYard

    def getDefaultConditionByQuestID(self, groupName, conditionID):
        return self.getModeSettings().getDefaultConditionByQuestID(groupName, conditionID)

    def iterByDefaultRerollQuests(self):
        return self.getModeSettings().iterByDefaultRerollQuests()

    @serverSettingsChangeListener(Configs.ARMORY_YARD_CONFIG.value)
    def __onServerSettingsChanged(self, diff, *args, **kwards):
        self.__seasonProvider.onSettingsUpdated(diff)
        self.onUpdated()
        self.__armoryYardCtrl.update()
