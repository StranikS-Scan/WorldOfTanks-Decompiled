# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/hangar/comp7_light_hangar.py
from __future__ import absolute_import
import logging
import typing
from comp7_light.gui.Scaleform.genConsts.COMP7_LIGHT_HANGAR_ALIASES import COMP7_LIGHT_HANGAR_ALIASES
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.impl.lobby.hangar.base.account_styles import AccountStyles
from gui.lobby_state_machine.router import SubstateRouter
from shared_utils import nextTick
from ClientSelectableCameraObject import ClientSelectableCameraObject
from CurrentVehicle import g_currentPreviewVehicle, g_currentVehicle
from PlayerEvents import g_playerEvents
from comp7_light.gui.Scaleform.daapi.view.lobby.hangar.carousels.carousel_filter import Comp7LightCarouselFilter
from comp7_light.gui.impl.lobby.alert_message_presenter import AlertMessagePresenter
from comp7_light.gui.impl.lobby.hangar.presenters.comp7_light_loadout_presenter import Comp7LightLoadoutPresenter
from comp7_light.gui.impl.lobby.role_skill_slot_presenter import Comp7LightRoleSkillSlotPresenter
from comp7_light.gui.impl.lobby.season_modifier_presenter import SeasonModifierPresenter
from comp7_light.gui.impl.lobby.user_missions_presenter import Comp7LightUserMissionsPresenter
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
from comp7_light.gui.impl.lobby.hangar.presenters.comp7_light_optional_devices_assistant_presenter import Comp7LightOptionalDevicesAssistantPresenter
from gui.impl.lobby.hangar.presenters.space_interaction_presenter import SpaceInteractionPresenter
from gui.impl.lobby.hangar.presenters.teaser_presenter import TeaserPresenter
from gui.impl.lobby.hangar.presenters.utils import getMenuItems
from comp7_core.gui.impl.lobby.hangar.presenters.comp7_core_vehicle_filters_presenter import Comp7CoreVehicleFiltersDataProvider
from gui.impl.lobby.hangar.presenters.vehicle_inventory_presenter import VehicleInventoryPresenter
from gui.impl.lobby.hangar.presenters.vehicle_menu_presenter import VehicleMenuPresenter
from gui.impl.lobby.hangar.presenters.vehicle_statistics_presenter import VehiclesStatisticsPresenter
from comp7_light.gui.impl.lobby.hangar.presenters.comp7_light_vehicles_info_presenter import Comp7LightVehiclesInfoPresenter
from gui.impl.lobby.hangar.random.random_hangar import RANDOM_HANGAR_SOUND_SPACE
from gui.impl.pub import WindowImpl
from gui.impl.pub.view_component import ViewComponent
from gui.lobby_state_machine.routable_view import IRoutableView
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.shared.event_dispatcher import showLobbyMenu
from gui.shared.utils.requesters import REQ_CRITERIA
from hangar_selectable_objects import HangarSelectableLogic
from helpers import dependency
from helpers.statistics import HANGAR_LOADING_STATE
from skeletons.helpers.statistics import IStatisticsCollector
if typing.TYPE_CHECKING:
    from gui.shared.utils.requesters import RequestCriteria
    from gui.impl.pub.view_impl import TViewModel
    from hangar_selectable_objects.interfaces import ISelectableLogic
_logger = logging.getLogger(__name__)

def _createComp7LightCriteria():
    comp7LightCriteria = REQ_CRITERIA.INVENTORY
    comp7LightCriteria |= ~REQ_CRITERIA.VEHICLE.MODE_HIDDEN
    comp7LightCriteria |= ~REQ_CRITERIA.VEHICLE.BATTLE_ROYALE
    comp7LightCriteria |= ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE
    return comp7LightCriteria


class Comp7LightHangarWindow(WindowImpl):
    _statsCollector = dependency.descriptor(IStatisticsCollector)

    def __init__(self, layer, *_, **__):
        super(Comp7LightHangarWindow, self).__init__(content=Comp7LightHangar(), wndFlags=WindowFlags.WINDOW, layer=layer)

    def _onReady(self):
        self._statsCollector.noteHangarLoadingState(HANGAR_LOADING_STATE.HANGAR_UI_READY)
        g_playerEvents.onLoadingMilestoneReached(Milestones.HANGAR_UI_READY)
        super(Comp7LightHangarWindow, self)._onReady()


class Comp7LightHangar(ViewComponent[RouterModel], IRoutableView):
    _COMMON_SOUND_SPACE = RANDOM_HANGAR_SOUND_SPACE

    def __init__(self, layoutId=R.views.comp7_light.mono.lobby.hangar(), model=RouterModel):
        super(Comp7LightHangar, self).__init__(layoutId, model)
        self.__inputManager = None
        self.__routerObserver = None
        self.__baseCriteria = _createComp7LightCriteria()
        self.__vehicleFilter = VehiclesFilterComponent(self.__baseCriteria)
        self.__carouselFilter = Comp7LightCarouselFilter()
        self.__carouselFilter.setDisabledUpdateCriteries(True)
        self.__accountStyles = AccountStyles()
        return

    def getRouterModel(self):
        return self.getViewModel()

    def _getChildComponents(self):
        hangar = R.aliases.hangar.shared
        comp7LightHangar = R.aliases.comp7_light.shared
        return {hangar.VehiclesInfo(): lambda : Comp7LightVehiclesInfoPresenter(self.__vehicleFilter),
         hangar.VehiclesStatistics(): lambda : VehiclesStatisticsPresenter(self.__vehicleFilter, self.__accountStyles),
         hangar.Loadout(): Comp7LightLoadoutPresenter,
         hangar.Crew(): CrewPresenter,
         hangar.VehicleParams(): HangarVehicleParamsPresenter,
         hangar.VehiclesInventory(): lambda : VehicleInventoryPresenter(self.__baseCriteria),
         hangar.VehicleFilters(): lambda : Comp7CoreVehicleFiltersDataProvider(self.__carouselFilter),
         hangar.MainMenu(): lambda : MainMenuPresenter(getMenuItems()),
         hangar.VehicleMenu(): VehicleMenuPresenter,
         hangar.SpaceInteraction(): lambda : SpaceInteractionPresenter(self.__createSelectableLogic()),
         hangar.Teaser(): TeaserPresenter,
         hangar.HeroTank(): HeroTankPresenter,
         hangar.OptionalDevicesAssistant(): Comp7LightOptionalDevicesAssistantPresenter,
         comp7LightHangar.AlertMessage(): AlertMessagePresenter,
         comp7LightHangar.SeasonModifier(): SeasonModifierPresenter,
         comp7LightHangar.RoleSkillSlot(): Comp7LightRoleSkillSlotPresenter,
         comp7LightHangar.UserMissions(): Comp7LightUserMissionsPresenter}

    def _subscribe(self):
        super(Comp7LightHangar, self)._subscribe()
        self.__inputManager.addEscapeListener(self.__escapeHandler)

    def _unsubscribe(self):
        self.__inputManager.removeEscapeListener(self.__escapeHandler)
        super(Comp7LightHangar, self)._unsubscribe()

    def _onLoading(self, *args, **kwargs):
        self.__inputManager = self.__app.gameInputManager
        self.__vehicleFilter.initialize()
        self.__accountStyles.initialize()
        super(Comp7LightHangar, self)._onLoading(*args, **kwargs)

    def _onShown(self):
        super(Comp7LightHangar, self)._onShown()
        nextTick(ClientSelectableCameraObject.switchCamera)()
        g_eventBus.handleEvent(events.HangarCustomizationEvent(events.HangarCustomizationEvent.RESET_VEHICLE_MODEL_TRANSFORM), scope=EVENT_BUS_SCOPE.LOBBY)
        g_currentPreviewVehicle.selectNoVehicle()
        if g_currentVehicle.isPresent():
            g_currentVehicle.refreshModel()

    def _initialize(self, *args, **kwargs):
        super(Comp7LightHangar, self)._initialize(*args, **kwargs)
        lsm = getLobbyStateMachine()
        state = lsm.getStateByViewKey(ViewKey(alias=COMP7_LIGHT_HANGAR_ALIASES.COMP7_LIGHT_LOBBY_HANGAR))
        self.__routerObserver = SubstateRouter(lsm, self, state)
        self.__routerObserver.init()

    def _finalize(self):
        super(Comp7LightHangar, self)._finalize()
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
