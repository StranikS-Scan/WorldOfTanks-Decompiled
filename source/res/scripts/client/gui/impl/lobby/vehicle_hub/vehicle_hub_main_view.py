# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_hub/vehicle_hub_main_view.py
from __future__ import absolute_import
import typing
from collections import namedtuple, OrderedDict
from future.utils import itervalues
from CurrentVehicle import g_currentPreviewVehicle
from PlayerEvents import g_playerEvents
from account_helpers import AccountSettings
from account_helpers.AccountSettings import VIEWED_MODULES_SECTION
from armor_inspector_common.schemas import armorInspectorConfigSchema
from frameworks.wulf import WindowFlags
from frameworks.state_machine import StateIdsObserver
from Event import Event
from collector_vehicle import CollectorVehicleConsts
from gui import g_tankActiveCamouflage
from gui.shared.events import VehicleBuyEvent
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.comparison_model import ComparisonModel
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.menu_item_model import MenuItemModel
from gui.impl.lobby.vehicle_hub.sub_presenters.research_purchase_sub_presenter import ResearchPurchaseSubPresenter
from gui.impl.lobby.vehicle_hub.vehicle_hub_characteristics_presenter import VehicleHubCharacteristicsPresenter
from gui.impl.lobby.vehicle_hub.vehicle_hub_wallet_presenter import VehicleHubWalletPresenter
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.vehicle_hub_view_model import VehicleHubViewModel
from gui.impl.pub import WindowImpl
from gui.impl.gen import R
from gui.impl.pub.view_component import ViewComponent
from gui.lobby_state_machine.router import SubstateRouter
from gui.lobby_state_machine.routable_view import IRoutableView
from gui.impl.lobby.vehicle_hub.sub_presenters.presenters_map import PresentersMap, SubModelInfo
from gui.shared.utils.module_upd_available_helper import getVehicleResearchInfo
from helpers import dependency
from renewable_subscription_common.settings_constants import RS_PDATA_KEY
from skeletons.gui.game_control import IVehicleComparisonBasket, IRentalsController
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Dict
_REQUIRED_TAGS = [VEHICLE_TAGS.SPECIAL,
 VEHICLE_TAGS.PREMIUM,
 VEHICLE_TAGS.EARN_CRYSTALS,
 CollectorVehicleConsts.COLLECTOR_VEHICLES_TAG]
VehicleHubCtx = namedtuple('VehicleHubCtx', ('intCD',
 'vehicleStrCD',
 'style',
 'outfit'))

class _VehicleHubStatesObserver(StateIdsObserver):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, vhCtx):
        self.__vhCtx = vhCtx
        from gui.impl.lobby.vehicle_hub.states import OverviewState
        from gui.impl.lobby.vehicle_hub.states import ArmorState
        from gui.impl.lobby.vehicle_hub.states import StatsState
        from gui.impl.lobby.vehicle_hub.states import ModulesState
        from gui.impl.lobby.vehicle_hub.states import VehSkillTreeState
        from gui.impl.lobby.vehicle_hub.states import VehSkillTreeInitialState
        from gui.impl.lobby.vehicle_hub.states import VehSkillTreeProgressionState
        from gui.impl.lobby.vehicle_hub.states import VehSkillTreePrestigeState
        super(_VehicleHubStatesObserver, self).__init__([OverviewState.STATE_ID,
         ArmorState.STATE_ID,
         StatsState.STATE_ID,
         ModulesState.STATE_ID,
         VehSkillTreeState.STATE_ID,
         VehSkillTreeInitialState.STATE_ID,
         VehSkillTreeProgressionState.STATE_ID,
         VehSkillTreePrestigeState.STATE_ID])
        self.__setupPreviewTank(self.__vhCtx)
        self.onNavigationChanged = Event()

    def onEnterState(self, state, event):
        vhCtx = event.params.get('vhCtx')
        if vhCtx and self.__vhCtx != vhCtx:
            self.__vhCtx = vhCtx
            self.__setupPreviewTank(self.__vhCtx)
        if hasattr(state, 'TAB_NAME'):
            self.onNavigationChanged(state.TAB_NAME, event)

    def __setupPreviewTank(self, vhCtx):
        vehicle = self.__itemsCache.items.getItemByCD(int(vhCtx.intCD))
        if vehicle.isInInventory:
            season = g_tankActiveCamouflage.get(vehicle.intCD, vehicle.getAnyOutfitSeason())
            g_currentPreviewVehicle.selectVehicle(vehicle.intCD, vehicleStrCD=vehicle.strCD, outfit=vehicle.getOutfit(season))
        else:
            g_currentPreviewVehicle.selectNoVehicle()
            g_currentPreviewVehicle.selectVehicle(vhCtx.intCD, vehicleStrCD=vhCtx.vehicleStrCD, style=vhCtx.style, outfit=vhCtx.outfit)


class VehicleHubMainView(ViewComponent, IRoutableView):
    __comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)
    __itemsCache = dependency.descriptor(IItemsCache)
    __rentals = dependency.descriptor(IRentalsController)

    def __init__(self, ctx, *args, **kwargs):
        self.__contentPresentersMap = {}
        self.__activeTab = None
        self.__vhCtx = ctx
        self.__lsmObserver = _VehicleHubStatesObserver(ctx)
        self.__researchPurchase = None
        self.__router = None
        super(VehicleHubMainView, self).__init__(R.views.mono.vehicle_hub.main(), VehicleHubViewModel)
        return

    @property
    def viewModel(self):
        return super(VehicleHubMainView, self).getViewModel()

    @property
    def currentPresenter(self):
        return self.__contentPresentersMap[self.__activeTab].presenter if self.__activeTab else None

    @property
    def vehicleCtx(self):
        return self.__vhCtx

    def getRouterModel(self):
        return self.getViewModel().router

    def createToolTipContent(self, event, contentID):
        return self.currentPresenter.createToolTipContent(event, contentID)

    def createToolTip(self, event):
        return self.currentPresenter.createToolTip(event) or super(VehicleHubMainView, self).createToolTip(event)

    def stateExited(self):
        self.__router.fini()
        self.__router = None
        return

    def _onLoading(self, *args, **kwargs):
        super(VehicleHubMainView, self)._onLoading(*args, **kwargs)
        self.__registerSubModels()
        self.__researchPurchase = ResearchPurchaseSubPresenter(self.viewModel.researchPurchaseModel, self)
        self.__researchPurchase.initialize(self.__vhCtx)
        lsm = getLobbyStateMachine()
        self.__router = SubstateRouter(lsm, self, lsm.getStateFromView(self))
        self.__router.init()
        lsm.connect(self.__lsmObserver)
        with self.viewModel.transaction():
            self.__setCommonInfo()
            self.__updateComparisonInfo()
            self.__updateMenuItems()

    def _initChildren(self):
        vehicleHub = R.aliases.vehicle_hub.default
        self._registerChild(vehicleHub.VehicleParams(), VehicleHubCharacteristicsPresenter(self.__vhCtx.intCD))
        self._registerChild(vehicleHub.Wallet(), VehicleHubWalletPresenter())

    def _getEvents(self):
        eventsTuple = super(VehicleHubMainView, self)._getEvents()
        return eventsTuple + ((self.__lsmObserver.onNavigationChanged, self.__onNavigationChanged),
         (self.__rentals.onRentChangeNotify, self.__onRentChange),
         (self.viewModel.onMoveSpace, self.__onMoveSpace),
         (self.viewModel.onMouseOver3dScene, self.__onMouseOver3dScene),
         (self.viewModel.comparisonModel.onAddToComparison, self.__onAddToComparison),
         (self.__comparisonBasket.onChange, self.__onVehCompareBasketChanged),
         (self.__comparisonBasket.onSwitchChange, self.__updateComparisonInfo),
         (g_playerEvents.onClientUpdated, self.__onClientUpdate),
         (AccountSettings.onSettingsChanging, self.__onAccountSettingsChanging))

    def _getCallbacks(self):
        callbacksTuple = super(VehicleHubMainView, self)._getCallbacks()
        return callbacksTuple + (('inventory', self.__onInventoryUpdate), ('cache.vehsLock', self.__onVehsLockUpdate), ('stats.eliteVehicles', self.__onVehicleBecomeElite))

    def _getListeners(self):
        return ((VehicleBuyEvent.VEHICLE_SELECTED, self.__onTradeOffSelectedChanged, EVENT_BUS_SCOPE.DEFAULT),)

    def _finalize(self):
        super(VehicleHubMainView, self)._finalize()
        lsm = getLobbyStateMachine()
        lsm.disconnect(self.__lsmObserver)
        if self.__router is not None:
            self.__router.fini()
            self.__router = None
        if self.currentPresenter is not None:
            self.currentPresenter.finalize()
        self.__lsmObserver = None
        self.__clearAllSubPresenters()
        self.__activeTab = None
        self.__vhCtx = None
        self.__researchPurchase.finalize()
        self.__researchPurchase.clear()
        self.__researchPurchase = None
        return

    @property
    def __vehicle(self):
        return self.__itemsCache.items.getItemByCD(self.__vhCtx.intCD)

    def __getUnviewedResearchedModulesCount(self):
        researchInfo = getVehicleResearchInfo(self.__vehicle.intCD, self.__vehicle)
        if researchInfo is None:
            return 0
        else:
            unviewedResearchedModules = researchInfo.getUnviewedItems()
            return len(unviewedResearchedModules)

    def __getVehSkillTreeVisibility(self):
        return self.__vehicle.postProgression.isVehSkillTree()

    def __getMenuItems(self):
        return OrderedDict([(VehicleHubViewModel.OVERVIEW, (None, None)),
         (VehicleHubViewModel.STATS, (None, None)),
         (VehicleHubViewModel.MODULES, (self.__getUnviewedResearchedModulesCount, None)),
         (VehicleHubViewModel.VEH_SKILL_TREE, (None, self.__getVehSkillTreeVisibility)),
         (VehicleHubViewModel.ARMOR, (None, None))])

    @replaceNoneKwargsModel
    def __setCommonInfo(self, model=None):
        fillVehicleInfo(model.vehicleInfoModel, self.__vehicle, tags=_REQUIRED_TAGS)

    @replaceNoneKwargsModel
    def __updateComparisonInfo(self, model=None):
        comparisonModel = model.comparisonModel
        status = None
        if not self.__comparisonBasket.isEnabled():
            status = ComparisonModel.DISABLED_ON_SERVER
        elif self.__comparisonBasket.isFull():
            status = ComparisonModel.DISABLED_FULL_BASKET
        if not status:
            if self.__comparisonBasket.isReadyToAdd(self.__vehicle):
                status = ComparisonModel.ENABLED
            else:
                status = ComparisonModel.CAN_NOT_COMPARE
        comparisonModel.setStatus(status)
        return

    def __onClientUpdate(self, diff, _):
        if RS_PDATA_KEY in diff:
            self.__setCommonInfo()

    def __onTradeOffSelectedChanged(self, _=None):
        self.__setCommonInfo()

    def __onVehicleBecomeElite(self, elite):
        if self.vehicleCtx.intCD in elite:
            self.__setCommonInfo()

    def __onAccountSettingsChanging(self, key, _):
        if key == VIEWED_MODULES_SECTION:
            self.__updateMenuItems()

    @replaceNoneKwargsModel
    def __updateMenuItems(self, model=None):
        menuItems = self.__getMenuItems()
        disabledTabs = self.__disabledTabs
        menuItemsModel = model.getMenuItems()
        menuItemsModel.clear()
        for tab, handlers in menuItems.items():
            counterHandler, visibilityHandler = handlers
            if visibilityHandler and not visibilityHandler():
                continue
            if tab not in disabledTabs:
                menuItemModel = MenuItemModel()
                counter = counterHandler() if counterHandler else 0
                menuItemModel.setTabName(tab)
                menuItemModel.setCounter(counter)
                menuItemsModel.addViewModel(menuItemModel)

        menuItemsModel.invalidate()

    def __onAddToComparison(self):
        if self.__comparisonBasket.isReadyToAdd(self.__vehicle):
            self.__comparisonBasket.addVehicle(self.__vhCtx.intCD)

    def __onVehCompareBasketChanged(self, _):
        self.__updateComparisonInfo()

    def __onNavigationChanged(self, state, event):
        self.__switchSubView(state, event.params.get('vhCtx'))

    def __onInventoryUpdate(self, invDiff):
        if GUI_ITEM_TYPE.VEHICLE in invDiff:
            self.__updateMenuItems()

    def __onVehsLockUpdate(self, _=None):
        self.__setCommonInfo()

    def __onRentChange(self, vehicles):
        if self.__vhCtx.intCD in vehicles:
            self.__setCommonInfo()

    def __onVehicleHubCtxChanged(self, vhCtx):
        self.__vhCtx = vhCtx
        if self.currentPresenter:
            self.currentPresenter.setVehicleHubCtx(vhCtx)
        self.__setCommonInfo()
        self.__updateComparisonInfo()
        self.__updateMenuItems()
        if self.__researchPurchase:
            self.__researchPurchase.setVehicleHubCtx(vhCtx)
        uid = self._childrenUidByPosition.get(R.aliases.vehicle_hub.default.VehicleParams())
        vehicleParams = self._childrenByUid.get(uid, None)
        if isinstance(vehicleParams, VehicleHubCharacteristicsPresenter):
            vehicleParams.setVehicle(self.__vhCtx.intCD)
        return

    def __switchSubView(self, tabName, vhCtx=None):
        if self.__activeTab != tabName:
            subModelInfo = self.__contentPresentersMap[tabName]
            if self.currentPresenter and self.currentPresenter.isLoaded:
                self.currentPresenter.finalize()
            self.__activeTab = tabName
            subModelInfo.presenter.initialize(self.__vhCtx)
        if vhCtx and self.__vhCtx != vhCtx:
            self.__onVehicleHubCtxChanged(vhCtx)

    def __registerSubModels(self):
        self.__contentPresentersMap = PresentersMap(self)

    def __clearAllSubPresenters(self):
        self.currentPresenter.finalize()
        for subModelInfo in itervalues(self.__contentPresentersMap):
            subModelInfo.presenter.clear()

        self.__contentPresentersMap.clear()
        self.__contentPresentersMap = None
        return

    @staticmethod
    def __onMoveSpace(args=None):
        if args is None:
            return
        else:
            dx = args.get('dx')
            dy = args.get('dy')
            dz = args.get('dz')
            g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, ctx={'dx': dx,
             'dy': dy,
             'dz': dz}), EVENT_BUS_SCOPE.GLOBAL)
            return

    @staticmethod
    def __onMouseOver3dScene(args):
        g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, ctx={'isOver3dScene': bool(args.get('isOver3dScene'))}))

    @property
    def __disabledTabs(self):
        tabs = set()
        vehicle = self.__itemsCache.items.getItemByCD(int(self.__vhCtx.intCD))
        if vehicle is not None:
            configModel = armorInspectorConfigSchema.getModel()
            vehicleName = vehicle.name
            if not configModel.enabled or configModel.isDisabledForVehicle(vehicleName):
                tabs.add(VehicleHubViewModel.ARMOR)
        return tabs


class VehicleHubWindow(WindowImpl):

    def __init__(self, layer, ctx, **kwargs):
        super(VehicleHubWindow, self).__init__(content=VehicleHubMainView(ctx=ctx), wndFlags=WindowFlags.WINDOW, layer=layer)
