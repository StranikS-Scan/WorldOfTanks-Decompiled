# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/halloween/hangar_view.py
import typing
import logging
import BigWorld
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.view.lobby.LobbyMenu import LobbyMenu
from gui.impl.gen import R
from gui.impl.lobby.halloween.hangar_event_view import HangarEventView
from gui.prb_control import prb_getters
from helpers import dependency
from gui.app_loader import sf_lobby
from PlayerEvents import g_playerEvents
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared import IItemsCache
from skeletons.gui.app_loader import IAppLoader
from HalloweenHangarTank import HalloweenHangarTank
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.afk_controller import IAFKController
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.utils.functions import replaceHyphenToUnderscore
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_event_controller import IGameEventController
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.impl.backport import createTooltipData, BackportTooltipWindow
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from account_helpers.settings_core.ServerSettingsManager import UIGameEventKeys
from gui.impl.lobby.halloween.sound_constants import EVENT_HANGAR_SOUND_SPACE
from frameworks.wulf import ViewSettings, ViewFlags, WindowLayer, WindowStatus
from gui.impl.lobby.halloween.hangar_selectable_view import HangarSelectableView
from gui.Scaleform.daapi.view.lobby.event_boards.formaters import formatTimeAndDate
from gui.impl.lobby.halloween.tooltips.daily_widget_tooltip import DailyWidgetTooltip
from gui.impl.gen.view_models.views.lobby.halloween.shop_view_model import PageTypeEnum
from gui.impl.lobby.halloween.event_difficulty_panel_view import EventDifficultyPanelView
from gui.shared.event_dispatcher import showAmmunitionSetupView, showShopView, showMetaView, showCustomizationShopView, showHalloweenKingRewardPreview, showBrowserOverlayView
from gui.impl.lobby.halloween.sub_views.event_ammunition_panel import EventAmmunitionPanel
from gui.impl.lobby.halloween.event_keys_counter_panel_view import EventKeysCounterPanelView
from gui.impl.gen.view_models.views.lobby.halloween.hangar_view_model import HangarViewModel
from gui.impl.gen.view_models.views.lobby.halloween.hangar_tank_model import HangarTankModel
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents, CameraMovementStates
from gui.impl.lobby.tank_setup.ammunition_setup.base_hangar import BaseHangarAmmunitionSetupView
from gui.impl.lobby.halloween.event_helpers import closeEvent, moveCamera, notifyCursorOver3DScene, getCurrentVehicle
from gui.impl.gen.view_models.views.lobby.halloween.event_keys_counter_panel_view_model import VisualTypeEnum
from gui.server_events.events_helpers import EventInfoModel
from gui.impl.lobby.halloween.event_helpers import isEvent
if typing.TYPE_CHECKING:
    from gui.shared.gui_items import Vehicle
_logger = logging.getLogger(__name__)
_BACKGROUND_ALPHA = 0.0

class HangarView(HangarSelectableView, HangarEventView):
    _COMMON_SOUND_SPACE = EVENT_HANGAR_SOUND_SPACE
    _INFO_PAGE_KEY = 'infoPageEventBattle'
    _MAX_REWARDS_NUM = 8
    __slots__ = ('__layoutID', '__isVehicleCameraReadyForC11n', '__vehiclesController', '__ammoPanel', '__isUnitJoiningInProgress', '__timer', '__difficultyPanel', '__keysCounterPanel')
    _gameEventController = dependency.descriptor(IGameEventController)
    _itemsCache = dependency.descriptor(IItemsCache)
    _eventsCache = dependency.descriptor(IEventsCache)
    _uiLoader = dependency.instance(IGuiLoader)
    _settingsCore = dependency.descriptor(ISettingsCore)
    _afkController = dependency.descriptor(IAFKController)
    _appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.model = HangarViewModel()
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        super(HangarView, self).__init__(settings)
        self.__layoutID = layoutID
        self.__isVehicleCameraReadyForC11n = False
        self.__vehiclesController = self._gameEventController.getVehiclesController()
        self.__ammoPanel = None
        self.__difficultyPanel = None
        self.__keysCounterPanel = None
        self.__isUnitJoiningInProgress = False
        self.__timer = None
        return

    @property
    def viewModel(self):
        return super(HangarView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            tankId = event.getArgument('tankId', None)
            specialArgs = []
            if tankId is not None:
                vehicleId = -tankId if tankId < 0 else self._itemsCache.items.getVehicle(tankId).intCD
                specialArgs = [vehicleId]
                tooltipId = TOOLTIPS_CONSTANTS.EVENT_CAROUSEL_VEHICLE
            if tooltipId == TOOLTIPS_CONSTANTS.EVENT_BAN_INFO:
                specialArgs = [self._afkController.banExpiryTime]
            window = BackportTooltipWindow(createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=specialArgs), self.getParentWindow())
            window.load()
            return window
        else:
            return super(HangarView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        return DailyWidgetTooltip() if contentID == R.views.lobby.halloween.tooltips.DailyTooltip() else None

    def _onLoading(self):
        super(HangarView, self)._onLoading()
        self._afkController.showAFKWindows()
        g_eventBus.addListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__handleSelectedEntityUpdated)
        self.viewModel.onClose += self.__onClose
        self.viewModel.onEscape += self.__onEscape
        self.viewModel.onTankChanged += self.__onTankChanged
        self.viewModel.onRedirectTo += self.__onRedirectTo
        self.viewModel.onMoveSpace += self.__onMoveSpace
        self.viewModel.onOverScene += self.__onCursorOver3DScene
        self._eventsCache.onSyncCompleted += self.__onSyncCompleted
        self.__vehiclesController.onDailyRewardsUpdated += self.__onDailyRewardsUpdated
        self._settingsCore.onSettingsChanged += self.__onSettingsChanged
        self._gameEventController.onIngameEventsUpdated += self.__updateEvent
        g_currentVehicle.onChanged += self.__onCurrentVehicleChanged
        g_currentPreviewVehicle.onChanged += self.__onCurrentVehicleChanged
        g_playerEvents.onPrebattleInvitationAccepted += self.__onPrebattleInvitationAccepted
        self._uiLoader.windowsManager.onWindowStatusChanged += self.__windowStatusChanged
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitJoined += self.__onUnitJoined
        g_clientUpdateManager.addCallbacks({'cache.vehsLock': self.__onVehicleLockUpdated})
        self.__ammoPanel = EventAmmunitionPanel()
        self.setChildView(self.__ammoPanel.layoutID, self.__ammoPanel)
        self.__difficultyPanel = EventDifficultyPanelView()
        self.setChildView(self.__difficultyPanel.layoutID, self.__difficultyPanel)
        self.__keysCounterPanel = EventKeysCounterPanelView(VisualTypeEnum.HANGAR)
        self.setChildView(self.__keysCounterPanel.layoutID, self.__keysCounterPanel)
        self.__ammoPanel.onPanelSectionSelected += self.__onPanelSectionSelected
        self._gameEventController.onRewardBoxUpdated += self.__onRewardBoxUpdated
        self._afkController.onBanUpdated += self.__onBanUpdated
        self.__timer = CallbackDelayer()
        app = self._appLoader.getApp()
        app.setBackgroundAlpha(_BACKGROUND_ALPHA)
        self.__fillViewModel()
        notifyCursorOver3DScene(False)

    def _initialize(self, *args, **kwargs):
        super(HangarView, self)._initialize(*args, **kwargs)
        g_currentVehicle.selectEventVehicle()

    def _finalize(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_eventBus.removeListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__handleSelectedEntityUpdated)
        self.viewModel.onClose -= self.__onClose
        self.viewModel.onEscape -= self.__onEscape
        self.viewModel.onTankChanged -= self.__onTankChanged
        self.viewModel.onRedirectTo -= self.__onRedirectTo
        self.viewModel.onMoveSpace -= self.__onMoveSpace
        self.viewModel.onOverScene -= self.__onCursorOver3DScene
        self._eventsCache.onSyncCompleted -= self.__onSyncCompleted
        self.__vehiclesController.onDailyRewardsUpdated -= self.__onDailyRewardsUpdated
        self._settingsCore.onSettingsChanged -= self.__onSettingsChanged
        self._gameEventController.onIngameEventsUpdated -= self.__updateEvent
        g_currentVehicle.onChanged -= self.__onCurrentVehicleChanged
        g_currentPreviewVehicle.onChanged -= self.__onCurrentVehicleChanged
        if self.__ammoPanel is not None:
            self.__ammoPanel.onPanelSectionSelected -= self.__onPanelSectionSelected
        g_playerEvents.onPrebattleInvitationAccepted -= self.__onPrebattleInvitationAccepted
        self._uiLoader.windowsManager.onWindowStatusChanged -= self.__windowStatusChanged
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitJoined -= self.__onUnitJoined
        if self.__timer is not None:
            self.__timer.clearCallbacks()
            self.__timer = None
        self._gameEventController.onRewardBoxUpdated -= self.__onRewardBoxUpdated
        self._afkController.onBanUpdated -= self.__onBanUpdated
        super(HangarView, self)._finalize()
        return

    def __onMoveSpace(self, args=None):
        if args is None:
            return
        else:
            dx = args.get('dx')
            dy = args.get('dy')
            dz = args.get('dz')
            moveCamera(dx, dy, dz)
            return

    def __onCursorOver3DScene(self, args=None):
        if args is None:
            _logger.error("Can't notified cursor over changed. args=None. Please fix JS")
            return
        else:
            notifyCursorOver3DScene(args.get('isOver3dScene', False))
            return

    def __onTankChanged(self, args):
        if args is not None:
            vehId = int(args.get('id'))
            g_currentVehicle.selectEventVehicle(vehId)
        else:
            _logger.error("Can't change selected general. args=None. Please fix JS")
        return

    def __onRedirectTo(self, args=None):
        page = args.get('page') if 'page' in args else None
        if page == HangarViewModel.PACKAGES:
            showShopView(PageTypeEnum.VEHICLES)
        elif page in (HangarViewModel.REWARDS, HangarViewModel.MEMORIES):
            showMetaView(page)
        elif page == HangarViewModel.STYLES:
            showCustomizationShopView()
        elif page == HangarViewModel.INFO:
            url = GUI_SETTINGS.lookup(self._INFO_PAGE_KEY)
            showBrowserOverlayView(url, VIEW_ALIAS.WEB_VIEW_TRANSPARENT)
        return

    def __updateEvent(self):
        if not self._eventsCache.isEventEnabled():
            closeEvent()

    def __onClose(self):
        closeEvent()

    def __onEscape(self):
        dialogsContainer = self.__app.containerManager.getContainer(WindowLayer.TOP_WINDOW)
        if not dialogsContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LOBBY_MENU}):
            g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_MENU)), scope=EVENT_BUS_SCOPE.LOBBY)
        notifyCursorOver3DScene(False)

    def __onCurrentVehicleChanged(self):
        if not self._eventsCache.isEventEnabled():
            closeEvent()
            return
        else:
            if g_currentVehicle.item is None and g_currentPreviewVehicle.item is None and not g_currentPreviewVehicle.isPresent() and isEvent():
                g_currentVehicle.selectEventVehicle()
            with self.viewModel.transaction() as tx:
                self.__createTankModel(getCurrentVehicle(self._itemsCache), tx.selectedTank)
                self.__fillDailyWidget(tx)
            return

    def __onBanUpdated(self, *_):
        with self.viewModel.transaction() as tx:
            self.__fillAfk(tx)

    def __fillViewModel(self):
        if not self._eventsCache.isEventEnabled():
            return
        with self.viewModel.transaction() as tx:
            self.__onCurrentVehicleChanged()
            self.__fillCarousel(tx)
            self.__fillMetaWidget(tx)
            self.__fillDailyWidget(tx)
            self.__fillAfk(tx)

    def __onDailyRewardsUpdated(self):
        with self.viewModel.transaction() as tx:
            self.__fillCarousel(tx)

    def __onSyncCompleted(self):
        with self.viewModel.transaction() as tx:
            self.__fillCarousel(tx)
            tx.getTanks().invalidate()
            self.__fillMetaWidget(tx)
            self.__fillDailyWidget(tx)
            self.__fillAfk(tx)

    def __onRewardBoxUpdated(self):
        with self.viewModel.transaction() as tx:
            self.__fillMetaWidget(tx)

    def __onSettingsChanged(self, _):
        with self.viewModel.transaction() as tx:
            self.__fillMetaWidget(tx)

    def __onVehicleLockUpdated(self, *args):
        self.__fillViewModel()

    @sf_lobby
    def __app(self):
        return None

    def __handleSelectedEntityUpdated(self, event):
        ctx = event.ctx
        if ctx['state'] != CameraMovementStates.FROM_OBJECT:
            entity = BigWorld.entities.get(ctx['entityId'], None)
            if isinstance(entity, HalloweenHangarTank):
                descriptor = entity.typeDescriptor
                if descriptor:
                    if entity.isKingReward:
                        showHalloweenKingRewardPreview(descriptor.type.compactDescr)
                    else:
                        showCustomizationShopView(entity.id)
            self.__checkVehicleCameraState()
        return

    def __checkVehicleCameraState(self):
        vehicleEntity = self._hangarSpace.getVehicleEntity()
        if vehicleEntity is None:
            return
        else:
            self.__isVehicleCameraReadyForC11n = vehicleEntity.state == CameraMovementStates.ON_OBJECT
            return

    def __fillMetaWidget(self, vm):
        availbelProgress = 0
        eventRewardController = self._gameEventController.getEventRewardController()
        value = self._settingsCore.serverSettings.getGameEventStorage().get(UIGameEventKeys.REWARD_BOXES_SHOWN)
        if value is not None:
            rewardBoxes = eventRewardController.rewardBoxesConfig
            for rewardBoxID in eventRewardController.iterAvailbleRewardBoxIDsInOrder():
                rewardBox = rewardBoxes[rewardBoxID]
                if rewardBox.boxIndex < len(rewardBoxes):
                    mask = 1 << rewardBox.boxIndex
                    if not value & mask:
                        availbelProgress += 1

        currentProgress = eventRewardController.getCurrentRewardProgress()
        maxProgress = max(eventRewardController.getMaxRewardProgress(), 0) or self._MAX_REWARDS_NUM
        isFinalRewardReceived = currentProgress > maxProgress
        vm.metaWidget.setIsCompleted(isFinalRewardReceived)
        vm.metaWidget.setMaxProgress(maxProgress)
        vm.metaWidget.setCurrentProgress(min(currentProgress, maxProgress))
        vm.metaWidget.setNewVideoCount(availbelProgress)
        return

    def __fillDailyWidget(self, vm):
        currentVehicle = getCurrentVehicle(self._itemsCache)
        if currentVehicle is None:
            return
        else:
            vm.dailyWidget.setDailyBonus(self.__vehiclesController.getDailyKeysReward(currentVehicle.intCD))
            vm.dailyWidget.setTimer(EventInfoModel.getDailyProgressResetTimeDelta())
            hasDailyQuest = self.__vehiclesController.hasDailyQuest(currentVehicle.intCD)
            vm.selectedTank.setHasDaily(hasDailyQuest)
            return

    def __fillAfk(self, vm):
        vm.afkBanner.setIsAfk(self._afkController.isBanned)
        vm.afkBanner.setAfkTimer(formatTimeAndDate(self._afkController.banExpiryTime))

    def __fillCarousel(self, vm):
        vm.getTanks().clear()
        order = self.__vehiclesController.getVehiclesOrder()
        for idd in order:
            vehicle = self._itemsCache.items.getItemByCD(idd)
            vm.getTanks().addViewModel(self.__createTankModel(vehicle))
            vm.getTanks().invalidate()

    def __createTankModel(self, vehicle, viewModel=None):
        if vehicle is None:
            return
        else:
            vehId = vehicle.invID if vehicle.isInInventory else -vehicle.intCD
            tankModel = HangarTankModel() if viewModel is None else viewModel
            tankModel.setId(vehId)
            tankModel.setName(vehicle.userName)
            tankModel.setType(vehicle.type)
            tankModel.setIconName(replaceHyphenToUnderscore(vehicle.name.replace(':', '-')))
            tankModel.setHasDaily(self.__vehiclesController.hasDailyQuest(vehicle.intCD))
            tankModel.setDailyBonus(self.__vehiclesController.getDailyKeysReward(vehicle.intCD))
            state = HangarTankModel.DEFAULT
            if vehicle.intCD in self.__vehiclesController.getVehiclesForRent() and not vehicle.isInInventory:
                state = HangarTankModel.LOCKED
            elif vehicle.isInBattle:
                state = HangarTankModel.IN_BATTLE
            elif vehicle.isInUnit:
                state = HangarTankModel.IN_PLATOON
            tankModel.setState(state)
            return tankModel

    def __onPanelSectionSelected(self, **kwargs):
        if self._hangarSpace.spaceLoading():
            _logger.warning('Optional Device click was not handled (kwargs=%s). HangarSpace is currently  loading.', kwargs)
        elif not self.__isUnitJoiningInProgress:
            with self.viewModel.transaction() as tx:
                tx.setIsLoadedSetup(True)
                notifyCursorOver3DScene(False)
            showAmmunitionSetupView(**kwargs)

    def __onPrebattleInvitationAccepted(self, _, __):
        self.__isUnitJoiningInProgress = True
        self.__timer.delayCallback(15, self.__onResetUnitJoiningProgress)

    def __onResetUnitJoiningProgress(self):
        self.__isUnitJoiningInProgress = False

    def __onUnitJoined(self, _, __):
        self.__isUnitJoiningInProgress = False
        if self.__timer is not None:
            self.__timer.stopCallback(self.__onResetUnitJoiningProgress)
        return

    def __windowStatusChanged(self, uniqueID, newStatus):
        if newStatus == WindowStatus.DESTROYING:
            window = self._uiLoader.windowsManager.getWindow(uniqueID)
            if window.content is None:
                return
            if isinstance(window.content, BaseHangarAmmunitionSetupView):
                with self.viewModel.transaction() as tx:
                    tx.setIsLoadedSetup(False)
                return
            if isinstance(window.content, LobbyMenu):
                with self.viewModel.transaction() as tx:
                    tx.setIsNeedReload(not tx.getIsNeedReload())
        return
