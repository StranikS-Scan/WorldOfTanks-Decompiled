# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/wt_tank_portal.py
import logging
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.battle_pass.battle_pass_decorators import createBackportTooltipDecorator
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.Waiting import Waiting
from gui.impl.pub.lobby_window import LobbyWindow
from white_tiger.gui.impl.gen.view_models.views.common.wt_common_consts import PortalType
from white_tiger.gui.impl.gen.view_models.views.lobby.portals.wt_tank_portal_view_model import WtTankPortalViewModel
from white_tiger.gui.impl.lobby.wt_event_constants import WhiteTigerLootBoxes
from white_tiger.gui.impl.lobby.wt_event_base_portals_view import WtEventBasePortalsView
from white_tiger.gui.impl.lobby.wt_event_sound import changePortalState, playLootBoxPortalExit
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE, event_dispatcher
from gui.wt_event.wt_event_helpers import getPortalCost
from white_tiger.gui.wt_event_models_helper import hasUnclaimedLoot
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from gui.shared.event_dispatcher import showVehiclePreviewWithoutBottomPanel
from constants import ROLE_TYPE_TO_LABEL
from gui.impl.lobby.tooltips.vehicle_role_descr_view import VehicleRolesTooltipView
from skeletons.prebattle_vehicle import IPrebattleVehicle
_logger = logging.getLogger(__name__)
_UNCLAIMED_RUN_DELAY = 1

class WtTankPortalView(WtEventBasePortalsView, CallbackDelayer):
    __slots__ = ()
    __prebattleVehicle = dependency.descriptor(IPrebattleVehicle)

    def __init__(self):
        settings = ViewSettings(layoutID=R.views.white_tiger.lobby.WtTankPortalView(), model=WtTankPortalViewModel())
        super(WtTankPortalView, self).__init__(settings)
        self.__mainPrizeVehicleCD = self._lootBoxesCtrl.getMainPrizeVehicles()[0]

    @property
    def viewModel(self):
        return super(WtTankPortalView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return VehicleRolesTooltipView(self.__mainPrizeVehicleCD) if contentID == R.views.lobby.ranked.tooltips.RankedBattlesRolesTooltipView() else super(WtTankPortalView, self).createToolTipContent(event, contentID)

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(WtTankPortalView, self).createToolTip(event)

    def _onLoaded(self, *args, **kwargs):
        super(WtTankPortalView, self)._onLoaded(*args, **kwargs)
        changePortalState(PortalType.TANK)
        if hasUnclaimedLoot(WhiteTigerLootBoxes.WT_TANK):
            self.delayCallback(_UNCLAIMED_RUN_DELAY, self.__openPortal)

    def _updateModel(self):
        if not self._eventCtrl.isEnabled():
            return
        super(WtTankPortalView, self)._updateModel()
        with self.viewModel.transaction() as model:
            model.setBackButtonText(backport.text(R.strings.wt_portals.insidePortal.backButton()))
            self.__updatePortalInfo(model)
            self._updateMainPrizeModel(model.mainPrize)

    def _updateMainPrizeModel(self, model):
        vehicle = self._itemsCache.items.getItemByCD(self.__mainPrizeVehicleCD)
        model.setTankName(vehicle.userName)
        model.setTankLevel(vehicle.level)
        model.setTankNation(vehicle.name.split(':')[0])
        model.setTankType(vehicle.type)
        model.setTankRoleName(ROLE_TYPE_TO_LABEL[vehicle.role])
        model.setDiscountTokenCount(self._eventCtrl.getCurrentMainPrizeDiscountTokensCount())
        model.setDiscountPerToken(self._eventCtrl.getMainPrizeDiscountPerToken())
        model.setMaxDiscountTokenCount(self._eventCtrl.getConfig().mainPrizeMaxDiscountTokenCount)

    def _addListeners(self):
        super(WtTankPortalView, self)._addListeners()
        self._lootBoxesCtrl.onUpdatedConfig += self.__updateBoxesConfig
        self.viewModel.onGoBack += self.__onGoBack
        self.viewModel.onRunPortal += self.__onRunPortal
        self.viewModel.onPreviewTank += self.__onPreviewTank
        g_eventBus.addListener(events.WtEventPortalsEvent.ON_PORTAL_AWARD_VIEW_CLOSED, self._onPortalAwardsViewClose, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.WtEventPortalsEvent.ON_BACK_TO_PORTAL, self.__onPortalAwardsViewClosed, EVENT_BUS_SCOPE.LOBBY)

    def _removeListeners(self):
        self._lootBoxesCtrl.onUpdatedConfig -= self.__updateBoxesConfig
        self.viewModel.onGoBack -= self.__onGoBack
        self.viewModel.onRunPortal -= self.__onRunPortal
        self.viewModel.onPreviewTank -= self.__onPreviewTank
        g_eventBus.removeListener(events.WtEventPortalsEvent.ON_PORTAL_AWARD_VIEW_CLOSED, self._onPortalAwardsViewClose, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.WtEventPortalsEvent.ON_BACK_TO_PORTAL, self.__onPortalAwardsViewClosed, EVENT_BUS_SCOPE.LOBBY)
        super(WtTankPortalView, self)._removeListeners()

    def _onClosedByUser(self):
        super(WtTankPortalView, self)._onClosedByUser()
        g_eventBus.handleEvent(events.WtEventPortalsEvent(events.WtEventPortalsEvent.ON_PORTAL_VIEW_CLOSED), scope=EVENT_BUS_SCOPE.LOBBY)

    def _onPortalAwardsViewClose(self, _):
        self.destroyWindow()

    def _onCacheResync(self, *_):
        if not self._eventCtrl.isEnabled():
            return
        with self.viewModel.transaction() as model:
            model.setIsBoxesEnabled(self._lootBoxesCtrl.isEnabled())
            self.__updatePortalInfo(model)

    def __onGoBack(self):
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

    def __onPreviewTank(self):
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.configurable_vehicle_preview import OptionalBlocks
        args = {'backBtnLabel': backport.text(R.strings.event.vehiclePortal.backToPortalButton()),
         'hiddenBlocks': (OptionalBlocks.BUYING_PANEL,)}
        showVehiclePreviewWithoutBottomPanel(self.__mainPrizeVehicleCD, backCallback=self.__previewBackCb, **args)
        self._eventCtrl.setVehicleForPreview(self.__mainPrizeVehicleCD)
        self._eventCtrl.getLootBoxAreaSoundMgr().leave()

    def __previewBackCb(self):
        g_eventBus.handleEvent(events.LobbySimpleEvent(events.HangarSimpleEvent.VEHICLE_PREVIEW_CLOSE), scope=EVENT_BUS_SCOPE.LOBBY)
        parent = self.getParentWindow()
        self.destroyWindow()
        event_dispatcher.showEventStorageWindow(parent)
        self.__prebattleVehicle.selectAny()

    def __handleRequestFailure(self):
        Waiting.hide('updating')
        self.destroyWindow()

    def __updatePortalInfo(self, model):
        lootBoxType = WhiteTigerLootBoxes.WT_TANK
        model.portalRun.setAttemptPrice(getPortalCost(lootBoxType))
        lootBoxesCount = self._lootBoxesCtrl.getLootBoxesCountByType(lootBoxType, excludePending=True)
        model.portalRun.setLootBoxesCount(lootBoxesCount)

    def __updateBoxesConfig(self):
        with self.viewModel.transaction() as model:
            model.setIsBoxesEnabled(self._lootBoxesCtrl.isEnabled())


class WtTankPortalWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, parent=None):
        super(WtTankPortalWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=WtTankPortalView(), parent=parent, layer=WindowLayer.FULLSCREEN_WINDOW)

    def _initialize(self):
        super(WtTankPortalWindow, self)._initialize()
        if Waiting.isOpened('updating'):
            Waiting.hide('updating')
