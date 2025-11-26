# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/views/battle_royale_hangar_view.py
from __future__ import absolute_import
import typing
import logging
from ClientSelectableCameraObject import ClientSelectableCameraObject
from CurrentVehicle import g_currentPreviewVehicle, g_currentVehicle
from battle_royale.gui.Scaleform.daapi.view.lobby.hangar.carousel.filter import RoyaleCarouselFilter
from battle_royale.gui.impl.lobby.views.user_missions.hangar_widget.presenters.user_missions_presenter import BattleRoyaleUserMissionsPresenter
from battle_royale.gui.impl.lobby.views.presenters.vehicle_filters_presenter import BattleRoyaleVehicleFiltersPresenter
from battle_royale.gui.impl.lobby.views.presenters.vehicles_inventory_presenter import BattleRoyaleVehiclesInventoryPresenter
from battle_royale.gui.impl.lobby.views.presenters.battle_type_selector_presenter import BattleTypeSelectorPresenter
from battle_royale.gui.impl.lobby.views.presenters.alert_message_presenter import AlertMessagePresenter
from battle_royale.gui.impl.lobby.views.presenters.header_presenter import HeaderPresenter
from battle_royale.gui.impl.lobby.views.presenters.loadout_panel_presenter.loadout_panel_presenter import LoadoutContainerPresenter
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.app_loader import app_getter
from frameworks.wulf import WindowFlags
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.impl.pub import WindowImpl
from gui.lobby_state_machine.router import SubstateRouter
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showLobbyMenu
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.common.router_model import RouterModel
from gui.impl.lobby.hangar.base.account_styles import AccountStyles
from gui.impl.lobby.hangar.base.vehicles_filter_component import VehiclesFilterComponent
from gui.impl.lobby.hangar.presenters.main_menu_presenter import MainMenuPresenter
from gui.impl.lobby.hangar.presenters.hero_tank_presenter import HeroTankPresenter
from gui.impl.lobby.hangar.presenters.space_interaction_presenter import SpaceInteractionPresenter
from gui.impl.lobby.hangar.presenters.utils import getMenuItems
from gui.impl.pub.view_component import ViewComponent
from gui.lobby_state_machine.routable_view import IRoutableView
from gui.shared.utils.requesters import REQ_CRITERIA
from hangar_selectable_objects import HangarSelectableLogic
from gui.impl.lobby.hangar.presenters.lootbox_entry_point_presenter import LootboxEntryPointPresenter
from helpers import dependency
from shared_utils import nextTick
from skeletons.gui.game_control import IBattleRoyaleController
if typing.TYPE_CHECKING:
    from gui.impl.pub.view_impl import TViewModel
    from gui.shared.utils.requesters import RequestCriteria
    from hangar_selectable_objects.interfaces import ISelectableLogic
_logger = logging.getLogger(__name__)

class BattleRoyaleHangarWindow(WindowImpl):
    __battleRoyale = dependency.descriptor(IBattleRoyaleController)
    __BACKGROUND_ALPHA = 0.0

    def __init__(self, layer, **kwargs):
        self.__background_alpha__ = self.__BACKGROUND_ALPHA
        super(BattleRoyaleHangarWindow, self).__init__(content=BattleRoyaleHangarView(R.views.battle_royale.mono.lobby.hangar()), wndFlags=WindowFlags.WINDOW, layer=layer)

    def _onReady(self):
        super(BattleRoyaleHangarWindow, self)._onReady()
        self.__battleRoyale.showIntroVideo(VIEW_ALIAS.BROWSER_OVERLAY)


class BattleRoyaleHangarView(ViewComponent[RouterModel], IRoutableView):

    def __init__(self, layoutId, model=RouterModel):
        super(BattleRoyaleHangarView, self).__init__(layoutId, model)
        self.__routerObserver = None
        self.__inputManager = None
        self.__vehicleFilter = VehiclesFilterComponent(self.__battleRoyalVehicleCriteria())
        self.__carouselFilter = RoyaleCarouselFilter()
        self.__carouselFilter.setDisabledUpdateCriteries(True)
        self.__accountStyles = AccountStyles()
        return

    def getRouterModel(self):
        return self.getViewModel()

    def _getChildComponents(self):
        hangar = R.aliases.hangar.shared
        battleRoyale = R.aliases.battle_royale
        return {hangar.MainMenu(): lambda : MainMenuPresenter(getMenuItems()),
         hangar.HeroTank(): HeroTankPresenter,
         hangar.SpaceInteraction(): lambda : SpaceInteractionPresenter(self.__createSelectableLogic()),
         hangar.LootboxEntryPoint(): LootboxEntryPointPresenter,
         battleRoyale.LoadoutPanelContainer(): LoadoutContainerPresenter,
         battleRoyale.VehiclesInventory(): lambda : BattleRoyaleVehiclesInventoryPresenter(self.__vehicleFilter, self.__battleRoyalVehicleCriteria()),
         battleRoyale.VehiclesFilter(): BattleRoyaleVehicleFiltersPresenter,
         battleRoyale.BattleSelector(): BattleTypeSelectorPresenter,
         battleRoyale.AlertMessage(): AlertMessagePresenter,
         battleRoyale.Header(): HeaderPresenter,
         battleRoyale.UserMissions(): BattleRoyaleUserMissionsPresenter}

    def _subscribe(self):
        super(BattleRoyaleHangarView, self)._subscribe()
        self.__inputManager.addEscapeListener(self.__escapeHandler)

    def _unsubscribe(self):
        self.__inputManager.removeEscapeListener(self.__escapeHandler)
        super(BattleRoyaleHangarView, self)._unsubscribe()

    def _onLoading(self, *args, **kwargs):
        self.__inputManager = self.__app.gameInputManager
        self.__vehicleFilter.initialize()
        self.__accountStyles.initialize()
        super(BattleRoyaleHangarView, self)._onLoading(*args, **kwargs)

    def _initialize(self, *args, **kwargs):
        super(BattleRoyaleHangarView, self)._initialize(*args, **kwargs)
        lsm = getLobbyStateMachine()
        state = lsm.getStateFromView(self)
        self.__routerObserver = SubstateRouter(lsm, self, state)
        self.__routerObserver.init()

    def _finalize(self):
        super(BattleRoyaleHangarView, self)._finalize()
        if self.__routerObserver is not None:
            self.__routerObserver.fini()
        self.__routerObserver = None
        self.__inputManager = None
        self.__carouselFilter = None
        self.__vehicleFilter.destroy()
        self.__vehicleFilter = None
        self.__accountStyles.destroy()
        self.__accountStyles = None
        return

    def _onShown(self):
        super(BattleRoyaleHangarView, self)._onShown()
        nextTick(ClientSelectableCameraObject.switchCamera)()
        g_eventBus.handleEvent(events.HangarCustomizationEvent(events.HangarCustomizationEvent.RESET_VEHICLE_MODEL_TRANSFORM), scope=EVENT_BUS_SCOPE.LOBBY)
        g_currentPreviewVehicle.selectNoVehicle()
        if g_currentVehicle.isPresent():
            g_currentVehicle.refreshModel()

    @app_getter
    def __app(self):
        return None

    def __createSelectableLogic(self):
        return HangarSelectableLogic()

    def __escapeHandler(self):
        showLobbyMenu()

    @staticmethod
    def __battleRoyalVehicleCriteria():
        return REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.BATTLE_ROYALE
