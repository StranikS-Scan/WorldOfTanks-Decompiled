# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/hangar/fun_random_hangar.py
from __future__ import absolute_import
import typing
from ClientSelectableCameraObject import ClientSelectableCameraObject
from CurrentVehicle import g_currentPreviewVehicle, g_currentVehicle
from PlayerEvents import g_playerEvents
from account_helpers.AccountSettings import HANGAR_VIEW_SETTINGS, HANGAR_KEY_BINDINGS
from frameworks.wulf import WindowFlags
from fun_random.gui.filters.fun_random_carousel_filter import FunRandomCarouselFilter
from fun_random.gui.impl.lobby.hangar.base.fun_vehicles_filter_component import FunRandomVehiclesFilterComponent
from fun_random.gui.impl.lobby.hangar.presenters.fun_random_loadout_presenter import FunRandomLoadoutPresenter
from fun_random.gui.impl.lobby.hangar.presenters.fun_random_modifiers_presenter import FunRandomModifiersPresenter
from fun_random.gui.impl.lobby.hangar.presenters.fun_random_mode_state_presenter import FunRandomModeStatePresenter
from fun_random.gui.impl.lobby.hangar.presenters.fun_random_vehicle_filters_presenter import FunRandomVehicleFiltersDataProvider
from fun_random.gui.impl.lobby.hangar.presenters.fun_random_vehicles_info_presenter import FunRandomVehiclesInfoPresenter
from fun_random.gui.impl.lobby.hangar.presenters.fun_random_vehicle_inventory_presenter import FunRandomVehicleInventoryPresenter
from fun_random.gui.impl.lobby.hangar.presenters.fun_random_user_missions_presenter import FunRandomUserMissionsPresenter
from fun_random.gui.impl.lobby.hangar.presenters.fun_random_vehicle_menu_presenter import FunRandomVehiclesMenuPresenter
from gui.app_loader import app_getter
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.game_loading.resources.consts import Milestones
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.common.router_model import RouterModel
from gui.impl.gen.view_models.views.lobby.hangar.hangar_settings_model import HangarSettingsModel
from gui.impl.gen.view_models.views.lobby.hangar.key_bindings_model import KeyBindingsModel
from gui.impl.lobby.common.presenters.dynamic_economics_presenter import DynamicEconomicsPresenter
from gui.impl.lobby.common.presenters.settings_presenter import SettingsPresenter
from gui.impl.lobby.hangar.base.account_styles import AccountStyles
from gui.impl.lobby.hangar.presenters.crew_presenter import CrewPresenter
from gui.impl.lobby.hangar.presenters.hangar_vehicle_params_presenter import HangarVehicleParamsPresenter
from gui.impl.lobby.hangar.presenters.hero_tank_presenter import HeroTankPresenter
from gui.impl.lobby.hangar.presenters.main_menu_presenter import MainMenuPresenter
from gui.impl.lobby.hangar.presenters.pet_object_tooltip_presenter import PetObjectTooltipPresenter
from gui.impl.lobby.hangar.presenters.space_interaction_presenter import SpaceInteractionPresenter
from gui.impl.lobby.hangar.presenters.teaser_presenter import TeaserPresenter
from gui.impl.lobby.hangar.presenters.utils import getMenuItems
from gui.impl.lobby.hangar.presenters.vehicle_statistics_presenter import VehiclesStatisticsPresenter
from gui.impl.lobby.hangar.random.sound_manager import RANDOM_HANGAR_SOUND_SPACE
from gui.impl.lobby.hangar.base.blur import RandomHangarBlur
from gui.impl.pub import WindowImpl
from gui.impl.pub.view_component import ViewComponent
from gui.lobby_state_machine.router import SubstateRouter
from gui.lobby_state_machine.routable_view import IRoutableView
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from gui.shared.event_dispatcher import showLobbyMenu
from gui.shared.utils.requesters import REQ_CRITERIA
from hangar_selectable_objects import HangarSelectableLogic
from helpers import dependency
from helpers.statistics import HANGAR_LOADING_STATE
from shared_utils import nextTick
from skeletons.helpers.statistics import IStatisticsCollector
if typing.TYPE_CHECKING:
    from gui.impl.pub.view_impl import TViewModel
    from hangar_selectable_objects.interfaces import ISelectableLogic

class FunRandomHangarWindow(WindowImpl):
    _statsCollector = dependency.descriptor(IStatisticsCollector)

    def __init__(self, layer, **kwargs):
        super(FunRandomHangarWindow, self).__init__(content=FunRandomHangar(), wndFlags=WindowFlags.WINDOW, layer=layer)

    def _onReady(self):
        super(FunRandomHangarWindow, self)._onReady()
        self._statsCollector.noteHangarLoadingState(HANGAR_LOADING_STATE.HANGAR_UI_READY)
        g_playerEvents.onLoadingMilestoneReached(Milestones.HANGAR_UI_READY)


class FunRandomHangar(ViewComponent[RouterModel], IRoutableView):
    _COMMON_SOUND_SPACE = RANDOM_HANGAR_SOUND_SPACE

    def __init__(self, layoutId=R.views.fun_random.mono.lobby.hangar(), model=RouterModel):
        super(FunRandomHangar, self).__init__(layoutId, model)
        self.__router = None
        self.__inputManager = None
        self.__accountStyles = AccountStyles()
        self.__carouselFilter = FunRandomCarouselFilter()
        self.__vehicleInvFilter = FunRandomVehiclesFilterComponent(REQ_CRITERIA.INVENTORY)
        self.__blur = RandomHangarBlur()
        return

    @property
    def blur(self):
        return self.__blur

    def getRouterModel(self):
        return self.getViewModel()

    def _getChildComponents(self):
        common = R.aliases.common.shared
        hangar = R.aliases.hangar.shared
        battleModifiersHangar = R.aliases.battle_modifiers.shared
        funRandom = R.aliases.fun_random.shared
        return {common.DynamicEconomics(): DynamicEconomicsPresenter,
         hangar.VehiclesInfo(): lambda : FunRandomVehiclesInfoPresenter(self.__vehicleInvFilter),
         hangar.VehiclesStatistics(): lambda : VehiclesStatisticsPresenter(self.__vehicleInvFilter, self.__accountStyles),
         hangar.Loadout(): FunRandomLoadoutPresenter,
         hangar.Crew(): CrewPresenter,
         hangar.VehicleParams(): HangarVehicleParamsPresenter,
         hangar.VehiclesInventory(): lambda : FunRandomVehicleInventoryPresenter(self.__vehicleInvFilter),
         hangar.VehicleFilters(): lambda : FunRandomVehicleFiltersDataProvider(self.__carouselFilter),
         hangar.MainMenu(): lambda : MainMenuPresenter(getMenuItems()),
         hangar.VehicleMenu(): FunRandomVehiclesMenuPresenter,
         hangar.SpaceInteraction(): lambda : SpaceInteractionPresenter(self.__createSelectableLogic()),
         hangar.Teaser(): TeaserPresenter,
         hangar.HeroTank(): HeroTankPresenter,
         hangar.ModeState(): FunRandomModeStatePresenter,
         hangar.Settings(): lambda : SettingsPresenter(HangarSettingsModel, HANGAR_VIEW_SETTINGS),
         hangar.KeyBindings(): lambda : SettingsPresenter(KeyBindingsModel, HANGAR_KEY_BINDINGS, readOnly=True),
         hangar.PetObjectTooltip(): PetObjectTooltipPresenter,
         battleModifiersHangar.Modifiers(): FunRandomModifiersPresenter,
         funRandom.UserMissions(): FunRandomUserMissionsPresenter}

    def _finalize(self):
        super(FunRandomHangar, self)._finalize()
        self.__vehicleInvFilter.destroy()
        self.__accountStyles.destroy()
        self.__router.fini()
        self.__inputManager = None
        self.__blur.destroy()
        self.__blur = None
        return

    def _subscribe(self):
        super(FunRandomHangar, self)._subscribe()
        self.__inputManager.addEscapeListener(self.__escapeHandler)

    def _unsubscribe(self):
        self.__inputManager.removeEscapeListener(self.__escapeHandler)
        super(FunRandomHangar, self)._unsubscribe()

    def _onLoading(self, *args, **kwargs):
        self.__initializeSubSystems()
        self.__blur.init()
        super(FunRandomHangar, self)._onLoading(*args, **kwargs)

    def _onShown(self):
        super(FunRandomHangar, self)._onShown()
        nextTick(ClientSelectableCameraObject.switchCamera)()
        g_eventBus.handleEvent(events.HangarCustomizationEvent(events.HangarCustomizationEvent.RESET_VEHICLE_MODEL_TRANSFORM), scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.handleEvent(events.PetSystemEvent(events.PetSystemEvent.MEDAL_ANIMATION_SHOW), scope=EVENT_BUS_SCOPE.LOBBY)
        g_currentPreviewVehicle.selectNoVehicle()
        if g_currentVehicle.isPresent():
            g_currentVehicle.refreshModel()

    @app_getter
    def __app(self):
        return None

    def __initializeSubSystems(self):
        lsm = getLobbyStateMachine()
        self.__router = SubstateRouter(lsm, self, lsm.getStateFromView(self))
        self.__inputManager = self.__app.gameInputManager
        self.__router.init()
        self.__accountStyles.initialize()
        self.__vehicleInvFilter.initialize()

    def __createSelectableLogic(self):
        return HangarSelectableLogic()

    def __escapeHandler(self):
        showLobbyMenu()
