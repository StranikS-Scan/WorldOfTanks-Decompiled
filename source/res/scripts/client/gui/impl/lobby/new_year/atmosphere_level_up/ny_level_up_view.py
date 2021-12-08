# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/atmosphere_level_up/ny_level_up_view.py
from functools import partial
import typing
import AnimationSequence
import BigWorld
from CurrentVehicle import g_currentVehicle
from frameworks.wulf import ViewSettings, WindowLayer, ViewStatus, WindowStatus
from gui.Scaleform.Waiting import Waiting
from gui.impl.backport import BackportTooltipWindow
from gui.impl.backport import TooltipData
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.lobby.new_year.views.atmosphere_level_up_model import AtmosphereLevelUpModel
from gui.impl.lobby.loot_box.loot_box_sounds import LootBoxVideoStartStopHandler, LootBoxVideos, setOverlayHangarGeneral, PausedSoundManager
from gui.impl.lobby.missions.daily_quests_widget_view import predicateTooltipWindow
from gui.impl.lobby.new_year.tooltips.ny_shards_tooltip import NyShardsTooltip
from gui.impl.lobby.new_year.tooltips.ny_vehicle_slot_tooltip import NyVehicleSlotTooltip
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
from gui.impl.new_year.new_year_bonus_packer import packBonusModelAndTooltipData, getNewYearBonusPacker
from gui.impl.new_year.new_year_bonuses import extendBonusesByLevel
from gui.impl.new_year.new_year_helper import nyBonusGFSortOrder, ADDITIONAL_BONUS_NAME_GETTERS
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.server_events.bonuses import splitBonuses
from gui.shared.event_dispatcher import showNewYearVehiclesView, showVideoView
from helpers import dependency, uniprof, isPlayerAccount
from items.components.crew_books_constants import CREW_BOOK_RARITY
from items.components.ny_constants import CurrentNYConstants
from messenger.proto.events import g_messengerEvents
from shared_utils import findFirst, first
from skeletons.gui.impl import IGuiLoader, INotificationWindowController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.new_year import INewYearController
from uilogging.deprecated.decorators import loggerEntry
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array
    from gui.shared.missions.packers.bonus import BonusUIPacker
    from gui.server_events.bonuses import SimpleBonus
_FIRST_LVL = 1
_MIN_HUGE_REWARDS = 1
_MAX_HUGE_REWARDS = 3
_HUGE_BONUESES_ORDER = ('tmanToken',
 'newYearSlot',
 CREW_BOOK_RARITY.PERSONAL,
 'vehicles',
 CurrentNYConstants.FILLERS,
 'entitlements')

def _splitHugeBonuses(bonuses):
    hugeBonuses = []
    otherBonuses = []
    for bonus in bonuses:
        bonusName = bonus.getName()
        getAdditionalName = ADDITIONAL_BONUS_NAME_GETTERS.get(bonusName)
        if getAdditionalName is not None:
            bonusName = getAdditionalName(bonus)
        if bonusName in _HUGE_BONUESES_ORDER:
            hugeBonuses.append(bonus)
        otherBonuses.append(bonus)

    if len(hugeBonuses) > 1:
        hugeBonuses.sort(key=_hugeBonusesSortOrder)
        delimiter = _MAX_HUGE_REWARDS
        if len(hugeBonuses) < _MAX_HUGE_REWARDS:
            delimiter = _MIN_HUGE_REWARDS
        otherBonuses.extend(hugeBonuses[delimiter:])
        hugeBonuses = hugeBonuses[:delimiter]
    return (hugeBonuses, otherBonuses)


def _hugeBonusesSortOrder(bonus):
    bonusName = bonus.getName()
    getAdditionalName = ADDITIONAL_BONUS_NAME_GETTERS.get(bonusName)
    if getAdditionalName is not None:
        bonusName = getAdditionalName(bonus)
    return _HUGE_BONUESES_ORDER.index(bonusName) if bonusName in _HUGE_BONUESES_ORDER else len(_HUGE_BONUESES_ORDER)


class NyAtmosphereLevelUpView(ViewImpl):
    __nyController = dependency.descriptor(INewYearController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __gui = dependency.descriptor(IGuiLoader)
    __notificationMgr = dependency.descriptor(INotificationWindowController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.AtmosphereLevelUp())
        settings.model = AtmosphereLevelUpModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NyAtmosphereLevelUpView, self).__init__(settings)
        self.__tooltips = {}
        self.__isFirstLevelUp = False
        self.__rewards = {}
        self.__currentLevel = 0
        self.__completedLevels = []
        self.__spaceLoaded = False
        self.__cacheLoaded = False
        self.__callbackId = None
        self.__videoStartStopHandler = LootBoxVideoStartStopHandler(checkPauseOnStart=False)
        self.__vehicleBonus = None
        return

    @property
    def viewModel(self):
        return super(NyAtmosphereLevelUpView, self).getViewModel()

    def createToolTipContent(self, event, ctID):
        if ctID == R.views.lobby.new_year.tooltips.NyVehicleSlotTooltip():
            tooltipData = self.__tooltips.get(event.getArgument('tooltipId'))
            if tooltipData is None:
                return
            return NyVehicleSlotTooltip(*tooltipData.specialArgs)
        elif ctID == R.views.lobby.new_year.tooltips.NyShardsTooltip():
            return NyShardsTooltip()
        elif ctID == R.views.lobby.tooltips.AdditionalRewardsTooltip() and self.viewStatus == ViewStatus.LOADED:
            showCount = int(event.getArgument('showedCount'))
            bonuses = splitBonuses(self.__rewards[self.__currentLevel])
            _, secondaryBonuses = _splitHugeBonuses(bonuses)
            return AdditionalRewardsTooltip(sorted(secondaryBonuses, key=nyBonusGFSortOrder)[showCount:], getNewYearBonusPacker())
        else:
            return super(NyAtmosphereLevelUpView, self).createToolTipContent(event, ctID)

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            window = None
            if tooltipId is not None:
                window = BackportTooltipWindow(self.__tooltips[tooltipId], self.getParentWindow())
                window.load()
            return window
        else:
            return super(NyAtmosphereLevelUpView, self).createToolTip(event)

    def appendRewards(self, *_, **kwargs):
        for level, rewards in kwargs.get('levelRewards', {}).iteritems():
            self.__rewards[level] = rewards
            self.__completedLevels.append(level)

        self.__completedLevels.sort()

    def _onLoading(self, *_, **kwargs):
        super(NyAtmosphereLevelUpView, self)._onLoading()
        self.__isFirstLevelUp = _FIRST_LVL in self.__rewards
        if self.__isFirstLevelUp:
            self.__saveVehicleData()
        self.__cacheLoaded = self.__itemsCache.isSynced()
        self.__spaceLoaded = self.__hangarSpace.spaceInited
        if self.__isFirstLevelUp and not (self.__spaceLoaded and self.__cacheLoaded):
            if not self.__cacheLoaded:
                self.__itemsCache.onSyncCompleted += self.__onSyncCompleted
            if not self.__spaceLoaded:
                self.__hangarSpace.onSpaceCreate += self.__onSpaceCreated
        else:
            self.__spaceLoaded = self.__cacheLoaded = True
            self.viewModel.setIsViewReady(True)
        self.viewModel.onClose += self.__onCloseAction
        self.viewModel.onGoToTanks += self.__onGoToTanks
        self.__nyController.onStateChanged += self.__onEventStateChanged
        self.__processNextReward()

    def __hasRewards(self):
        return bool(set(self.__completedLevels).intersection(self.__rewards.keys()))

    def __processNextReward(self):
        if self.__completedLevels:
            self.__currentLevel = self.__completedLevels.pop(0)
            self.__setRewards()

    @loggerEntry
    @uniprof.regionDecorator(label='ny.level_up_reward.open', scope='enter')
    def _initialize(self, *args, **kwargs):
        super(NyAtmosphereLevelUpView, self)._initialize(*args, **kwargs)
        setOverlayHangarGeneral(True)
        g_messengerEvents.onLockPopUpMessages(key=self.__class__.__name__, lockHigh=True)

    @uniprof.regionDecorator(label='ny.level_up_reward.open', scope='exit')
    def _finalize(self):
        self.setHold(False)
        g_messengerEvents.onUnlockPopUpMessages(key=self.__class__.__name__)
        setOverlayHangarGeneral(False)
        super(NyAtmosphereLevelUpView, self)._finalize()
        self.__removeSyncHandler()
        self.__removeSpaceHandler()
        self.viewModel.onClose -= self.__onCloseAction
        self.viewModel.onGoToTanks -= self.__onGoToTanks
        self.__nyController.onStateChanged -= self.__onEventStateChanged
        self.__videoStartStopHandler.onVideoDone()
        self.__rewards = None
        if self.__callbackId is not None:
            BigWorld.cancelCallback(self.__callbackId)
        if self.__isFirstLevelUp:
            self.__processVehicleChange()
        return

    def __onCloseAction(self):
        if self.__completedLevels:
            self.__processNextReward()
            return
        if self.__isFirstLevelUp:
            windows = self.__gui.windowsManager.findWindows(predicateTooltipWindow)
            for window in windows:
                window.destroy()

            self.setHold(True)
            showVideoView(R.videos.lootboxes.ng_startup(), onVideoStarted=partial(self.__videoStartStopHandler.onVideoStart, videoId=LootBoxVideos.START), onVideoStopped=self.__onVideoDone, isAutoClose=True, soundControl=PausedSoundManager())
        else:
            self.destroyWindow()

    def __onEventStateChanged(self):
        if not self.__nyController.isEnabled():
            self.destroyWindow()

    def __onVideoDone(self):
        self.setHold(False)
        self.__videoStartStopHandler.onVideoDone()
        self.destroyWindow()

    def __onGoToTanks(self):
        if self.__hasRewards():
            self.__hideWindow()
            showNewYearVehiclesView(backCallback=self.__restoreWindow)
        else:
            self.__notificationMgr.postponeActive()
            self.destroyWindow()
            showNewYearVehiclesView()

    def __hideWindow(self):
        self.getParentWindow().hide()

    def __restoreWindow(self):
        self.getParentWindow().show()
        self.__processNextReward()

    def __setRewards(self):
        bonuses = self.__rewards[self.__currentLevel]
        extendBonusesByLevel(bonuses, self.__currentLevel)
        bonuses = splitBonuses(bonuses)
        hugeBonuses, otherBonuses = _splitHugeBonuses(bonuses)
        with self.getViewModel().transaction() as model:
            self.__tooltips.clear()
            self.__fillRewardsList(rewardsList=model.hugeRewards.getItems(), bonuses=hugeBonuses, sortMethod=_hugeBonusesSortOrder, packer=getNewYearBonusPacker())
            self.__fillRewardsList(rewardsList=model.rewards.getItems(), bonuses=otherBonuses, sortMethod=nyBonusGFSortOrder, packer=getNewYearBonusPacker())
            model.setLevel(self.__currentLevel)

    def __fillRewardsList(self, rewardsList, bonuses, sortMethod, packer):
        rewardsList.clear()
        bonuses.sort(key=sortMethod)
        packBonusModelAndTooltipData(bonuses, rewardsList, packer, self.__tooltips)

    def __saveVehicleData(self):
        vehicleBonus = findFirst(lambda bonus: bonus.getName() == 'vehicles', self.__rewards[_FIRST_LVL])
        if vehicleBonus is not None:
            self.__vehicleBonus = vehicleBonus
        return

    def __processVehicleChange(self):
        if not isPlayerAccount():
            return
        else:
            if self.__vehicleBonus is not None:
                vehicle, _ = first(self.__vehicleBonus.getVehicles(), (None, None))
                if vehicle is not None:
                    g_currentVehicle.selectVehicle(vehicle.invID)
            return

    def __removeSyncHandler(self):
        self.__itemsCache.onSyncCompleted -= self.__onSyncCompleted

    def __removeSpaceHandler(self):
        self.__hangarSpace.onSpaceCreate -= self.__onSpaceCreated

    def __onSpaceCreated(self):
        self.__removeSpaceHandler()
        self.__spaceLoaded = True
        self.__checkViewReady()

    def __onSyncCompleted(self, _, diff):
        self.__removeSyncHandler()
        self.__cacheLoaded = True
        self.__checkViewReady()

    def __checkViewReady(self):
        if self.__spaceLoaded and self.__cacheLoaded:
            self.setIsViewReadyAfterWheelFinish()

    def setIsViewReadyAfterWheelFinish(self):
        if Waiting.isVisible():
            self.__callbackId = BigWorld.callback(0.1, self.setIsViewReadyAfterWheelFinish)
        else:
            self.__callbackId = None
            self.viewModel.setIsViewReady(True)
        return


class NyLevelUpWindow(LobbyNotificationWindow):
    __slots__ = ('__worldOn',)

    def __init__(self, *args, **kwargs):
        super(NyLevelUpWindow, self).__init__(content=NyAtmosphereLevelUpView(*args, **kwargs), layer=WindowLayer.OVERLAY)
        self.__worldOn = False
        self.onStatusChanged += self.__onStatusChanged

    def isParamsEqual(self, *args, **kwargs):
        return True

    def _finalize(self):
        self.onStatusChanged -= self.__onStatusChanged
        if self.__worldOn and dependency.instance(IHangarSpace).spaceInited:
            BigWorld.worldDrawEnabled(True)
            AnimationSequence.setEnableAnimationSequenceUpdate(True)
        super(NyLevelUpWindow, self)._finalize()

    def __onStatusChanged(self, newState):
        if newState == WindowStatus.LOADED:
            self.__worldOn = dependency.instance(IHangarSpace).spaceInited and BigWorld.worldDrawEnabled()
            if self.__worldOn:
                BigWorld.worldDrawEnabled(False)
                AnimationSequence.setEnableAnimationSequenceUpdate(False)
