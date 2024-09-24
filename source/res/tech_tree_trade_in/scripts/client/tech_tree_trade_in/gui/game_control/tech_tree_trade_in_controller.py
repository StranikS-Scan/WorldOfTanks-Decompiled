# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/gui/game_control/tech_tree_trade_in_controller.py
import BigWorld
from collections import OrderedDict
import typing
import nations
from adisp import adisp_process
from Event import Event
from debug_utils import LOG_DEBUG
from gui import SystemMessages, GUI_NATIONS, GUI_SETTINGS
from gui.impl.lobby.elite_window.elite_view import EliteWindow
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.settings import FUNCTIONAL_FLAG
from gui.shared.lock_overlays import lockNotificationManager
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from helpers import dependency, time_utils
from skeletons.gui.impl import INotificationWindowController
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
from tech_tree_trade_in.account_settings import isTechTreeTradeInIntroViewed, setTechTreeTradeInIntroViewed
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.tech_tree_trade_in_view_model import MainViews
from tech_tree_trade_in.gui.shared import event_dispatcher
from tech_tree_trade_in.skeletons.gui.game_control import ITechTreeTradeInController, TechTreeBranch, BranchType, GuiSettingsTradeInUrlName
from tech_tree_trade_in.helpers.server_settings import TechTreeTradeInConfig
from tech_tree_trade_in_common.helpers import TradeInToken
from tech_tree_trade_in_common.tech_tree_trade_in_constants import TECH_TREE_TRADE_IN_CONFIG
from tech_tree_trade_in_common.tech_tree_trade_in_config import getTradeInVehiclesCfg
from tech_tree_trade_in_common.tech_tree_trade_in_constants import MAX_TRADE_LEVEL
from tech_tree_trade_in.gui.shared.gui_items.processors import TechTreeTradeInProcessor
if typing.TYPE_CHECKING:
    from typing import Callable, Dict, Generator, List, Optional
    T_PROCESSOR_CALLBACK = Callable[[bool], None]

class TechTreeTradeInController(Notifiable, ITechTreeTradeInController, IGlobalListener):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __notificationManager = dependency.descriptor(INotificationWindowController)
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self):
        super(TechTreeTradeInController, self).__init__()
        self.onSettingsChanged = Event()
        self.onEntryPointUpdated = Event()
        self.onPlayerTradeInStatusChanged = Event()
        self.__serverSettings = None
        self.__tradeInSettings = None
        self.__branchesConfig = self.__readBranchesFromConfig()
        LOG_DEBUG('TechTreeTradeIn: branches config: ', self.__branchesConfig)
        return

    @property
    def isTechTreeTradeInEntryPointEnabled(self):
        return self.isEnabled() and self.isActive() and self.isRandomPrbActive() and self.isTradeInAvailableForPlayer() and bool(self.getBranchesToTrade())

    def init(self):
        super(TechTreeTradeInController, self).init()
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdated})
        LOG_DEBUG('TechTreeTradeInController::init')
        self.addNotificator(SimpleNotifier(self.__getEntryPointTimerDelta, self.__timerUpdate))

    def fini(self):
        self.onSettingsChanged.clear()
        self.onPlayerTradeInStatusChanged.clear()
        self.clearNotification()
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(TechTreeTradeInController, self).fini()

    def getBranchById(self, branchId, branchTypeKey):
        for branch in self.__branchesConfig[branchTypeKey.value]:
            if branch.branchId == branchId:
                return branch

    def getBranchesToTrade(self):
        return [ branch for branch in self.__getBranchesToTrade() if all([ vCd in self.__itemsCache.items.stats.unlocks for vCd in branch.vehCDs ]) ]

    def getBranchesToTradeSortedForNation(self):
        branchesToTrade = self.getBranchesToTrade()
        return self.__groupAndSortBranches(branchesToTrade)

    def getBranchesToReceiveSortedForNation(self):
        branchesToReceive = self.__getBranchesToReceive()
        return self.__groupAndSortBranches([ branch for branch in branchesToReceive if branch.vehCDs[-1] not in self.__itemsCache.items.stats.unlocks and self.__validateBranchToReceive(branch) ])

    def getConfig(self):
        return self.__tradeInSettings

    def getEndTime(self):
        return self.__tradeInSettings.endTime

    def getStartTime(self):
        return self.__tradeInSettings.startTime

    def getTradeInToken(self):
        tradeInToken = next((token for token in self.__itemsCache.items.tokens.getTokens() if token.startswith(TradeInToken.PREFIX)), '')
        return TradeInToken.parseToken(tradeInToken) if tradeInToken else None

    @staticmethod
    def getTradeInURL(urlName):
        if not hasattr(GUI_SETTINGS, 'branchTradeIn'):
            return
        url = GUI_SETTINGS.branchTradeIn.get(urlName.value)
        if url:
            url = GUI_SETTINGS.checkAndReplaceWebBridgeMacros(url)
        return url

    def isActive(self):
        currentTime = time_utils.getCurrentLocalServerTimestamp()
        return True if self.getStartTime() <= currentTime < self.getEndTime() else False

    def isRandomPrbActive(self):
        return False if self.prbEntity is None else bool(self.prbEntity.getModeFlags() & FUNCTIONAL_FLAG.RANDOM)

    def isEnabled(self):
        return self.__tradeInSettings.isEnabled

    def isTradeInAvailableForPlayer(self):
        return not self.__hasTradeInToken(self.__itemsCache.items.tokens.getTokens())

    def onAccountBecomePlayer(self):
        self.__onServerSettingsChanged(self.__lobbyContext.getServerSettings())
        super(TechTreeTradeInController, self).onAccountBecomePlayer()

    @adisp_process
    def requestTradeIn(self, branchToTradeID, branchToReceiveID, multiPrice, callback=None):
        lockNotificationManager(True, postponeActive=True, notificationManager=self.__notificationManager)
        self.__notificationManager.setFilterPredicate(self.__tradeInNotificationWindowsPredicate)
        branchToTrade = self.getBranchById(branchToTradeID, BranchType.BRANCHES_TO_TRADE)
        branchToReceive = self.getBranchById(branchToReceiveID, BranchType.BRANCHES_TO_RECEIVE)
        flatMultiPrice = self.__flattenMultiprice(multiPrice)
        result = yield TechTreeTradeInProcessor(branchToTrade.vehCDs, branchToReceive.vehCDs, flatMultiPrice).request()
        SystemMessages.pushMessagesFromResult(result)
        if callback is not None:
            callback(result)
        self.__notificationManager.setFilterPredicate(None)
        lockNotificationManager(False, releasePostponed=True, notificationManager=self.__notificationManager)
        return

    def requestTradeInDryRun(self, branchToTradeID, branchToReceiveID, callback):
        branchToTrade = self.getBranchById(branchToTradeID, BranchType.BRANCHES_TO_TRADE)
        branchToReceive = self.getBranchById(branchToReceiveID, BranchType.BRANCHES_TO_RECEIVE)
        LOG_DEBUG('TechTreeTradeIn: requesting trade-in dry run', branchToTrade.vehCDs, branchToReceive.vehCDs)
        BigWorld.player().TechTreeTradeInAccountComponent.requestTradeInDryRun(branchToTrade.vehCDs, branchToReceive.vehCDs, callback)

    def showTechTreeTradeInView(self):
        if isTechTreeTradeInIntroViewed():
            event_dispatcher.showTechTreeTradeInView(MainViews.BRANCH_SELECTION)
        else:
            setTechTreeTradeInIntroViewed()
            self.__showOnboardingIntro()

    def __getBranchesToTrade(self):
        return self.__branchesConfig['branchesToTrade']

    def __getBranchesToReceive(self):
        return self.__branchesConfig['branchesToReceive']

    def __getEntryPointTimerDelta(self):
        currentTime = time_utils.getCurrentLocalServerTimestamp()
        startTime = self.getStartTime()
        return max(0, startTime - currentTime) if currentTime < startTime else max(0, self.getEndTime() - currentTime)

    @staticmethod
    def __flattenMultiprice(multiPrice):
        return (multiPrice['gold']['value'],
         multiPrice['intelligence']['value'],
         multiPrice['fragments']['value'],
         nations.INDICES[multiPrice['fragments']['type']],
         multiPrice['freeXP']['value'],
         multiPrice['crystal']['value'])

    @staticmethod
    def __groupAndSortBranches(branches):
        g_techTreeDP.load()
        result = OrderedDict()
        for nationName, nationIdx in sorted(nations.INDICES.items(), key=lambda (key, value): GUI_NATIONS.index(key)):
            orderedBranches = []
            nationTopVehiclesOrdered = [ item[0].nodeCD for item in g_techTreeDP.getNationTreeIterator(nationIdx) if item[1]['column'] == MAX_TRADE_LEVEL ]
            for branch in branches:
                if branch.vehCDs[-1] in nationTopVehiclesOrdered:
                    orderedBranches.append(branch)

            result[nationName] = sorted(orderedBranches, key=lambda branch: nationTopVehiclesOrdered.index(branch.vehCDs[-1]))

        return result

    @staticmethod
    def __hasTradeInToken(mapping):
        return any((key.startswith('tech_tree_trade_in') for key in mapping))

    def __onServerSettingsChanged(self, serverSettings):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__updateTradeInSettings
        self.__serverSettings = serverSettings
        newRawSettings = serverSettings.getSettings().get(TECH_TREE_TRADE_IN_CONFIG, {})
        self.__tradeInSettings = TechTreeTradeInConfig(**newRawSettings)
        self.__serverSettings.onServerSettingsChange += self.__updateTradeInSettings
        return

    def __onTokensUpdated(self, diff):
        if self.__hasTradeInToken(diff):
            LOG_DEBUG("TechTreeTradeIn: Player's trade-in status changed, ", diff)
            self.onPlayerTradeInStatusChanged()

    @staticmethod
    def __readBranchesFromConfig():
        return {key:[ TechTreeBranch(branchId, branch) for branchId, branch in enumerate(value) ] for key, value in getTradeInVehiclesCfg()['branches'].items()}

    def __resetTimer(self):
        self.startNotification()
        self.__timerUpdate()

    def __showOnboardingIntro(self):
        event_dispatcher.showTechTreeTradeInView(MainViews.INTRO)
        self.showOnboardingIntroVideo()

    def __timerUpdate(self):
        self.onEntryPointUpdated()

    def __updateTradeInSettings(self, diff):
        if TECH_TREE_TRADE_IN_CONFIG not in diff:
            return
        self.__tradeInSettings = self.__tradeInSettings.replace(diff[TECH_TREE_TRADE_IN_CONFIG].copy())
        self.onSettingsChanged()
        self.__resetTimer()

    def __validateBranchToReceive(self, branch):
        prevUnlocked = branch.vehCDs[0] in self.__itemsCache.items.stats.unlocks
        for vCD in branch.vehCDs:
            isUnlocked = vCD in self.__itemsCache.items.stats.unlocks
            if isUnlocked and not prevUnlocked:
                return False
            prevUnlocked = isUnlocked

        return True

    @staticmethod
    def __tradeInNotificationWindowsPredicate(command):
        window = command.getWindow()
        if window is not None and isinstance(window, EliteWindow):
            window.destroy()
            return False
        else:
            return True

    def showOnboardingIntroVideo(self):
        event_dispatcher.showBranchTechTradeInOverlay(self.getTradeInURL(GuiSettingsTradeInUrlName.VIDEO))
