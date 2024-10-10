# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/game_control/armory_yard_controller.py
from enum import Enum
from functools import partial
from typing import Dict
import adisp
import BigWorld
from account_helpers.AccountSettings import ArmoryYard, AccountSettings
from armory_yard_constants import getCurrencyToken, getGroupName, getStageToken, getEndToken, getEndQuestID, getBundleBlockToken, getFinalEndQuestID, PROGRESSION_LEVEL_PDATA_KEY, State, CLAIMED_FINAL_REWARD, PDATA_KEY_ARMORY_YARD, INTRO_VIDEO, MAX_PAID_TOKENS, isArmoryYardStyleQuest, DAY_BEFORE_END_STYLE_QUEST, AY_VIDEOS, VEHICLE_NAME, getPostProgressionPaidEntitlement, getSubtrahendStageToken
from armory_yard.gui.window_events import showArmoryYardIntroWindow, showArmoryYardWaiting, hideArmoryYardWaiting
from armory_yard.gui.impl.lobby.feature.armory_yard_main_view import ArmoryYardMainView
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_main_view_model import TabId
from armory_yard.managers.sound_manager import ArmorySoundManager
from armory_yard.managers.camera_manager import CameraManager
from armory_yard.managers.scene_loading_manager import SceneLoadingManager
from constants import Configs, EVENT_TYPE
from gui.shared.events import ArmoryYardEvent
from gui.shared.money import Money, Currency, ZERO_MONEY
from helpers import dependency, time_utils
from Event import Event, EventManager
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.server_events.event_items import Group
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.game_control.season_provider import SeasonProvider
from gui.shared.utils.scheduled_notifications import AcyclicNotifier, Notifiable, SimpleNotifier
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
from gui.Scaleform.framework import ScopeTemplates
from gui.wgcg.shop.contexts import ShopStorefrontProductsCtx
from helpers.server_settings import serverSettingsChangeListener
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.game_control import IArmoryYardController, IEntitlementsController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.gui.web import IWebController
from armory_yard.managers.stage_manager import showVideo
from gui.impl.gen import R
import ScaleformFileLoader
from gui.doc_loaders.GuiDirReader import GuiDirReader
from items import vehicles
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.impl import backport
from gui.shared.utils.functions import makeTooltip
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
AY_VIDEOS_FOLDER = '/'.join((GuiDirReader.SCALEFORM_STARTUP_VIDEO_PATH, 'armory_yard'))

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
        self.__soundManager = ArmorySoundManager()
        self.__cameraManager = CameraManager()
        self.__sceneLoadingManager = SceneLoadingManager()
        self.__bundlesNotifier = AcyclicNotifier(self.__getBundlesTimer, self.onBundlesDisabled)
        self.__statusChangeNotifier = SimpleNotifier(self.__getTimeToStatusChange, self.__onNotifyStatusChange)
        self.__isPaused = False
        self.__isStarted = False
        self.__isStreamingEnabled = False
        self.__isVisiting = False
        self.__bundlesProducts = []
        self.__bundlesState = BundleState.EMPTY
        self.__isFinalQuestCompleted = False
        nationID, vehID = vehicles.g_list.getIDsByName(VEHICLE_NAME)
        self.__vehicleCD = vehicles.makeIntCompactDescrByID('vehicle', nationID, vehID)
        self.__isVehiclePreview = False
        super(ArmoryYardController, self).__init__()

    def disableVideoStreaming(self):
        if self.__isStreamingEnabled:
            ScaleformFileLoader.disableStreaming()
            self.__isStreamingEnabled = False

    def enableVideoStreaming(self):
        if not self.__isStreamingEnabled:
            self.__isStreamingEnabled = True
            files = [ '/'.join((AY_VIDEOS_FOLDER, video)) for video in AY_VIDEOS ]
            ScaleformFileLoader.enableStreaming(files)

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
        if self.getTotalSteps() == self.getCurrencyTokenCount():
            self.__isFinalQuestCompleted = True

    def onAccountBecomeNonPlayer(self):
        self.__serverSettings.stop()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__soundManager.clear()
        self.__sceneLoadingManager.destroy()
        self.__cameraManager.destroy()
        self.__stopNotification()
        self.__entitlementsController.onCacheUpdated -= self.__bundlesCheck
        self.__itemsCache.onSyncCompleted -= self.__bundlesCheck

    def fini(self):
        self.__serverSettings.stop()
        self.__eventManager.clear()
        self.__soundManager.clear()
        self.__sceneLoadingManager.destroy()
        self.__cameraManager.destroy()
        self.__stopNotification()
        self.__connectionMgr.onDisconnected -= self.__onDisconnected
        self.__entitlementsController.onCacheUpdated -= self.__bundlesCheck
        self.__itemsCache.onSyncCompleted -= self.__bundlesCheck

    def __onDisconnected(self):
        self.__isStarted = False
        self.__isPaused = False
        self.__isStreamingEnabled = False
        self.__isVisiting = False
        self.__bundlesState = BundleState.EMPTY
        self.__bundlesProducts = []
        self.__bundlesNotifier.stopNotification()

    def __isCoinUpdate(self, diff):
        currSeason = self.serverSettings.getCurrentSeason()
        if currSeason and getPostProgressionPaidEntitlement(currSeason.getSeasonID()) in diff.get('entitlements', {}):
            self.onAYCoinsUpdate()

    def isActive(self):
        return self.getState() not in (State.DISABLED, State.BEFOREPROGRESSION)

    def isQuestActive(self):
        return self.getState() not in (State.DISABLED, State.BEFOREPROGRESSION, State.POSTPROGRESSION)

    def isEnabled(self):
        startSeasonDate, _ = self.getSeasonInterval()
        return startSeasonDate is not None and self.__serverSettings.isEnabled()

    def isCompleted(self):
        totalTokens, receivedTokens = self.getTokensInfo()
        return totalTokens <= receivedTokens

    def isClaimedFinalReward(self):
        data = self.__itemsCache.items.armoryYard.data
        return data is not None and data.get('claimedFinalReward', False)

    def isProgressionQuest(self, questID):
        return any([ quest.getID() == questID for _, quest in self.iterProgressionQuests() ])

    def isPostProgressionEnabled(self):
        return self.serverSettings.getModeSettings().postProgression.get('isEnabled', False)

    def isPostProgressionActive(self):
        return self.isPostProgressionEnabled() and self.getTotalSteps() == self.getCurrencyTokenCount()

    def payedTokensLeft(self):
        paidTokens = self.serverSettings.getModeSettings().postProgression.get('maxPaidTokens', 0)
        currSeason = self.serverSettings.getCurrentSeason()
        if not paidTokens or not currSeason:
            return MAX_PAID_TOKENS
        paidEntitlement = getPostProgressionPaidEntitlement(currSeason.getSeasonID())
        paidCount = self.__itemsCache.items.stats.entitlements.get(paidEntitlement, 0)
        return max(paidTokens - paidCount, 0)

    def isStarterPackAvailable(self):
        packsSettings = self.serverSettings.getModeSettings().starterPacks
        if not packsSettings.get('isEnabled', False) or not self.__bundlesProducts or self.__itemsCache.items.tokens.getTokenCount(self.getBundleBlockToken()) > 0:
            return False
        return packsSettings.get('startTime', 0) <= time_utils.getServerUTCTime() < packsSettings.get('endTime', 0)

    def iterProgressionQuests(self):
        for cycleID, _ in self.serverSettings.iterAllCycles():
            for quest in self.iterCycleProgressionQuests(cycleID):
                yield (cycleID, quest)

    def iterCycleProgressionQuests(self, cycleID):
        for questID in self.__eventsCache.getGroups().get(getGroupName(cycleID), Group(0, {})).getGroupEvents():
            quest = self.__eventsCache.getQuestByID(questID)
            if quest is not None and quest.getType() != EVENT_TYPE.TOKEN_QUEST:
                yield quest

        return

    def isSceneLoaded(self):
        return self.__sceneLoadingManager.sceneIsLoaded()

    def getBundleBlockToken(self):
        curSeason = self.__serverSettings.getCurrentSeason()
        return '' if curSeason is None else getBundleBlockToken(curSeason.getSeasonID())

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
        return self.getCurrencyTokenCount() - self.getProgressionLevel()

    def getCurrencyTokenCount(self):
        count = self.__eventsCache.questsProgress.getTokenCount(self.serverSettings.getCurrencyToken())
        total = self.getTotalSteps()
        return count if count <= total else total

    def getProgressionLevel(self):
        return self.__itemsCache.items.armoryYard.progressionLevel

    def getCurrentProgress(self):
        return self.getCurrencyTokenCount()

    def getTotalSteps(self):
        currentSeason = self.__serverSettings.getCurrentSeason()
        return 0 if currentSeason is None else self.__serverSettings.getModeSettings().rewards.get(currentSeason.getSeasonID(), {}).get('maxNumberOfSteps', 0)

    def getStarterPackSettings(self):
        return self.serverSettings.getModeSettings().starterPacks

    def getStepsRewards(self):
        currentSeason = self.__serverSettings.getCurrentSeason()
        return {} if currentSeason is None else self.__serverSettings.getModeSettings().rewards.get(currentSeason.getSeasonID(), {}).get('steps', {})

    def getFinalRewardVehicle(self):
        vehicleBonus = self.getStepsRewards().get(self.getTotalSteps(), {}).get('vehicles', {})
        vehicleCD = next(iter(vehicleBonus.keys())) if vehicleBonus else None
        return self.__itemsCache.items.getItemByCD(vehicleCD) if vehicleCD is not None else None

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

    @staticmethod
    def updateVisibilityHangarHeaderMenu(isVisible=False):
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.NOTHING if not isVisible else HeaderMenuVisibilityState.ALL}), EVENT_BUS_SCOPE.LOBBY)

    def __bundlesCheck(self, *_):
        if not self.__bundlesProducts:
            return
        payedTokensLeft = self.payedTokensLeft()
        idx = 0
        while idx < len(self.__bundlesProducts):
            if self.__bundlesProducts[idx]['tokens'] > payedTokensLeft:
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
            result = yield self.__webCtrl.sendRequest(ctx=ShopStorefrontProductsCtx(storefront=packSettings['storefrontName']))
            self.__bundlesState = BundleState.FILL
            currSeason = self.serverSettings.getCurrentSeason()
            return (not result.isSuccess() or not currSeason) and None
        self.__bundlesProducts = []
        payedTokensLeft = self.payedTokensLeft()
        seasonId = currSeason.getSeasonID()
        for product in result.getData().get('data', []):
            entitlements = product['entitlements']
            price = product['price']
            cost = float(price['value'])
            promotion = product.get('promotion', {})
            tokens = 0
            tokenName = getCurrencyToken(seasonId)
            if isinstance(promotion, Dict) and 'discounted_cost' in promotion:
                cost = float(promotion['discounted_cost'])
            for entitlement in entitlements:
                if tokenName == entitlement['cd']:
                    tokens = int(entitlement['amount'])
                    break

            if tokens == 0 or tokens > payedTokensLeft:
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

    def subtrahendStageToken(self):
        season = self.serverSettings.getCurrentSeason()
        return self.__eventsCache.questsProgress.getTokenCount(getSubtrahendStageToken(season.getSeasonID())) if season is not None else 0

    def getSeasonInterval(self):
        season = self.serverSettings.getCurrentSeason()
        return (season.getStartDate(), season.getEndDate()) if season else (None, None)

    def getTokensInfo(self):
        return (self.getTotalSteps(), self.getCurrencyTokenCount())

    def totalTokensInChapter(self, cycleID):
        quest = self.__eventsCache.getQuestByID(getEndQuestID(cycleID))
        if quest is None:
            return 0
        else:
            return sum([ token.getNeededCount() for token in quest.accountReqs.getTokens() if token.getID() == self.__serverSettings.getStageToken(cycleID) ])

    def getCompensation(self):
        pass

    def getProgressionTimes(self):
        startProgressionTime = None
        finishProgressionTime = 0
        for _, data in self.serverSettings.iterAllCycles():
            if startProgressionTime is None or startProgressionTime > data.startDate:
                startProgressionTime = data.startDate
            if data.endDate > finishProgressionTime:
                finishProgressionTime = data.endDate

        return (startProgressionTime, finishProgressionTime)

    def getPostProgressionTimes(self):
        startPostProgressionTime = None
        for _, data in self.serverSettings.iterAllCycles():
            if startPostProgressionTime is None or startPostProgressionTime < data.endDate:
                startPostProgressionTime = data.endDate

        finishPostProgressionTime = self.__serverSettings.getCurrentSeason().getEndDate()
        return (startPostProgressionTime, finishPostProgressionTime)

    def getAvailableQuestsCount(self):
        currentTime = time_utils.getServerUTCTime()
        isPrevChapterFinished = True
        count = 0
        curSeason = self.__serverSettings.getCurrentSeason()
        allCycles = curSeason.getAllCycles() if curSeason else {}
        for cycle in sorted(allCycles.values(), key=lambda item: item.ID):
            if currentTime > cycle.startDate and isPrevChapterFinished:
                count += sum([ not quest.isCompleted() for quest in self.iterCycleProgressionQuests(cycle.ID) ])
            isPrevChapterFinished = self.isChapterFinished(cycle.ID)

        return count

    def getState(self):
        if self.serverSettings.isPaused or not self.isEnabled():
            return State.DISABLED
        currDate = time_utils.getCurrentLocalServerTimestamp()
        startProgressionTime, finishProgressionTime = self.getProgressionTimes()
        if currDate < startProgressionTime:
            return State.BEFOREPROGRESSION
        return State.POSTPROGRESSION if currDate >= finishProgressionTime else State.ACTIVE

    def goToArmoryYard(self, tabId=TabId.PROGRESS, ctx=None):
        loadShopBuyView = False
        loadBuyView = False
        if not self.isActive():
            return
        else:
            if ctx is not None:
                loadShopBuyView = ctx.get('loadShopBuyView', False)
                loadBuyView = ctx.get('loadBuyView', False)
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
            self.enableVideoStreaming()

            def _loadedCallback():
                if loadBuyView:
                    g_eventBus.handleEvent(ArmoryYardEvent(ArmoryYardEvent.SHOW_ARMORY_YARD_BUY_VIEW, ctx={'onLoadedCallback': lambda : BigWorld.callback(0.0, hideArmoryYardWaiting)}), EVENT_BUS_SCOPE.DEFAULT)
                elif loadShopBuyView:
                    g_eventBus.handleEvent(ArmoryYardEvent(ArmoryYardEvent.SHOW_ARMORY_YARD_SHOP_BUY_VIEW, ctx={'productID': ctx.get('productID', 0),
                     'onLoadedCallback': lambda : BigWorld.callback(0.0, hideArmoryYardWaiting)}), EVENT_BUS_SCOPE.DEFAULT)
                else:
                    BigWorld.callback(0.0, hideArmoryYardWaiting)

            showArmoryYardWaiting()
            if not self.__sceneLoadingManager.isLoading() and not self.__sceneLoadingManager.sceneIsLoaded():
                currSeason = self.serverSettings.getCurrentSeason()
                lastSeasonID = AccountSettings.getArmoryYard(ArmoryYard.ARMORY_YARD_LAST_INTRO_VIEWED) or -1
                isShowIntro = currSeason is not None and lastSeasonID != currSeason.getSeasonID()
                if isShowIntro:
                    showArmoryYardIntroWindow(partial(self.showIntroVideo, tabId))
                self.__sceneLoadingManager.loadScene(partial(self.goToArmoryYard, tabId, ctx) if not isShowIntro else hideArmoryYardWaiting)
                self.__soundManager.onSoundModeChanged(True)
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
            self.goToArmoryYard(TabId.QUESTS)

    def unloadScene(self, isReload=True):
        self.__soundManager.onSoundModeChanged(False)
        self.__sceneLoadingManager.unloadScene(isReload=isReload)

    def onLoadingHangar(self):
        self.__soundManager.onSoundModeChanged(False)
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
        if nextLevel == self.getTotalSteps():
            nextLevel -= 1
        for step in xrange(currentLevel + 1, nextLevel + 1):
            if step in stepRewards:
                return True

        return False

    def update(self):
        if self.isEnabled():
            self.__checkSeason()
            self.onCheckNotify()
            self.checkAnnouncement()
            self.__fillBundlesProducts()
            if self.__isPaused != self.serverSettings.isPaused:
                self.__isPaused = self.serverSettings.isPaused
                self.onServerSwitchChange()
        self.onUpdated()

    def checkAnnouncement(self):
        if self.getState() == State.BEFOREPROGRESSION:
            startTime, _ = self.getProgressionTimes()
            self.onAnnouncement(startTime)
        if not self.isActive():
            return
        announcementCountdown = self.serverSettings.getModeSettings().announcementCountdown * time_utils.ONE_HOUR
        nowTime = time_utils.getServerUTCTime()
        curSeason = self.__serverSettings.getCurrentSeason()
        allCycles = curSeason.getAllCycles() if curSeason else {}
        for cycle in allCycles.values():
            if cycle.startDate > nowTime and cycle.startDate - nowTime <= announcementCountdown:
                self.onAnnouncement(cycle.startDate, cycle)

    def getHangarFlagData(self):
        iconsPath = R.images.armory_yard.gui.maps.icons.entry_point
        currentTime = time_utils.getServerUTCTime()
        _, finishProgressionTime = self.getProgressionTimes()
        deltaFinishProgressionTime = finishProgressionTime - currentTime
        state = self.getState()
        availableQuestsCount = self.getAvailableQuestsCount()
        enabled = state == State.ACTIVE
        if state == State.ACTIVE:
            nextCycle = self.getNextCycle(currentTime)
            if nextCycle is not None and nextCycle.startDate - currentTime <= time_utils.ONE_DAY:
                state = State.ACTIVE
            elif self.isQuestActive() and availableQuestsCount == 0:
                state = State.COMPLETED
        if state == State.ACTIVE and deltaFinishProgressionTime >= time_utils.ONE_DAY:
            label = str(availableQuestsCount)
            stateIcon = ''
        else:
            label = ''
            imageRes = iconsPath.dyn(state.value)
            stateIcon = backport.image(imageRes()) if imageRes.exists() else ''
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
        if state == State.POSTPROGRESSION:
            return makeTooltip(header=backport.text(tooltipTexts.postProgression.header()), body=backport.text(tooltipTexts.postProgression.body()))
        return makeTooltip(header=backport.text(tooltipTexts.disabled.header()), body=backport.text(tooltipTexts.disabled.body())) if state == State.DISABLED else TOOLTIPS_CONSTANTS.ARMORY_YARD_ENTRY_POINT_ACTIVE

    def __checkRewards(self):
        if self.getCollectableRewards() > int(self.isClaimedFinalReward()):
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
        if self.serverSettings.getCurrencyToken() in diff:
            self.onProgressUpdated()
        for cycleID, _ in self.serverSettings.iterAllCycles():
            if getEndToken(cycleID) in diff or getStageToken(cycleID) in diff:
                self.onQuestsUpdated()
                break

    def __onPdataUpdated(self, diff):
        if PROGRESSION_LEVEL_PDATA_KEY in diff or CLAIMED_FINAL_REWARD in diff:
            self.__checkSeason()
            self.onProgressUpdated()

    def __onQuestsUpdated(self, diff):
        if set([ quest.getID() for _, quest in self.iterProgressionQuests() ]) & set(diff):
            self.onQuestsUpdated()
        currentSeason = self.serverSettings.getCurrentSeason()
        if currentSeason and getFinalEndQuestID(currentSeason.getSeasonID()) in diff:
            self.__isFinalQuestCompleted = True
            self.onProgressUpdated()
            self.onCollectFinalReward()

    def __getTimeToStatusChange(self):
        if self.isEnabled():
            nowTime = time_utils.getServerUTCTime()
            _, finishTime = self.getSeasonInterval()
            currentSeason = self.serverSettings.getCurrentSeason()
            cycleData = currentSeason.getNextByTimeCycle(nowTime) if currentSeason else None
            if cycleData is not None:
                announcement = self.serverSettings.getModeSettings().announcementCountdown * time_utils.ONE_HOUR
                announcementDate = cycleData.startDate - announcement
                if announcementDate > nowTime:
                    return announcementDate - nowTime + 1
                if cycleData.startDate > nowTime:
                    return cycleData.startDate - nowTime + 1
            delta = currentSeason.getLastCycleInfo().endDate - nowTime
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
        return stateChange + 1 if stateChange > 0 else 0

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

    def getCurrentSeason(self, now=None):
        return self.__seasonProvider.getCurrentSeason(now)

    def getNextSeason(self, now=None):
        return self.__seasonProvider.getNextSeason(now)

    def getStageToken(self, cycleID=None):
        cycleID = cycleID or self.__seasonProvider.getCurrentCycleID()
        return '' if cycleID is None else getStageToken(cycleID)

    def getCurrencyToken(self, seasonID=None):
        if seasonID is None:
            curSeason = self.__seasonProvider.getCurrentSeason()
            if curSeason is not None:
                seasonID = curSeason.getSeasonID()
        return '' if seasonID is None else getCurrencyToken(seasonID)

    def isEnabled(self):
        return self.getModeSettings().isEnabled

    def getModeSettings(self):
        return self.__lobbyContext.getServerSettings().armoryYard

    @serverSettingsChangeListener(Configs.ARMORY_YARD_CONFIG.value)
    def __onServerSettingsChanged(self, diff, *args, **kwards):
        self.__seasonProvider.onSettingsUpdated(diff)
        self.onUpdated()
        self.__armoryYardCtrl.update()
