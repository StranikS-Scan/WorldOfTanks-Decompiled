# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/hangar_view.py
from __future__ import absolute_import
import typing
import logging
from CurrentVehicle import g_currentPreviewVehicle
from account_helpers.AccountSettings import HANGAR_KEY_BINDINGS, HANGAR_VIEW_SETTINGS
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.impl.gen.view_models.views.lobby.hangar.hangar_settings_model import HangarSettingsModel
from gui.impl.gen.view_models.views.lobby.hangar.key_bindings_model import KeyBindingsModel
from gui.impl.lobby.common.presenters.settings_presenter import SettingsPresenter
from gui.impl.lobby.common.presenters.vehicles_info_presenter import VehiclesInfoPresenter
from gui.impl.lobby.hangar.base.account_styles import AccountStyles
from gui.impl.lobby.hangar.presenters.crew_presenter import CrewPresenter
from gui.impl.lobby.hangar.presenters.lootbox_entry_point_presenter import LootboxEntryPointPresenter
from gui.impl.lobby.hangar.presenters.main_menu_presenter import MainMenuPresenter
from gui.impl.lobby.hangar.presenters.optional_devices_assistant_presenter import OptionalDevicesAssistantPresenter
from gui.impl.lobby.hangar.presenters.utils import getSharedMenuItems
from gui.impl.lobby.hangar.presenters.vehicle_filters_presenter import VehicleFiltersDataProvider
from gui.impl.lobby.hangar.presenters.vehicle_menu_presenter import VehicleMenuPresenter
from gui.impl.lobby.hangar.presenters.vehicle_playlists_presenter import VehiclePlaylistsPresenter
from gui.impl.pub import WindowImpl
from gui.impl.pub.view_component import ViewComponent
from gui.lobby_state_machine.routable_view import IRoutableView
from gui.lobby_state_machine.router import SubstateRouter
from gui.shared.event_dispatcher import showLobbyMenu
from last_stand.gui.impl.lobby.base_view import SwitcherPresenter
from last_stand.gui.impl.lobby.battle_result_view import BattleResultView
from last_stand.gui.impl.lobby.ls_vehicle_params_view import LSVehicleParamsPresenter
from last_stand.gui.impl.lobby.vehicles_data_providers.ls_vehicle_daily_presenter import LSVehiclesDailyPresenter
from last_stand.gui.impl.lobby.vehicles_data_providers.ls_vehicle_filter import LSBattleCarouselFilter
from last_stand.gui.impl.lobby.vehicles_data_providers.ls_vehicle_inventory_presenter import LSVehicleInventoryPresenter
from last_stand.gui.impl.lobby.vehicles_data_providers.ls_vehicle_statistics_presenter import LSVehiclesStatisticsPresenter
from last_stand.gui.impl.lobby.vehicles_data_providers.ls_vehicles_filter_component import LSVehiclesFilterComponent
from last_stand.gui.impl.lobby.widgets.ls_loadout import LastStandLoadoutPresenter
from last_stand.gui.impl.lobby.widgets.parallax_view import ParallaxView
from last_stand.skeletons.difficulty_level_controller import IDifficultyLevelController
from frameworks.wulf import WindowStatus, WindowFlags
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.app_loader import app_getter
from gui.impl.gen import R
from gui.impl.lobby.common.tooltips.extended_text_tooltip import ExtendedTextTooltip
from gui.shared import g_eventBus, events
from last_stand.gui.impl.gen.view_models.views.lobby.hangar_view_model import HangarViewModel
from last_stand.gui.impl.lobby.widgets.difficulty_view import DifficultyView
from last_stand.gui.shared.event_dispatcher import showInfoPage, showNarrationWindowView
from last_stand.skeletons.ls_controller import ILSController
from last_stand.gui.sounds.sound_constants import HANGAR_SOUND_SETTINGS
from helpers import dependency
from skeletons.gui.impl import IGuiLoader, INotificationWindowController
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.account_helpers.settings_core import ISettingsCore
_logger = logging.getLogger(__name__)

class HangarView(ViewComponent[HangarViewModel], IRoutableView):
    _guiLoader = dependency.descriptor(IGuiLoader)
    lsCtrl = dependency.descriptor(ILSController)
    _hangarSpace = dependency.descriptor(IHangarSpace)
    _notificationMgr = dependency.descriptor(INotificationWindowController)
    _settingsCore = dependency.descriptor(ISettingsCore)
    _difficultyController = dependency.descriptor(IDifficultyLevelController)
    _COMMON_SOUND_SPACE = HANGAR_SOUND_SETTINGS
    LAYOUT_ID = R.views.last_stand.mono.lobby.hangar()

    def __init__(self, layoutId=LAYOUT_ID, model=HangarViewModel):
        super(HangarView, self).__init__(layoutId, model)
        self.__inputManager = None
        self.__ammoPanel = None
        self.__prevOptimizationEnabled = False
        self.__selectedMissionIndex = 1
        self.__needSlideToNext = False
        self._router = None
        self.__allModeVehicleFilter = LSVehiclesFilterComponent(onlySuitableVehicles=False)
        self.__accountVehicleFilter = LSVehiclesFilterComponent()
        self.__carouselFilter = LSBattleCarouselFilter()
        self.__carouselFilter.setDisabledUpdateCriteries(True)
        self.__accountStyles = AccountStyles()
        return

    @property
    def viewModel(self):
        return super(HangarView, self).getViewModel()

    def getRouterModel(self):
        return self.getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.common.tooltips.ExtendedTextTooltip():
            text = event.getArgument('text', '')
            stringifyKwargs = event.getArgument('stringifyKwargs', '')
            return ExtendedTextTooltip(text, stringifyKwargs)
        return super(HangarView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        self.__inputManager = self.__app.gameInputManager
        self.__fillCore()
        self.__allModeVehicleFilter.initialize()
        self.__accountVehicleFilter.initialize()
        self.__accountStyles.initialize()
        self._initializeRouter()
        super(HangarView, self)._onLoading()

    def _onLoaded(self, *args, **kwargs):
        super(HangarView, self)._onLoaded(*args, **kwargs)
        if g_currentPreviewVehicle is not None:
            g_currentPreviewVehicle.selectNoVehicle()
        return

    def _finalize(self):
        self.__accountVehicleFilter.destroy()
        self.__accountVehicleFilter = None
        self.__allModeVehicleFilter.destroy()
        self.__allModeVehicleFilter = None
        self._router.fini()
        self._router = None
        self.__accountStyles.destroy()
        self.__accountStyles = None
        self.__carouselFilter = None
        super(HangarView, self)._finalize()
        return

    def _getEvents(self):
        return [(self._guiLoader.windowsManager.onWindowStatusChanged, self.__windowStatusChanged),
         (self.viewModel.onAboutClick, self.__onAboutClick),
         (self.viewModel.onViewLoaded, self.__onViewLoaded),
         (self.viewModel.onNarrationClick, self.__onNarrationClick),
         (self.lsCtrl.onSettingsUpdate, self.__onSettingsUpdated),
         (self._difficultyController.onChangeDifficultyLevel, self.__setBackground),
         (self._difficultyController.onChangeDifficultyLevelStatus, self.__setBackground)]

    def _subscribe(self):
        super(HangarView, self)._subscribe()
        self.__inputManager.addEscapeListener(self.__escapeHandler)

    def _unsubscribe(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__inputManager.removeEscapeListener(self.__escapeHandler)
        self.__inputManager = None
        super(HangarView, self)._unsubscribe()
        return

    def _getChildComponents(self):
        from last_stand.gui.impl.lobby.widgets.user_missions_view import LastStandUserMissionsPresenter
        lastStand = R.aliases.last_stand.shared
        coreRandom = R.aliases.hangar.shared
        return {lastStand.Switcher(): SwitcherPresenter,
         lastStand.Difficulty(): DifficultyView,
         lastStand.Parallax(): ParallaxView,
         coreRandom.MainMenu(): lambda : MainMenuPresenter(getSharedMenuItems()),
         lastStand.Gsw(): LastStandUserMissionsPresenter,
         lastStand.VehiclesDaily(): lambda : LSVehiclesDailyPresenter(self.__accountVehicleFilter),
         coreRandom.Loadout(): LastStandLoadoutPresenter,
         coreRandom.Crew(): CrewPresenter,
         coreRandom.VehiclesInfo(): lambda : VehiclesInfoPresenter(self.__allModeVehicleFilter),
         coreRandom.VehiclesStatistics(): lambda : LSVehiclesStatisticsPresenter(self.__accountVehicleFilter, self.__accountStyles),
         coreRandom.VehicleParams(): LSVehicleParamsPresenter,
         coreRandom.VehiclesInventory(): lambda : LSVehicleInventoryPresenter(self.__accountVehicleFilter),
         coreRandom.VehicleFilters(): lambda : VehicleFiltersDataProvider(self.__carouselFilter),
         coreRandom.VehicleMenu(): VehicleMenuPresenter,
         coreRandom.LootboxEntryPoint(): LootboxEntryPointPresenter,
         coreRandom.VehiclePlaylists(): VehiclePlaylistsPresenter,
         coreRandom.KeyBindings(): lambda : SettingsPresenter(KeyBindingsModel, HANGAR_KEY_BINDINGS, readOnly=True),
         coreRandom.Settings(): lambda : SettingsPresenter(HangarSettingsModel, HANGAR_VIEW_SETTINGS),
         coreRandom.OptionalDevicesAssistant(): OptionalDevicesAssistantPresenter}

    def _initializeRouter(self):
        lsm = getLobbyStateMachine()
        self._router = SubstateRouter(lsm, self, lsm.getStateFromView(self))
        self._router.init()

    def _onClose(self):
        pass

    def __escapeHandler(self):
        showLobbyMenu()

    def __onSettingsUpdated(self):
        self.__fillCore()

    @app_getter
    def __app(self):
        return None

    def __setBackground(self, *args, **kwargs):
        level = self._difficultyController.getSelectedLevel()
        levelInfo = self._difficultyController.getLevelInfo(level)
        if levelInfo is None or not levelInfo.isUnlock:
            level = self._difficultyController.getLastSelectedLevel()
        with self.viewModel.transaction() as tx:
            tx.setSelectedStory(level)
        return

    def __fillCore(self):
        with self.viewModel.transaction() as tx:
            tx.setIsInfoEnabled(self.lsCtrl.isInfoPageEnabled())
            tx.setIsLootBoxEntryPointEnabled(self.lsCtrl.isLootBoxEntryPointEnabled())
            self.__setBackground()

    def __onAboutClick(self):
        showInfoPage()

    def __windowStatusChanged(self, uniqueID, newStatus):
        if newStatus == WindowStatus.DESTROYING:
            window = self._guiLoader.windowsManager.getWindow(uniqueID)
            if window is None or window.content is None:
                return
            if isinstance(window.content, BattleResultView) and self._notificationMgr.activeQueueLength == 0:
                self.viewModel.setShowDailyAnim(not self.viewModel.getShowDailyAnim())
        return

    def __onViewLoaded(self):
        g_eventBus.handleEvent(events.ViewReadyEvent(self.layoutID))

    def __onNarrationClick(self):
        showNarrationWindowView()


class HangarWindow(WindowImpl):

    def __init__(self, layer, **kwargs):
        super(HangarWindow, self).__init__(content=HangarView(), wndFlags=WindowFlags.WINDOW, layer=layer)
