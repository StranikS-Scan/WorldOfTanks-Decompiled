# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/random/random_hangar.py
from __future__ import absolute_import
import logging
import typing
from ClientSelectableCameraObject import ClientSelectableCameraObject
from CurrentVehicle import g_currentPreviewVehicle, g_currentVehicle
from PlayerEvents import g_playerEvents
from frameworks.wulf import WindowFlags
from gui.app_loader import app_getter
from gui.Scaleform.daapi.view.lobby.hangar.carousels.battle_pass.carousel_filter import BattlePassCarouselFilter
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.game_loading.resources.consts import Milestones
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.common.router_model import RouterModel
from gui.impl.lobby.hangar.base.account_styles import AccountStyles
from gui.impl.lobby.hangar.base.vehicles_filter_component import VehiclesFilterComponent
from gui.impl.lobby.hangar.presenters.crew_presenter import CrewPresenter
from gui.impl.lobby.hangar.presenters.hangar_vehicle_params_presenter import HangarVehicleParamsPresenter
from gui.impl.lobby.hangar.presenters.hero_tank_presenter import HeroTankPresenter
from gui.impl.lobby.hangar.presenters.loadout_presenter import LoadoutPresenter
from gui.impl.lobby.hangar.presenters.lootbox_entry_point_presenter import LootboxEntryPointPresenter
from gui.impl.lobby.hangar.presenters.main_menu_presenter import MainMenuPresenter
from gui.impl.lobby.hangar.presenters.optional_devices_assistant_presenter import OptionalDevicesAssistantPresenter
from gui.impl.lobby.hangar.presenters.space_interaction_presenter import SpaceInteractionPresenter
from gui.impl.lobby.hangar.presenters.teaser_presenter import TeaserPresenter
from gui.impl.lobby.hangar.presenters.user_missions_presenter import UserMissionsPresenter
from gui.impl.lobby.hangar.presenters.utils import getMenuItems
from gui.impl.lobby.hangar.presenters.vehicle_filters_presenter import VehicleFiltersDataProvider
from gui.impl.lobby.hangar.presenters.vehicle_inventory_presenter import VehicleInventoryPresenter
from gui.impl.lobby.hangar.presenters.vehicle_menu_presenter import VehicleMenuPresenter
from gui.impl.lobby.hangar.presenters.vehicle_playlists_presenter import VehiclePlaylistsPresenter
from gui.impl.lobby.hangar.presenters.vehicle_statistics_presenter import VehiclesStatisticsPresenter
from gui.impl.lobby.hangar.presenters.vehicles_info_presenter import VehiclesInfoPresenter
from gui.impl.lobby.hangar.random.sound_manager import RANDOM_HANGAR_SOUND_SPACE
from gui.impl.pub import WindowImpl
from gui.impl.pub.view_component import ViewComponent
from gui.lobby_state_machine.routable_view import IRoutableView
from gui.lobby_state_machine.router import SubstateRouter
from gui.shared import EVENT_BUS_SCOPE, events
from gui.shared import g_eventBus
from gui.shared.event_dispatcher import showLobbyMenu
from gui.shared.utils.requesters import REQ_CRITERIA
from hangar_selectable_objects import HangarSelectableLogic
from helpers import dependency
from helpers.statistics import HANGAR_LOADING_STATE
from shared_utils import nextTick
from skeletons.gui.customization import ICustomizationService
from skeletons.helpers.statistics import IStatisticsCollector
from skeletons.gui.offers import IOffersBannerController
if typing.TYPE_CHECKING:
    from gui.shared.utils.requesters import RequestCriteria
    from gui.impl.pub.view_impl import TViewModel
    from hangar_selectable_objects.interfaces import ISelectableLogic
_logger = logging.getLogger(__name__)

def _createRandomModeCriteria():
    randomCriteria = REQ_CRITERIA.EMPTY
    randomCriteria |= ~REQ_CRITERIA.VEHICLE.MODE_HIDDEN
    randomCriteria |= ~REQ_CRITERIA.VEHICLE.BATTLE_ROYALE
    randomCriteria |= ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE
    randomCriteria |= REQ_CRITERIA.VEHICLE.ACTIVE_IN_NATION_GROUP
    return randomCriteria


class HangarSpaceSelectable(object):
    VEHICLE_PREVIEW_FLAG = 'vehiclePreviewFlag'
    HERO_TANK_PREVIEW_FLAG = 'heroTankPreviewFlag'
    HANGAR_FLAG = 'hangarFlag'


class HangarWindow(WindowImpl):
    _statsCollector = dependency.descriptor(IStatisticsCollector)

    def __init__(self, layer, **kwargs):
        super(HangarWindow, self).__init__(content=RandomHangar(), wndFlags=WindowFlags.WINDOW, layer=layer)

    def _onReady(self):
        super(HangarWindow, self)._onReady()
        self._statsCollector.noteHangarLoadingState(HANGAR_LOADING_STATE.HANGAR_UI_READY)
        g_playerEvents.onLoadingMilestoneReached(Milestones.HANGAR_UI_READY)


class RandomHangar(ViewComponent[RouterModel], IRoutableView):
    _COMMON_SOUND_SPACE = RANDOM_HANGAR_SOUND_SPACE
    __customizationService = dependency.descriptor(ICustomizationService)
    __offersBannerController = dependency.descriptor(IOffersBannerController)

    def __init__(self, layoutId=R.views.mono.hangar.main(), model=RouterModel):
        super(RandomHangar, self).__init__(layoutId, model)
        self.__inputManager = None
        self.__baseCriteria = _createRandomModeCriteria()
        self.__accountVehiclesCriteria = self.__baseCriteria | REQ_CRITERIA.INVENTORY
        self.__allModeVehicleFilter = VehiclesFilterComponent(self.__baseCriteria)
        self.__accountVehicleFilter = VehiclesFilterComponent(self.__accountVehiclesCriteria)
        self.__carouselFilter = BattlePassCarouselFilter()
        self.__carouselFilter.setDisabledUpdateCriteries(True)
        self.__accountStyles = AccountStyles()
        self._router = None
        return

    def getRouterModel(self):
        return self.getViewModel()

    def _getChildComponents(self):
        hangar = R.aliases.hangar.shared
        return {hangar.VehiclesInfo(): lambda : VehiclesInfoPresenter(self.__allModeVehicleFilter),
         hangar.VehiclesStatistics(): lambda : VehiclesStatisticsPresenter(self.__accountVehicleFilter, self.__accountStyles),
         hangar.Loadout(): LoadoutPresenter,
         hangar.Crew(): CrewPresenter,
         hangar.VehicleParams(): HangarVehicleParamsPresenter,
         hangar.VehiclesInventory(): lambda : VehicleInventoryPresenter(self.__accountVehiclesCriteria),
         hangar.VehicleFilters(): lambda : VehicleFiltersDataProvider(self.__carouselFilter),
         hangar.MainMenu(): lambda : MainMenuPresenter(getMenuItems()),
         hangar.SpaceInteraction(): lambda : SpaceInteractionPresenter(self.__createSelectableLogic()),
         hangar.VehicleMenu(): VehicleMenuPresenter,
         hangar.LootboxEntryPoint(): LootboxEntryPointPresenter,
         hangar.Teaser(): TeaserPresenter,
         hangar.HeroTank(): HeroTankPresenter,
         hangar.OptionalDevicesAssistant(): OptionalDevicesAssistantPresenter,
         hangar.VehiclePlaylists(): VehiclePlaylistsPresenter,
         hangar.UserMissions(): UserMissionsPresenter}

    def _subscribe(self):
        super(RandomHangar, self)._subscribe()
        self.__inputManager.addEscapeListener(self.__escapeHandler)

    def _unsubscribe(self):
        self.__inputManager.removeEscapeListener(self.__escapeHandler)
        super(RandomHangar, self)._unsubscribe()

    def _initializeRouter(self):
        lsm = getLobbyStateMachine()
        self._router = SubstateRouter(lsm, self, lsm.getStateFromView(self))
        self._router.init()

    def _onLoading(self, *args, **kwargs):
        self.__inputManager = self.__app.gameInputManager
        self.__allModeVehicleFilter.initialize()
        self.__accountVehicleFilter.initialize()
        self._initializeRouter()
        self.__accountStyles.initialize()
        super(RandomHangar, self)._onLoading(*args, **kwargs)

    def _onShown(self):
        super(RandomHangar, self)._onShown()
        nextTick(ClientSelectableCameraObject.switchCamera)()
        g_eventBus.handleEvent(events.HangarCustomizationEvent(events.HangarCustomizationEvent.RESET_VEHICLE_MODEL_TRANSFORM), scope=EVENT_BUS_SCOPE.LOBBY)
        g_currentPreviewVehicle.selectNoVehicle()
        if g_currentVehicle.isPresent():
            g_currentVehicle.refreshModel()
        self.__offersBannerController.showBanners()

    def _onHidden(self):
        self.__offersBannerController.hideBanners()
        super(RandomHangar, self)._onHidden()

    def _finalize(self):
        super(RandomHangar, self)._finalize()
        self.__allModeVehicleFilter.destroy()
        self.__allModeVehicleFilter = None
        self.__accountVehicleFilter.destroy()
        self.__accountVehicleFilter = None
        self.__carouselFilter = None
        self.__baseCriteria = None
        self._router.fini()
        self._router = None
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
