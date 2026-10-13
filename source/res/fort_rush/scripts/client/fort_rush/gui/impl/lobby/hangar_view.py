# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/lobby/hangar_view.py
from __future__ import absolute_import
import typing
from account_helpers.AccountSettings import HANGAR_VIEW_SETTINGS, HANGAR_KEY_BINDINGS
from gui.impl.lobby.hangar.presenters.pet_object_tooltip_presenter import PetObjectTooltipPresenter
from helpers.CallbackDelayer import CallbackDelayer
from ClientSelectableCameraObject import ClientSelectableCameraObject
from CurrentVehicle import g_currentPreviewVehicle, g_currentVehicle
from PlayerEvents import g_playerEvents
from fort_rush.account_helpers import account_settings as fort_rush_account_settings
from fort_rush.gui.fort_rush_gui_constants import PREBATTLE_ACTION_NAME
from fort_rush.gui.filters.fort_rush_carousel_filter import FortRushCarouselFilter
from fort_rush_common.fort_rush_constants import FORT_RUSH_VEHICLE_TAG
from fort_rush.gui.impl.lobby.presenters.fort_rush_lobby_vehicle_filters_presenter import FortRushLobbyVehicleFiltersPresenter
from fort_rush.gui.impl.lobby.presenters.fort_rush_lobby_vehicles_info_presenter import FortRushLobbyVehiclesInfoPresenter
from fort_rush.gui.impl.lobby.presenters.loadout_presenter import FortRushLoadoutPresenter
from fort_rush.gui.impl.lobby.user_missions.fort_rush_user_missions_presenter import FortRushUserMissionsPresenter
from frameworks.wulf import WindowFlags
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.app_loader import app_getter
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.common.router_model import RouterModel
from gui.impl.gen.view_models.views.lobby.hangar.hangar_settings_model import HangarSettingsModel
from gui.impl.gen.view_models.views.lobby.hangar.key_bindings_model import KeyBindingsModel
from gui.impl.gen.view_models.views.lobby.tank_setup.common.ammunition_panel_constants import AmmunitionPanelConstants
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.common.presenters.dynamic_economics_presenter import DynamicEconomicsPresenter
from gui.impl.lobby.common.presenters.settings_presenter import SettingsPresenter
from gui.impl.lobby.easy_tank_equip.easy_tank_equip_presenter import EasyTankEquipPresenter
from gui.impl.lobby.hangar.base.account_styles import AccountStyles
from gui.impl.lobby.hangar.base.blur import RandomHangarBlur
from gui.impl.lobby.hangar.base.vehicles_filter_component import VehiclesFilterComponent
from gui.impl.lobby.hangar.presenters.crew_presenter import CrewPresenter
from gui.impl.lobby.hangar.presenters.hangar_vehicle_params_presenter import HangarVehicleParamsPresenter
from gui.impl.lobby.hangar.presenters.hero_tank_presenter import HeroTankPresenter
from gui.impl.lobby.hangar.presenters.main_menu_presenter import MainMenuPresenter
from gui.impl.lobby.hangar.presenters.space_interaction_presenter import SpaceInteractionPresenter
from gui.impl.lobby.hangar.presenters.utils import RANDOM_MENU_ITEMS
from gui.impl.lobby.hangar.presenters.vehicle_inventory_presenter import VehicleInventoryPresenter
from gui.impl.lobby.hangar.presenters.vehicle_menu_presenter import VehicleMenuPresenter
from gui.impl.lobby.hangar.presenters.vehicle_playlists_presenter import VehiclePlaylistsPresenter
from gui.impl.lobby.hangar.presenters.vehicle_statistics_presenter import VehiclesStatisticsPresenter
from gui.impl.lobby.common.presenters.manage_vehicle_playlists_presenter import ManageableVehiclePlaylistsPresenter
from gui.impl.pub import WindowImpl
from gui.impl.pub.view_component import ViewComponent
from gui.lobby_state_machine.routable_view import IRoutableView
from gui.lobby_state_machine.router import SubstateRouter
from gui.prb_control import prb_getters
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from gui.shared.event_dispatcher import showLobbyMenu
from gui.shared.utils import SelectorBattleTypesUtils
from gui.shared.utils.requesters import REQ_CRITERIA
from hangar_selectable_objects import HangarSelectableLogic
from shared_utils import nextTick
if typing.TYPE_CHECKING:
    from gui.impl.pub.view_impl import TViewModel

def _showLoadout():
    from fort_rush.gui.impl.lobby.states import FortRushLoadoutState
    FortRushLoadoutState.goTo(groupId=AmmunitionPanelConstants.OPTIONAL_DEVICES_AND_BOOSTERS, sectionName=TankSetupConstants.OPT_DEVICES, slotIndex=0)


def _restoreLastSelectedVehicle():
    intCD = fort_rush_account_settings.getLastSelectedVehicleIntCD()
    if intCD and (not g_currentVehicle.isPresent() or g_currentVehicle.intCD != intCD):
        g_currentVehicle.selectVehicleByCD(intCD)


def _onCurrentVehicleChanged():
    if g_currentVehicle.isPresent():
        fort_rush_account_settings.setLastSelectedVehicleIntCD(g_currentVehicle.intCD)


class FortRushHangarWindow(WindowImpl):

    def __init__(self, layer, **kwargs):
        super(FortRushHangarWindow, self).__init__(content=FortRushHangarView(), wndFlags=WindowFlags.WINDOW, layer=layer)


EXT_MODE_CRITERIA = ~REQ_CRITERIA.VEHICLE.MODE_HIDDEN | ~REQ_CRITERIA.VEHICLE.BATTLE_ROYALE | ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE ^ REQ_CRITERIA.VEHICLE.HAS_TAGS({FORT_RUSH_VEHICLE_TAG}) | REQ_CRITERIA.VEHICLE.ACTIVE_IN_NATION_GROUP

class FortRushHangarView(ViewComponent[RouterModel], IRoutableView):
    LAYOUT_ID = R.views.fort_rush.mono.lobby.hangar()

    def __init__(self, layoutId=LAYOUT_ID, model=RouterModel):
        super(FortRushHangarView, self).__init__(layoutId, model)
        self.__inputManager = None
        self.__isUnitJoiningInProgress = False
        self.__timer = None
        self.__router = None
        self.__allModeVehicleFilter = VehiclesFilterComponent(EXT_MODE_CRITERIA)
        self.__accountVehicleFilter = VehiclesFilterComponent(REQ_CRITERIA.INVENTORY | EXT_MODE_CRITERIA)
        self.__carouselFilter = FortRushCarouselFilter()
        self.__carouselFilter.setDisabledUpdateCriteries(True)
        self.__accountStyles = AccountStyles()
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
        fortRush = R.aliases.fort_rush.shared
        return {common.DynamicEconomics(): DynamicEconomicsPresenter,
         hangar.Loadout(): FortRushLoadoutPresenter,
         hangar.Crew(): CrewPresenter,
         hangar.MainMenu(): lambda : MainMenuPresenter(RANDOM_MENU_ITEMS),
         hangar.VehiclesInfo(): lambda : FortRushLobbyVehiclesInfoPresenter(self.__allModeVehicleFilter),
         hangar.VehiclesInventory(): lambda : VehicleInventoryPresenter(self.__accountVehicleFilter),
         hangar.VehiclesStatistics(): lambda : VehiclesStatisticsPresenter(self.__accountVehicleFilter, self.__accountStyles),
         hangar.VehicleFilters(): lambda : FortRushLobbyVehicleFiltersPresenter(self.__carouselFilter),
         hangar.VehicleParams(): HangarVehicleParamsPresenter,
         hangar.SpaceInteraction(): lambda : SpaceInteractionPresenter(self.__createSelectableLogic()),
         hangar.VehicleMenu(): VehicleMenuPresenter,
         hangar.HeroTank(): HeroTankPresenter,
         hangar.PetObjectTooltip(): PetObjectTooltipPresenter,
         hangar.Settings(): lambda : SettingsPresenter(HangarSettingsModel, HANGAR_VIEW_SETTINGS),
         hangar.KeyBindings(): lambda : SettingsPresenter(KeyBindingsModel, HANGAR_KEY_BINDINGS, readOnly=True),
         hangar.ManageableVehiclePlaylists(): ManageableVehiclePlaylistsPresenter,
         hangar.VehiclePlaylists(): VehiclePlaylistsPresenter,
         fortRush.UserMissions(): FortRushUserMissionsPresenter,
         hangar.EasyTankEquip(): EasyTankEquipPresenter}

    def _initializeRouter(self):
        lsm = getLobbyStateMachine()
        self._router = SubstateRouter(lsm, self, lsm.getStateFromView(self))
        self._router.init()

    def _onLoading(self, *args, **kwargs):
        self.__inputManager = self.__app.gameInputManager
        self.__timer = CallbackDelayer()
        self.__allModeVehicleFilter.initialize()
        self.__accountVehicleFilter.initialize()
        self.__accountStyles.initialize()
        self._initializeRouter()
        self.__blur.init()
        super(FortRushHangarView, self)._onLoading(*args, **kwargs)

    def _onLoaded(self, *args, **kwargs):
        super(FortRushHangarView, self)._onLoaded(*args, **kwargs)
        if not SelectorBattleTypesUtils.isKnownBattleType(PREBATTLE_ACTION_NAME.FORT_RUSH):
            SelectorBattleTypesUtils.setBattleTypeAsKnown(PREBATTLE_ACTION_NAME.FORT_RUSH)
        g_eventBus.handleEvent(events.ViewReadyEvent(self.layoutID))

    def _onShown(self):
        super(FortRushHangarView, self)._onShown()
        _restoreLastSelectedVehicle()
        nextTick(ClientSelectableCameraObject.switchCamera)()
        g_eventBus.handleEvent(events.HangarCustomizationEvent(events.HangarCustomizationEvent.RESET_VEHICLE_MODEL_TRANSFORM), scope=EVENT_BUS_SCOPE.LOBBY)
        g_currentPreviewVehicle.selectNoVehicle()
        if g_currentVehicle.isPresent():
            g_currentVehicle.refreshModel()

    def _subscribe(self):
        super(FortRushHangarView, self)._subscribe()
        self.__inputManager.addEscapeListener(self.__escapeHandler)
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitJoined += self.__onUnitJoined
        g_playerEvents.onPrebattleInvitationAccepted += self.__onPrebattleInvitationAccepted
        g_currentVehicle.onChanged += _onCurrentVehicleChanged

    def _unsubscribe(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitJoined -= self.__onUnitJoined
        if self.__timer is not None:
            self.__timer.clearCallbacks()
            self.__timer = None
        g_playerEvents.onPrebattleInvitationAccepted -= self.__onPrebattleInvitationAccepted
        g_currentVehicle.onChanged -= _onCurrentVehicleChanged
        self.__inputManager.removeEscapeListener(self.__escapeHandler)
        super(FortRushHangarView, self)._unsubscribe()
        return

    def _finalize(self):
        super(FortRushHangarView, self)._finalize()
        self.__inputManager = None
        self.__timer = None
        self.__accountVehicleFilter.destroy()
        self.__accountVehicleFilter = None
        self._router.fini()
        self._router = None
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

    def __createSelectableLogic(self):
        return HangarSelectableLogic()

    def __onPrebattleInvitationAccepted(self, *args):
        self.__isUnitJoiningInProgress = True
        self.__timer.delayCallback(15, self.__onResetUnitJoiningProgress)

    def __onResetUnitJoiningProgress(self):
        self.__isUnitJoiningInProgress = False

    def __onUnitJoined(self, *args):
        self.__isUnitJoiningInProgress = False
        if self.__timer is not None:
            self.__timer.stopCallback(self.__onResetUnitJoiningProgress)
        return
