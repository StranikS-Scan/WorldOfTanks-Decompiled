# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/hangar_view.py
import typing
from account_helpers.AccountSettings import HANGAR_VIEW_SETTINGS, HANGAR_KEY_BINDINGS
from frontline.gui.impl.lobby.presenters.alert_presenter import AlertPresenter
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.hangar.hangar_settings_model import HangarSettingsModel
from gui.impl.gen.view_models.views.lobby.hangar.key_bindings_model import KeyBindingsModel
from gui.impl.lobby.common.presenters.settings_presenter import SettingsPresenter
from gui.impl.lobby.hangar.base.sound_constants import HangarSoundStates
from gui.impl.lobby.hangar.presenters.vehicle_playlists_presenter import VehiclePlaylistsPresenter
from gui.impl.lobby.hangar.presenters.pet_object_tooltip_presenter import PetObjectTooltipPresenter
from gui.sounds.epic_sound_constants import EPIC_SOUND
from helpers.statistics import HANGAR_LOADING_STATE
from gui.impl.lobby.hangar.base.blur import RandomHangarBlur
from shared_utils import nextTick
from gui.impl.pub import WindowImpl
from helpers import dependency
from skeletons.helpers.statistics import IStatisticsCollector
from PlayerEvents import g_playerEvents
from gui.impl.pub.view_component import ViewComponent
from gui.lobby_state_machine.routable_view import IRoutableView
from gui.game_loading.resources.consts import Milestones
from frameworks.wulf import WindowFlags
from gui.impl.gen.view_models.views.lobby.common.router_model import RouterModel
from gui.shared.event_dispatcher import showLobbyMenu
from gui.app_loader import app_getter
from gui.impl.lobby.hangar.presenters.utils import getMenuItems
from gui.impl.lobby.common.presenters.vehicles_info_presenter import VehiclesInfoPresenter
from gui.impl.lobby.hangar.base.vehicles_filter_component import VehiclesFilterComponent
from frontline.gui.impl.lobby.presenters.frontline_loadout_presenter import FrontlineLoadoutPresenter
from frontline.gui.impl.lobby.presenters.frontline_vehicle_menu_presenter import FrontlineVehicleMenuPresenter
from frontline.gui.impl.lobby.presenters.fl_vehicle_inventory_presenter import FLVehicleInventoryPresenter
from frontline.gui.impl.lobby.presenters.fl_vehicles_statistics_presenter import FLVehiclesStatisticsPresenter
from gui.impl.lobby.hangar.presenters.crew_presenter import CrewPresenter
from gui.impl.lobby.hangar.presenters.hangar_vehicle_params_presenter import HangarVehicleParamsPresenter
from gui.impl.lobby.hangar.presenters.main_menu_presenter import MainMenuPresenter
from gui.impl.lobby.hangar.presenters.space_interaction_presenter import SpaceInteractionPresenter
from ClientSelectableCameraObject import ClientSelectableCameraObject
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from CurrentVehicle import g_currentPreviewVehicle, g_currentVehicle
from gui.impl.lobby.hangar.presenters.teaser_presenter import TeaserPresenter
from gui.impl.lobby.hangar.presenters.hero_tank_presenter import HeroTankPresenter
from gui.impl.lobby.hangar.presenters.optional_devices_assistant_presenter import OptionalDevicesAssistantPresenter
from hangar_selectable_objects import HangarSelectableLogic
from gui.impl.lobby.hangar.presenters.vehicle_filters_presenter import VehicleFiltersDataProvider
from frontline.gui.impl.lobby.tooltips.level_reserves_tooltip import LevelReservesTooltip
from frontline.gui.Scaleform.daapi.view.battle.frontline_battle_carousel import BattleCarouselFilter
from frontline.constants.aliases import FrontlineHangarAliases
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.lobby_state_machine.router import SubstateRouter
from gui.impl.lobby.hangar.base.account_styles import AccountStyles
from gui.shared.utils.requesters import REQ_CRITERIA
from sound_gui_manager import CommonSoundSpaceSettings
if typing.TYPE_CHECKING:
    from gui.impl.pub.view_impl import TViewModel
    from typing import Optional

class FrontlineHangarWindow(WindowImpl):
    _statsCollector = dependency.descriptor(IStatisticsCollector)

    def __init__(self, layer, *_, **__):
        super(FrontlineHangarWindow, self).__init__(content=FrontlineHangar(), wndFlags=WindowFlags.WINDOW, layer=layer)

    def _onReady(self):
        self._statsCollector.noteHangarLoadingState(HANGAR_LOADING_STATE.HANGAR_UI_READY)
        g_playerEvents.onLoadingMilestoneReached(Milestones.HANGAR_UI_READY)
        super(FrontlineHangarWindow, self)._onReady()


def _createFrontlineCriteria():
    frontlineCriteria = REQ_CRITERIA.EMPTY
    frontlineCriteria |= ~REQ_CRITERIA.VEHICLE.MODE_HIDDEN
    frontlineCriteria |= ~REQ_CRITERIA.VEHICLE.BATTLE_ROYALE
    frontlineCriteria |= ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE
    frontlineCriteria |= REQ_CRITERIA.VEHICLE.ACTIVE_IN_NATION_GROUP
    return frontlineCriteria


class FrontlineHangar(ViewComponent[RouterModel], IRoutableView):
    _COMMON_SOUND_SPACE = CommonSoundSpaceSettings(name=EPIC_SOUND.HANGAR, entranceStates={HangarSoundStates.PLACE.value: HangarSoundStates.PLACE_GARAGE.value,
     EPIC_SOUND.GAMEMODE_GROUP: EPIC_SOUND.GAMEMODE_STATE}, exitStates={EPIC_SOUND.GAMEMODE_GROUP: EPIC_SOUND.GAMEMODE_DEFAULT}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')

    def __init__(self, layoutId=R.views.frontline.mono.lobby.hangar(), model=RouterModel):
        super(FrontlineHangar, self).__init__(layoutId, model)
        self.__routerObserver = None
        self.__inputManager = None
        self.__carouselFilter = BattleCarouselFilter()
        self.__carouselFilter.setDisabledUpdateCriteries(True)
        self.__accountStyles = AccountStyles()
        self.__baseCriteria = _createFrontlineCriteria()
        self.__vehicleFilter = VehiclesFilterComponent(self.__baseCriteria)
        self.__invVehicleFilter = VehiclesFilterComponent(self.__baseCriteria | REQ_CRITERIA.INVENTORY)
        self.__blur = RandomHangarBlur()
        return

    @property
    def blur(self):
        return self.__blur

    def createToolTipContent(self, event, contentID):
        return LevelReservesTooltip() if contentID == R.views.frontline.mono.lobby.tooltips.level_reserves_tooltip() else super(FrontlineHangar, self).createToolTipContent(event, contentID)

    def getRouterModel(self):
        return self.getViewModel()

    def _getChildComponents(self):
        from frontline.gui.impl.lobby.presenters.user_missions_presenter import FrontlineUserMissionsPresenter
        hangar = R.aliases.hangar.shared
        frontlineHangar = R.aliases.frontline.shared
        return {hangar.VehiclesInfo(): lambda : VehiclesInfoPresenter(self.__vehicleFilter),
         hangar.VehiclesStatistics(): lambda : FLVehiclesStatisticsPresenter(self.__invVehicleFilter, self.__accountStyles),
         hangar.Loadout(): FrontlineLoadoutPresenter,
         hangar.Crew(): CrewPresenter,
         hangar.VehicleParams(): HangarVehicleParamsPresenter,
         hangar.VehiclesInventory(): lambda : FLVehicleInventoryPresenter(self.__invVehicleFilter),
         hangar.VehicleFilters(): lambda : VehicleFiltersDataProvider(self.__carouselFilter),
         hangar.VehiclePlaylists(): VehiclePlaylistsPresenter,
         hangar.MainMenu(): lambda : MainMenuPresenter(getMenuItems()),
         hangar.VehicleMenu(): FrontlineVehicleMenuPresenter,
         hangar.SpaceInteraction(): lambda : SpaceInteractionPresenter(HangarSelectableLogic()),
         hangar.Teaser(): TeaserPresenter,
         hangar.HeroTank(): HeroTankPresenter,
         hangar.OptionalDevicesAssistant(): OptionalDevicesAssistantPresenter,
         hangar.Settings(): lambda : SettingsPresenter(HangarSettingsModel, HANGAR_VIEW_SETTINGS),
         hangar.KeyBindings(): lambda : SettingsPresenter(KeyBindingsModel, HANGAR_KEY_BINDINGS, readOnly=True),
         hangar.PetObjectTooltip(): PetObjectTooltipPresenter,
         frontlineHangar.UserMissions(): FrontlineUserMissionsPresenter,
         frontlineHangar.AlertMessage(): AlertPresenter}

    def _onLoading(self, *args, **kwargs):
        self.__inputManager = self.__app.gameInputManager
        self.__vehicleFilter.initialize()
        self.__invVehicleFilter.initialize()
        self.__accountStyles.initialize()
        self.__blur.init()
        super(FrontlineHangar, self)._onLoading(*args, **kwargs)

    def _onShown(self):
        super(FrontlineHangar, self)._onShown()
        nextTick(ClientSelectableCameraObject.switchCamera)()
        g_eventBus.handleEvent(events.HangarCustomizationEvent(events.HangarCustomizationEvent.RESET_VEHICLE_MODEL_TRANSFORM), scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.handleEvent(events.PetSystemEvent(events.PetSystemEvent.MEDAL_ANIMATION_SHOW), scope=EVENT_BUS_SCOPE.LOBBY)
        g_currentPreviewVehicle.selectNoVehicle()
        if g_currentVehicle.isPresent():
            g_currentVehicle.refreshModel()

    def _subscribe(self):
        super(FrontlineHangar, self)._subscribe()
        self.__inputManager.addEscapeListener(self.__escapeHandler)

    def _unsubscribe(self):
        self.__inputManager.removeEscapeListener(self.__escapeHandler)
        super(FrontlineHangar, self)._unsubscribe()

    def _initialize(self, *args, **kwargs):
        super(FrontlineHangar, self)._initialize(*args, **kwargs)
        lsm = getLobbyStateMachine()
        state = lsm.getStateByViewKey(ViewKey(alias=FrontlineHangarAliases.FRONTLINE_LOBBY_HANGAR))
        self.__routerObserver = SubstateRouter(lsm, self, state)
        self.__routerObserver.init()

    def _finalize(self):
        super(FrontlineHangar, self)._finalize()
        if self.__routerObserver is not None:
            self.__routerObserver.fini()
        self.__routerObserver = None
        self.__vehicleFilter.destroy()
        self.__vehicleFilter = None
        self.__invVehicleFilter.destroy()
        self.__invVehicleFilter = None
        self.__carouselFilter = None
        self.__baseCriteria = None
        self.__inputManager = None
        self.__accountStyles.destroy()
        self.__accountStyles = None
        self.__blur.destroy()
        self.__blur = None
        return

    @app_getter
    def __app(self):
        return None

    def __escapeHandler(self):
        showLobbyMenu()
