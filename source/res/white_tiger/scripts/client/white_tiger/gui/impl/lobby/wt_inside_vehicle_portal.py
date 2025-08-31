# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/wt_inside_vehicle_portal.py
import logging
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.battle_pass.battle_pass_decorators import createBackportTooltipDecorator
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.Waiting import Waiting
from gui.impl.pub.lobby_window import LobbyWindow
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_event_portal_model import PortalType
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_inside_vehicle_portal_model import WtInsideVehiclePortalModel
from white_tiger.gui.impl.lobby.wt_event_constants import WhiteTigerLootBoxes
from white_tiger.gui.impl.lobby.wt_event_base_portals_view import WtEventBasePortalsView
from white_tiger.gui.impl.lobby.wt_event_sound import changePortalState, playLootBoxPortalExit
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE, event_dispatcher
from gui.wt_event.wt_event_helpers import getPortalCost
from white_tiger.gui.wt_event_models_helper import setLootBoxesCount, hasUnclaimedLoot
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from gui.shared.event_dispatcher import showVehiclePreviewWithoutBottomPanel, showEventStorageWindow
from constants import ROLE_TYPE_TO_LABEL
from gui.impl.lobby.tooltips.vehicle_role_descr_view import VehicleRolesTooltipView
from skeletons.gui.game_control import ILootBoxesController
_logger = logging.getLogger(__name__)
_UNCLAIMED_RUN_DELAY = 1

class WTInsideVehiclePortalView(WtEventBasePortalsView, CallbackDelayer):
    __slots__ = ()
    __lootBoxesCtrl = dependency.descriptor(ILootBoxesController)

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.white_tiger.lobby.InsideVehiclePortalView(), model=WtInsideVehiclePortalModel())
        super(WTInsideVehiclePortalView, self).__init__(settings)
        self.__mainVehiclePrizeCD = self._lootBoxesCtrl.getMainPrizeVehicles()[0]

    @property
    def viewModel(self):
        return super(WTInsideVehiclePortalView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return VehicleRolesTooltipView(self.__mainVehiclePrizeCD) if contentID == R.views.lobby.ranked.tooltips.RankedBattlesRolesTooltipView() else super(WTInsideVehiclePortalView, self).createToolTipContent(event, contentID)

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(WTInsideVehiclePortalView, self).createToolTip(event)

    def _onLoaded(self, *args, **kwargs):
        super(WTInsideVehiclePortalView, self)._onLoaded(*args, **kwargs)
        changePortalState(PortalType.TANK)
        if hasUnclaimedLoot(WhiteTigerLootBoxes.WT_TANK):
            self.delayCallback(_UNCLAIMED_RUN_DELAY, self.__openPortal)

    def _updateModel(self):
        if not self._eventCtrl.isEnabled():
            return
        super(WTInsideVehiclePortalView, self)._updateModel()
        with self.viewModel.transaction() as model:
            model.setBackButtonText(backport.text(R.strings.wt_portals.insidePortal.backButton()))
            self.__updatePortalInfo(model)
            self._updateMainVehiclePrizeModel(model.mainVehiclePrize)

    def _updateMainVehiclePrizeModel(self, model):
        vehicle = self._itemsCache.items.getItemByCD(self.__mainVehiclePrizeCD)
        model.setShortTankName(vehicle.userName)
        model.setTankLevel(vehicle.level)
        model.setTankNation(vehicle.name.split(':')[0])
        model.setTankType(vehicle.type)
        model.setRoleName(ROLE_TYPE_TO_LABEL[vehicle.role])

    def _addListeners(self):
        super(WTInsideVehiclePortalView, self)._addListeners()
        self._lootBoxesCtrl.onUpdatedConfig += self.__updateBoxesConfig
        self.viewModel.onBackButtonClick += self.__onBackClick
        self.viewModel.onRunPortalClick += self.__onRunPortal
        self.viewModel.onPreviewTankClick += self.__onPreviewTankClick
        g_eventBus.addListener(events.WtEventPortalsEvent.ON_PORTAL_AWARD_VIEW_CLOSED, self._onPortalAwardsViewClose, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.WtEventPortalsEvent.ON_BACK_TO_PORTAL, self.__onPortalAwardsViewClosed, EVENT_BUS_SCOPE.LOBBY)

    def _removeListeners(self):
        self._lootBoxesCtrl.onUpdatedConfig -= self.__updateBoxesConfig
        self.viewModel.onBackButtonClick -= self.__onBackClick
        self.viewModel.onRunPortalClick -= self.__onRunPortal
        self.viewModel.onPreviewTankClick -= self.__onPreviewTankClick
        g_eventBus.removeListener(events.WtEventPortalsEvent.ON_PORTAL_AWARD_VIEW_CLOSED, self._onPortalAwardsViewClose, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.WtEventPortalsEvent.ON_BACK_TO_PORTAL, self.__onPortalAwardsViewClosed, EVENT_BUS_SCOPE.LOBBY)
        super(WTInsideVehiclePortalView, self)._removeListeners()

    def _onClosedByUser(self):
        super(WTInsideVehiclePortalView, self)._onClosedByUser()
        g_eventBus.handleEvent(events.WtEventPortalsEvent(events.WtEventPortalsEvent.ON_PORTAL_VIEW_CLOSED), scope=EVENT_BUS_SCOPE.LOBBY)

    def _onPortalAwardsViewClose(self, _):
        self.destroyWindow()

    def _onCacheResync(self, *_):
        if not self._eventCtrl.isEnabled():
            return
        self._updateLootBoxesPurchaseCount()
        with self.viewModel.transaction() as model:
            model.setIsBoxesEnabled(self.__lootBoxesCtrl.isEnabled())
            self.__updatePortalInfo(model)

    def __onBackClick(self, isEsc=False):
        if isEsc and Waiting.isOpened('updating'):
            return
        playLootBoxPortalExit()
        parent = self.getParentWindow()
        self.destroyWindow()
        event_dispatcher.showEventStorageWindow(parent)

    def __onPortalAwardsViewClosed(self, *args):
        self._updateModel()

    def __onRunPortal(self, args=None):
        Waiting.show('updating')
        self.__openPortal()

    def __openPortal(self):
        self._lootBoxesCtrl.onPortalOpened(WhiteTigerLootBoxes.WT_TANK, parentWindow=self.getParentWindow(), callbackFailure=self.__handleRequestFailure)

    def __onPreviewTankClick(self):
        args = {'backBtnLabel': backport.text(R.strings.event.vehiclePortal.backToPortalButton())}
        showVehiclePreviewWithoutBottomPanel(self.__mainVehiclePrizeCD, backCallback=self.__previewBackCb, **args)
        self._eventCtrl.setVehicleForPreview(self.__mainVehiclePrizeCD)

    def __previewBackCb(self):
        g_eventBus.handleEvent(events.LobbySimpleEvent(events.HangarSimpleEvent.VEHICLE_PREVIEW_CLOSE), scope=EVENT_BUS_SCOPE.LOBBY)
        showEventStorageWindow()

    def __handleRequestFailure(self):
        Waiting.hide('updating')
        self.destroyWindow()

    def __updatePortalInfo(self, model):
        lootBoxType = WhiteTigerLootBoxes.WT_TANK
        model.portalAvailability.setAttemptPrice(getPortalCost(lootBoxType))
        setLootBoxesCount(model.portalAvailability, lootBoxType)

    def __updateBoxesConfig(self):
        with self.viewModel.transaction() as model:
            model.setIsBoxesEnabled(self.__lootBoxesCtrl.isEnabled())


class WTInsideVehiclePortalWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, portalType, defaultRunPortalTimes, parent=None):
        super(WTInsideVehiclePortalWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=WTInsideVehiclePortalView(), parent=parent, layer=WindowLayer.FULLSCREEN_WINDOW)

    def _initialize(self):
        super(WTInsideVehiclePortalWindow, self)._initialize()
        if Waiting.isOpened('updating'):
            Waiting.hide('updating')
