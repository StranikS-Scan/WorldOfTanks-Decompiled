# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/hangar/comp7_hangar.py
from __future__ import absolute_import
import logging
import typing
from comp7.gui.Scaleform.genConsts.COMP7_HANGAR_ALIASES import COMP7_HANGAR_ALIASES
from comp7.gui.impl.lobby.comp7_helpers.comp7_shared import getComp7Criteria
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.impl.lobby.hangar.base.account_styles import AccountStyles
from gui.lobby_state_machine.router import SubstateRouter
from shared_utils import nextTick
from ClientSelectableCameraObject import ClientSelectableCameraObject
from CurrentVehicle import g_currentPreviewVehicle, g_currentVehicle
from PlayerEvents import g_playerEvents
from comp7.gui.Scaleform.daapi.view.lobby.hangar.carousels.carousel_filter import Comp7CarouselFilter
from comp7.gui.impl.lobby.alert_message_presenter import AlertMessagePresenter
from comp7.gui.impl.lobby.hangar.presenters.comp7_loadout_presenter import Comp7LoadoutPresenter
from comp7.gui.impl.lobby.role_skill_slot_presenter import Comp7RoleSkillSlotPresenter
from comp7.gui.impl.lobby.schedule_presenter import SchedulePresenter
from comp7.gui.impl.lobby.season_modifier_presenter import SeasonModifierPresenter
from comp7.gui.impl.lobby.user_missions_presenter import Comp7UserMissionsPresenter
from frameworks.wulf import WindowFlags
from gui.app_loader import app_getter
from gui.game_loading.resources.consts import Milestones
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.common.router_model import RouterModel
from gui.impl.lobby.hangar.base.vehicles_filter_component import VehiclesFilterComponent
from gui.impl.lobby.hangar.presenters.crew_presenter import CrewPresenter
from gui.impl.lobby.hangar.presenters.hangar_vehicle_params_presenter import HangarVehicleParamsPresenter
from gui.impl.lobby.hangar.presenters.hero_tank_presenter import HeroTankPresenter
from gui.impl.lobby.hangar.presenters.main_menu_presenter import MainMenuPresenter
from comp7.gui.impl.lobby.hangar.presenters.comp7_optional_devices_assistant_presenter import Comp7OptionalDevicesAssistantPresenter
from gui.impl.lobby.hangar.presenters.space_interaction_presenter import SpaceInteractionPresenter
from gui.impl.lobby.hangar.presenters.teaser_presenter import TeaserPresenter
from gui.impl.lobby.hangar.presenters.utils import getMenuItems
from comp7_core.gui.impl.lobby.hangar.presenters.comp7_core_vehicle_filters_presenter import Comp7CoreVehicleFiltersDataProvider
from gui.impl.lobby.hangar.presenters.vehicle_inventory_presenter import VehicleInventoryPresenter
from gui.impl.lobby.hangar.presenters.vehicle_menu_presenter import VehicleMenuPresenter
from gui.impl.lobby.hangar.presenters.vehicle_statistics_presenter import VehiclesStatisticsPresenter
from comp7.gui.impl.lobby.hangar.presenters.comp7_vehicles_info_presenter import Comp7VehiclesInfoPresenter
from gui.impl.lobby.hangar.random.random_hangar import RANDOM_HANGAR_SOUND_SPACE
from gui.impl.pub import WindowImpl
from gui.impl.pub.view_component import ViewComponent
from gui.lobby_state_machine.routable_view import IRoutableView
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.shared.event_dispatcher import showLobbyMenu
from hangar_selectable_objects import HangarSelectableLogic
from helpers import dependency
from helpers.statistics import HANGAR_LOADING_STATE
from skeletons.helpers.statistics import IStatisticsCollector
if typing.TYPE_CHECKING:
    from gui.impl.pub.view_impl import TViewModel
    from hangar_selectable_objects.interfaces import ISelectableLogic
    from typing import Optional
_logger = logging.getLogger(__name__)

class Comp7HangarWindow(WindowImpl):
    _statsCollector = dependency.descriptor(IStatisticsCollector)

    def __init__(self, layer, *_, **__):
        super(Comp7HangarWindow, self).__init__(content=Comp7Hangar(), wndFlags=WindowFlags.WINDOW, layer=layer)

    def _onReady(self):
        self._statsCollector.noteHangarLoadingState(HANGAR_LOADING_STATE.HANGAR_UI_READY)
        g_playerEvents.onLoadingMilestoneReached(Milestones.HANGAR_UI_READY)
        super(Comp7HangarWindow, self)._onReady()


class Comp7Hangar(ViewComponent[RouterModel], IRoutableView):
    _COMMON_SOUND_SPACE = RANDOM_HANGAR_SOUND_SPACE

    def __init__(self, layoutId=R.views.comp7.mono.lobby.hangar(), model=RouterModel):
        super(Comp7Hangar, self).__init__(layoutId, model)
        self.__inputManager = None
        self.__routerObserver = None
        self.__baseCriteria = getComp7Criteria()
        self.__vehicleFilter = VehiclesFilterComponent(self.__baseCriteria)
        self.__carouselFilter = Comp7CarouselFilter()
        self.__carouselFilter.setDisabledUpdateCriteries(True)
        self.__accountStyles = AccountStyles()
        return

    def getRouterModel(self):
        return self.getViewModel()

    def _getChildComponents(self):
        hangar = R.aliases.hangar.shared
        comp7Hangar = R.aliases.comp7.shared
        return {hangar.VehiclesInfo(): lambda : Comp7VehiclesInfoPresenter(self.__vehicleFilter),
         hangar.VehiclesStatistics(): lambda : VehiclesStatisticsPresenter(self.__vehicleFilter, self.__accountStyles),
         hangar.Loadout(): Comp7LoadoutPresenter,
         hangar.Crew(): CrewPresenter,
         hangar.VehicleParams(): HangarVehicleParamsPresenter,
         hangar.VehiclesInventory(): lambda : VehicleInventoryPresenter(self.__baseCriteria),
         hangar.VehicleFilters(): lambda : Comp7CoreVehicleFiltersDataProvider(self.__carouselFilter),
         hangar.MainMenu(): lambda : MainMenuPresenter(getMenuItems()),
         hangar.VehicleMenu(): VehicleMenuPresenter,
         hangar.SpaceInteraction(): lambda : SpaceInteractionPresenter(self.__createSelectableLogic()),
         hangar.Teaser(): TeaserPresenter,
         hangar.HeroTank(): HeroTankPresenter,
         hangar.OptionalDevicesAssistant(): Comp7OptionalDevicesAssistantPresenter,
         comp7Hangar.AlertMessage(): AlertMessagePresenter,
         comp7Hangar.Schedule(): SchedulePresenter,
         comp7Hangar.SeasonModifier(): SeasonModifierPresenter,
         comp7Hangar.RoleSkillSlot(): Comp7RoleSkillSlotPresenter,
         comp7Hangar.UserMissions(): Comp7UserMissionsPresenter}

    def _subscribe(self):
        super(Comp7Hangar, self)._subscribe()
        self.__inputManager.addEscapeListener(self.__escapeHandler)

    def _unsubscribe(self):
        self.__inputManager.removeEscapeListener(self.__escapeHandler)
        super(Comp7Hangar, self)._unsubscribe()

    def _onLoading(self, *args, **kwargs):
        self.__inputManager = self.__app.gameInputManager
        self.__vehicleFilter.initialize()
        self.__accountStyles.initialize()
        super(Comp7Hangar, self)._onLoading(*args, **kwargs)

    def _onShown(self):
        super(Comp7Hangar, self)._onShown()
        nextTick(ClientSelectableCameraObject.switchCamera)()
        g_eventBus.handleEvent(events.HangarCustomizationEvent(events.HangarCustomizationEvent.RESET_VEHICLE_MODEL_TRANSFORM), scope=EVENT_BUS_SCOPE.LOBBY)
        g_currentPreviewVehicle.selectNoVehicle()
        if g_currentVehicle.isPresent():
            g_currentVehicle.refreshModel()

    def _initialize(self, *args, **kwargs):
        super(Comp7Hangar, self)._initialize(*args, **kwargs)
        lsm = getLobbyStateMachine()
        state = lsm.getStateByViewKey(ViewKey(alias=COMP7_HANGAR_ALIASES.COMP7_LOBBY_HANGAR))
        self.__routerObserver = SubstateRouter(lsm, self, state)
        self.__routerObserver.init()

    def _finalize(self):
        super(Comp7Hangar, self)._finalize()
        if self.__routerObserver is not None:
            self.__routerObserver.fini()
        self.__routerObserver = None
        self.__vehicleFilter.destroy()
        self.__vehicleFilter = None
        self.__carouselFilter = None
        self.__baseCriteria = None
        self.__inputManager = None
        self.__accountStyles.destroy()
        self.__accountStyles = None
        return

    @app_getter
    def __app(self):
        return None

    def __createSelectableLogic(self):
        return HangarSelectableLogic()

    def __escapeHandler(self):
        showLobbyMenu()
