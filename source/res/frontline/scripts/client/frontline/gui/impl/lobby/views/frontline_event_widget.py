# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/views/frontline_event_widget.py
from CurrentVehicle import g_currentVehicle
from constants import LoadoutParams
from frontline.frontline_account_settings import isRentBannerClicked, setRentBannerClicked
from frontline.gui.impl.gen.view_models.views.lobby.views.event_widget_model import EventWidgetModel
from frontline.gui.impl.lobby.states import ProgressionScreenState, FrontlineBattleAbilitiesLoadoutState
from frontline.gui.impl.lobby.tooltips.banner_tooltip import BannerTooltipView
from frontline.gui.impl.lobby.user_missions.hangar_widget.overlap_ctrl import FLOverlapCtrlMixin
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getRentVehicleUrl
from gui.impl.lobby.user_missions.hangar_widget.tooltip_positioner import TooltipPositionerMixin
from gui.impl.pub.view_component import ViewComponent
from gui.shared.event_dispatcher import showShop, showEpicRewardsSelectionWindow
from gui.shared.formatters.ranges import toRangeString, toRomanRangeString
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.utils import isRomanNumberForbidden
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from frontline.gui.frontline_helpers import isFinishedCycleState, isAnnouncedCycleState, getFrontlineState
from PlayerEvents import g_playerEvents
from wg_async import wg_async, wg_await, delay
from constants import SERVER_TICK_LENGTH

class _LastEntryState(object):

    def __init__(self):
        self.rewards = dict()
        self.rewardsHash = 0

    def update(self, rewards=None, rewardsHash=0):
        self.rewards = dict() if rewards is None else rewards
        self.rewardsHash = rewardsHash
        return


class BattleAbilitiesLoadoutParams(object):
    loadoutGroupIndex = 0
    loadoutSectionIndex = 2
    loadoutSlotIndex = 0
    parameters = {LoadoutParams.groupIndex: loadoutGroupIndex,
     LoadoutParams.sectionIndex: loadoutSectionIndex,
     LoadoutParams.slotIndex: loadoutSlotIndex}


_g_entryLastState = _LastEntryState()

class FrontlineEventWidget(TooltipPositionerMixin, FLOverlapCtrlMixin, ViewComponent[EventWidgetModel]):
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __abilitiesPanelCriteria = (REQ_CRITERIA.VEHICLE.READY, REQ_CRITERIA.VEHICLE.WOT_PLUS_VEHICLE, REQ_CRITERIA.VEHICLE.EXPIRED_RENT)

    def __init__(self):
        super(FrontlineEventWidget, self).__init__(model=EventWidgetModel)
        self.__gameModeStatus, _, _ = getFrontlineState()

    @property
    def viewModel(self):
        return super(FrontlineEventWidget, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return BannerTooltipView(isForFrontlineWidget=True)

    def _onLoading(self, *args, **kwargs):
        self.initOverlapCtrl()
        super(FrontlineEventWidget, self)._onLoading(*args, **kwargs)
        self.queueUpdate()

    def _getEvents(self):
        return ((self.gui.windowsManager.onWindowStatusChanged, self._onWindowStatusChanged),
         (self.__epicController.onUpdated, self.__onEpicUpdated),
         (self.__epicController.onGameModeStatusTick, self.__onGameModeStatusChange),
         (self.viewModel.goToProgressionScreen, self.__onProgressionClick),
         (self.viewModel.goToCombatReservesScreen, self.__onCombatReservesClick),
         (self.viewModel.goToSpecialVehicleRentScreen, self.__onVehicleRentClick),
         (self.__itemsCache.onSyncCompleted, self.__onCacheResync),
         (self.__hangarSpace.onSpaceCreate, self.__onSpaceCreate),
         (g_currentVehicle.onChanged, self.__onChangedVehicle),
         (g_playerEvents.onClientUpdated, self.__onTokensUpdate))

    def _prepareRewardsData(self):
        hasNewRewards = False
        rewards = dict()
        tokens = self.__epicController.getNotChosenRewardTokens()
        for token in tokens:
            count = self.__itemsCache.items.tokens.getTokenCount(token)
            rewards[token] = count
            hasNewRewards = hasNewRewards or _g_entryLastState.rewards.get(token) != count

        rewardsHash = _g_entryLastState.rewardsHash + int(hasNewRewards) if tokens else 0
        return (rewards, rewardsHash)

    def _rawUpdate(self, *_, **__):
        super(FrontlineEventWidget, self)._rawUpdate()
        self.__setRentHightlighted()
        self.__updateBattleAbilitiesPanel()
        with self.viewModel.transaction() as vm:
            self.__fillWidgetModel(vm)
            if self.__hangarSpace.spaceInited:
                rewards, rewardsHash = self._prepareRewardsData()
                vm.setLastSeenRewardsHash(_g_entryLastState.rewardsHash)
                vm.setRewardsHash(rewardsHash)
                _g_entryLastState.update(rewards, rewardsHash)

    @wg_async
    def __onTokensUpdate(self, diff, _):
        if diff.get('tokens'):
            yield wg_await(delay(SERVER_TICK_LENGTH))
            if _g_entryLastState.rewards and not self.__epicController.getNotChosenRewardTokens():
                self._rawUpdate()

    def __onProgressionClick(self):
        if self.__epicController.getNotChosenRewardCount() and isFinishedCycleState():
            showEpicRewardsSelectionWindow()
        else:
            ProgressionScreenState.goTo()

    def __onCombatReservesClick(self):
        FrontlineBattleAbilitiesLoadoutState.goTo(**BattleAbilitiesLoadoutParams.parameters)

    def __onSpaceCreate(self):
        self.queueUpdate()

    def __onEpicUpdated(self, *_):
        self.queueUpdate()

    def __onGameModeStatusChange(self):
        state, _, _ = getFrontlineState()
        if self.__gameModeStatus != state:
            self.__gameModeStatus = state
            self._rawUpdate()

    def __onVehicleRentClick(self):
        setRentBannerClicked()
        showShop(getRentVehicleUrl())

    def __onCacheResync(self, reason, diff):
        if reason == CACHE_SYNC_REASON.CLIENT_UPDATE and GUI_ITEM_TYPE.VEHICLE in diff:
            self.__setRentHightlighted()
            self.__updateBattleAbilitiesPanel()

    def __setRentHightlighted(self):
        isRentHightlighted = not (isRentBannerClicked() or self.__epicController.hasSuitableVehicles(~REQ_CRITERIA.VEHICLE.EXPIRED_RENT))
        with self.viewModel.transaction() as vm:
            vm.setIsRentHighlighted(isRentHightlighted)

    def __fillWidgetModel(self, vm):
        modeStatus = self.__gameModeStatus
        vm.setIsCurrentCycleActive(self.__epicController.isCurrentCycleActive())
        vm.setModeState(modeStatus.value)
        progressTier = self.__epicController.getCurrentLevel()
        vm.setCurrentTier(progressTier)
        vm.setIsMaxLevel(self.__epicController.isMaxLevel())
        vm.setCurrentProgress(self.__epicController.getCurrentProgress())
        vm.setTotalProgress(self.__epicController.getPointsProgressForLevel(progressTier))
        vm.setCombatReservesPoints(self.__epicController.getSkillPoints() if not isFinishedCycleState(modeStatus) and not isAnnouncedCycleState(modeStatus) else 0)
        vehicleLevels = self.__epicController.getValidVehicleLevels()
        vehiclesLevel = toRangeString(vehicleLevels) if isRomanNumberForbidden() else toRomanRangeString(vehicleLevels)
        vm.setRentalVehicleLevel(vehiclesLevel)

    def __updateBattleAbilitiesPanel(self):
        ctrl = self.__epicController
        isSuitable = ctrl.isCurVehicleSuitable() and any((ctrl.isCurVehicleSuitable(criteria, True) for criteria in self.__abilitiesPanelCriteria))
        with self.viewModel.transaction() as vm:
            vm.setIsSelectedSuitableVehicle(isSuitable)

    def __onChangedVehicle(self):
        self.__updateBattleAbilitiesPanel()
