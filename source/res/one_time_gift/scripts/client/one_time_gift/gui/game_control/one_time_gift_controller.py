# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/gui/game_control/one_time_gift_controller.py
import logging
from collections import OrderedDict
import typing
import nations
from Event import Event, EventManager
from account_helpers import AccountSettings
from account_helpers.AccountSettings import OTG_BATTLES_PLAYED_BEFORE_START
from account_helpers.settings_core.ServerSettingsManager import UI_STORAGE_KEYS
from constants import ARENA_BONUS_TYPE
from frameworks.state_machine import StringEvent
from gui import GUI_NATIONS
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.game_loading.resources.consts import Milestones
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.lock_overlays import lockNotificationManager
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier
from helpers import dependency, time_utils
from helpers.events_handler import EventsHandler
from helpers.server_settings import serverSettingsChangeListener
from PlayerEvents import g_playerEvents
from one_time_gift.gui.shared.lock_overlays import lockAchievementsEarning, lockSteamShade
from shared_utils import findFirst, nextTick
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IHangarLoadingController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from messenger.proto.events import g_messengerEvents
from one_time_gift.gui.gui_constants import OTG_LOCK_SOURCE_NAME
from one_time_gift.gui.state_machine import OTGEvent, OneTimeGiftStateMachine
from one_time_gift.helpers.server_settings import OneTimeGiftConfig
from one_time_gift.skeletons.gui.game_control import IOneTimeGiftController
from one_time_gift_common import one_time_gift_token
from one_time_gift_common.one_time_gift_branches_config import getOneTimeGiftBranchesCfg
from one_time_gift_common.one_time_gift_constants import MAX_OTG_VEH_LEVEL, OTG_ERROR_CODES, OTG_GAME_PARAMS_KEY, BranchListType, TechTreeBranch
if typing.TYPE_CHECKING:
    from typing import Callable, Dict, List, Optional
    T_PROCESSOR_CALLBACK = Callable[[bool], None]
_logger = logging.getLogger(__name__)

class OneTimeGiftController(Notifiable, IOneTimeGiftController, IGlobalListener, EventsHandler):
    __hangarLoadingController = dependency.descriptor(IHangarLoadingController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(OneTimeGiftController, self).__init__()
        self.__eventsManager = EventManager()
        self.onEntryPointUpdated = Event(self.__eventsManager)
        self.onPlayerOTGStatusChanged = Event(self.__eventsManager)
        self.onSettingsChanged = Event(self.__eventsManager)
        self.__serverSettings = None
        self.__oneTimeGiftSettings = None
        self.__stateMachine = None
        self.__branchesConfig = self.__readBranchesFromConfig()
        _logger.debug('OneTimeGift: branches config: %s', self.__branchesConfig)
        self.__branchSets = None
        self.__isEntryPointShown = False
        self.__isCalledAfterStoryMode = False
        return

    @property
    def isEntryPointEnabled(self):
        return self.isActive() and not self.areAllRewardsReceived()

    @property
    def isEntryPointShown(self):
        return self.__isEntryPointShown

    def init(self):
        super(OneTimeGiftController, self).init()
        self.__stateMachine = OneTimeGiftStateMachine()
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdated})
        g_techTreeDP.load()
        self.addNotificator(SimpleNotifier(self.__getEntryPointTimerDelta, self.__timerUpdate))
        _logger.debug('OneTimeGiftController::init')

    def fini(self):
        self._unsubscribe()
        self.__eventsManager.clear()
        if self.__stateMachine is not None:
            self.__stateMachine.stop()
            self.__stateMachine = None
        self.__branchesConfig = None
        self.__branchSets = None
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.clearNotification()
        self.__serverSettings = None
        self.__oneTimeGiftSettings = None
        super(OneTimeGiftController, self).fini()
        return

    def onAccountBecomePlayer(self):
        self.__onServerSettingsChanged(self.__lobbyContext.getServerSettings())
        super(OneTimeGiftController, self).onAccountBecomePlayer()

    def onAccountBecomeNonPlayer(self):
        if self.__stateMachine is not None and self.__stateMachine.isRunning():
            self.__stateMachine.stop()
        self._unsubscribe()
        return

    def onAvatarBecomePlayer(self):
        arenaBonusType = self.__sessionProvider.arenaVisitor.getArenaBonusType()
        self.__isCalledAfterStoryMode = arenaBonusType in (ARENA_BONUS_TYPE.STORY_MODE_ONBOARDING, ARENA_BONUS_TYPE.STORY_MODE_REGULAR)

    def onLobbyStarted(self, ctx):
        if self.__needToShowIntro():
            lockSteamShade(True)
            lockAchievementsEarning(True)
            lockNotificationManager(True, OTG_LOCK_SOURCE_NAME)

    def onLobbyInited(self, event):
        self._subscribe()
        self.__saveBattlesBeforeEventStart()
        self.__startStateMachine()

    def onDisconnected(self):
        self._unsubscribe()
        self.__stateMachine.stop()
        self.__isEntryPointShown = False
        lockNotificationManager(False, OTG_LOCK_SOURCE_NAME)
        lockAchievementsEarning(False)
        lockSteamShade(False)

    def markEntryPointShown(self):
        self.__isEntryPointShown = True

    def areAllRewardsReceived(self):
        return self.isAdditionalRewardReceived() and (self.isFullListBranchReceived() or self.isCollectorsCompensationReceived())

    def getAvailabilityError(self):
        if not self.isEnabled():
            return OTG_ERROR_CODES.NOT_AVAILABLE
        else:
            return OTG_ERROR_CODES.NOT_ACTIVE if not self.isActive() else None

    def getBranchById(self, branchId, fromList):
        return findFirst(lambda branch: branch.branchId == branchId, self.__getBranches(fromList))

    def getBranchesSortedForNation(self, fromList):
        branches = self.__getBranches(fromList)
        return self.__groupAndSortBranches([ branch for branch in branches if self.__validateBranchToReceive(branch) ])

    def getConfig(self):
        return self.__oneTimeGiftSettings

    def getEndTime(self):
        return self.__oneTimeGiftSettings.endTime

    def getStartTime(self):
        return self.__oneTimeGiftSettings.startTime

    def getRemindTime(self):
        return self.__oneTimeGiftSettings.remindTime

    def getRemindBattlesAmount(self):
        return self.__oneTimeGiftSettings.remindBattlesAmount

    def isActive(self):
        return self.isEnabled() and self.getStartTime() <= time_utils.getServerUTCTime() < self.getEndTime()

    def isAdditionalRewardReceived(self):
        return self.__itemsCache.items.tokens.isTokenAvailable(one_time_gift_token.ADDITIONAL_REWARD_BLOCKER)

    def isCollectorsCompensationReceived(self):
        return self.__itemsCache.items.tokens.isTokenAvailable(one_time_gift_token.COLLECTOR_REWARD_BLOCKER)

    def isBranchListPurchased(self, branchListType):
        inventoryVehsSet = set(self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY))
        return self.__getBranchSets()[branchListType.value] <= inventoryVehsSet

    def isEnabled(self):
        return self.__oneTimeGiftSettings.isEnabled

    def isNewbieBranchReceived(self):
        return self.__itemsCache.items.tokens.isTokenAvailable(one_time_gift_token.NEWBIE_BRANCH_BLOCKER)

    def isFullListBranchReceived(self):
        return self.__itemsCache.items.tokens.isTokenAvailable(one_time_gift_token.FULL_BRANCH_BLOCKER)

    def isPlayerNewbie(self):
        return self.__getAccountCreationTime() >= self.__oneTimeGiftSettings.newbieDistinctionTime

    def onEntryPointClicked(self):
        _logger.info('OneTimeGift: onEntryPointClicked')
        if self.__stateMachine is not None:
            self.__stateMachine.post(StringEvent(OTGEvent.ENTRY_POINT_CLICK))
        return

    def onShowInfoClicked(self, ctx=None):
        _logger.info('OneTimeGift: onShowIntroClicked')
        if self.__stateMachine is not None:
            self.__stateMachine.post(StringEvent(OTGEvent.INFO_CLICK, ctx=ctx))
        return

    def onViewError(self):
        _logger.info('OneTimeGift: onViewError')
        if self.__stateMachine is not None:
            nextTick(self.__stateMachine.post)(StringEvent(OTGEvent.ERROR, error=OTG_ERROR_CODES.NOT_AVAILABLE))
        return

    def _getEvents(self):
        return super(OneTimeGiftController, self)._getEvents() + ((self.__hangarLoadingController.onHangarLoadedAfterLogin, self.__onHangarLoadedAfterLogin), (g_playerEvents.onLoadingMilestoneReached, self.__onLoadingMilestoneReached))

    def __getAccountCreationTime(self):
        dossierDescr = self.__itemsCache.items.getAccountDossier().getDossierDescr()
        return dossierDescr['total']['creationTime']

    def __getBranches(self, fromList):
        return self.__branchesConfig[fromList.value]

    def __getBranchSets(self):
        if not self.__branchSets:
            self.__branchSets = {}
            for branchListType in (BranchListType.NEWBIE, BranchListType.ALL):
                self.__branchSets[branchListType.value] = set()
                for branch in self.__getBranches(branchListType):
                    self.__branchSets[branchListType.value].update(branch.vehCDs)

        return self.__branchSets

    @staticmethod
    def __groupAndSortBranches(branches):
        result = OrderedDict()
        for nationName, nationIdx in sorted(nations.INDICES.items(), key=lambda (key, value): GUI_NATIONS.index(key)):
            orderedBranches = []
            nationTopVehiclesOrdered = [ item[0].nodeCD for item in g_techTreeDP.getNationTreeIterator(nationIdx) if item[1]['column'] == MAX_OTG_VEH_LEVEL ]
            for branch in branches:
                if branch.vehCDs[-1] in nationTopVehiclesOrdered:
                    orderedBranches.append(branch)

            result[nationName] = sorted(orderedBranches, key=lambda nationBranch: nationTopVehiclesOrdered.index(nationBranch.vehCDs[-1]))

        return result

    @staticmethod
    def __hasOTGToken(mapping):
        return any((key.startswith(one_time_gift_token.PREFIX) for key in mapping))

    def __onHangarLoadedAfterLogin(self):
        if self.__needToShowIntro() and self.__stateMachine is not None:
            self.__stateMachine.post(StringEvent(OTGEvent.INTRO_START))
        return

    def __onTokensUpdated(self, diff):
        if self.__hasOTGToken(diff):
            _logger.debug('OneTimeGift: Player rewards status changed, %s', diff)
            self.onPlayerOTGStatusChanged()

    def __onServerSettingsChanged(self, serverSettings):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__updateOTGSettings
        self.__serverSettings = serverSettings
        newRawSettings = serverSettings.getSettings().get(OTG_GAME_PARAMS_KEY, {})
        self.__oneTimeGiftSettings = OneTimeGiftConfig(**newRawSettings)
        self.__serverSettings.onServerSettingsChange += self.__updateOTGSettings
        return

    @staticmethod
    def __readBranchesFromConfig():
        result = {}
        for branchListType, branches in getOneTimeGiftBranchesCfg().items():
            result[branchListType] = [ TechTreeBranch(branchId, branch) for branchId, branch in enumerate(branches) ]

        return result

    def __startStateMachine(self):
        if not self.isActive():
            return
        if not self.__stateMachine.isRunning():
            _logger.debug('Start OTG state machine due to active event')
            self.__stateMachine.configure()
            self.__stateMachine.start()

    @serverSettingsChangeListener(OTG_GAME_PARAMS_KEY)
    def __updateOTGSettings(self, diff):
        self.__oneTimeGiftSettings = self.__oneTimeGiftSettings.replace(diff[OTG_GAME_PARAMS_KEY].copy())
        self.__saveBattlesBeforeEventStart()
        self.__resetTimer()
        self.__startStateMachine()
        self.onSettingsChanged()

    def __validateBranchToReceive(self, branch):
        branchVehicles = [ self.__itemsCache.items.getItemByCD(vehCD) for vehCD in branch.vehCDs ]
        return not all((vehicle.isPurchased for vehicle in branchVehicles))

    def __saveBattlesBeforeEventStart(self):
        if AccountSettings.getUIFlag(OTG_BATTLES_PLAYED_BEFORE_START) is None and self.isActive():
            randomStats = self.__itemsCache.items.getAccountDossier().getRandomStats()
            AccountSettings.setUIFlag(OTG_BATTLES_PLAYED_BEFORE_START, randomStats.getBattlesCount())
        return

    def __getEntryPointTimerDelta(self):
        currentTime = time_utils.getServerUTCTime()
        startTime = self.getStartTime()
        remindTime = self.getRemindTime()
        if currentTime < startTime:
            return max(0, startTime - currentTime)
        return max(0, remindTime - currentTime) if currentTime < remindTime else max(0, self.getEndTime() - currentTime)

    def __resetTimer(self):
        self.startNotification()
        self.__timerUpdate()

    def __timerUpdate(self):
        self.__startStateMachine()
        self.onEntryPointUpdated()

    def __onLoadingMilestoneReached(self, milestoneName):
        if milestoneName != Milestones.HANGAR_READY:
            return
        else:
            g_playerEvents.onLoadingMilestoneReached -= self.__onLoadingMilestoneReached
            if self.__needToShowIntro():
                g_messengerEvents.onLockPopUpMessages(OTG_LOCK_SOURCE_NAME, lockHigh=True, useQueue=False)
                if self.__isCalledAfterStoryMode and self.__stateMachine is not None:
                    self.__stateMachine.post(StringEvent(OTGEvent.INTRO_START))
                self.__settingsCore.serverSettings.saveInUIStorage2({UI_STORAGE_KEYS.ONE_TIME_GIFT_INTRO_SHOWN: True})
            return

    def __needToShowIntro(self):
        return self.isEntryPointEnabled and not self.__settingsCore.serverSettings.getUIStorage2().get(UI_STORAGE_KEYS.ONE_TIME_GIFT_INTRO_SHOWN)
