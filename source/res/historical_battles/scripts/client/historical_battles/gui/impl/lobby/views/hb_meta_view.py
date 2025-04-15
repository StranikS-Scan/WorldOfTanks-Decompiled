# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/views/hb_meta_view.py
import logging
import BigWorld
from helpers import dependency, isPlayerAccount
from historical_battles.gui.sounds.sound_hangar_controller import SoundHangarController
from shared_utils import first
import HBAccountSettings
from historical_battles.gui.impl.gen.view_models.views.lobby.hb_meta_view.hb_meta_view_model import HbMetaViewModel, TabId
from historical_battles.gui.impl.lobby.tooltips.hb_special_vehicles_tooltip import HBSpecialVehiclesTooltip
from historical_battles.gui.impl.lobby.tooltips.hb_vehicle_reward_tooltip import HBVehicleRewardTooltip
from historical_battles.gui.impl.lobby.tooltips.hb_main_discount_tooltip_view import HbMainDiscountTooltipView
from historical_battles.gui.impl.lobby.tooltips.hb_coin_tooltip import HbCoinTooltip
from historical_battles.gui.impl.lobby.views.progression_view import ProgressionView
from historical_battles.gui.impl.lobby.views.division_view import DivisionView
from historical_battles.gui.impl.lobby.views.order_view import OrderView
from historical_battles.gui.impl.lobby.tooltips.order_tooltip import OrderTooltip
from historical_battles.gui.impl.lobby.tooltips.hb_simple_tooltip_view import HbSimpleTooltipView
from historical_battles.gui.impl.lobby.base_event_view import BaseEventView
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from historical_battles_common.hb_constants import AccountSettingsKeys
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from historical_battles.gui.shared.event_dispatcher import showInfoPage, showOrdersInfoWindow
from gui.shared import event_dispatcher
from skeletons.gui.shared.utils import IHangarSpace
_logger = logging.getLogger(__name__)

class HBMetaView(BaseEventView):
    _gameEventController = dependency.descriptor(IGameEventController)
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, layoutID, tabId, frontId=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = HbMetaViewModel()
        super(HBMetaView, self).__init__(settings)
        self.__tabId = None
        self.__initedTabId = tabId if tabId is not None else TabId.PROGRESS
        self.__frontId = frontId
        self.__tabs = {TabId.PROGRESS: ProgressionView(self.viewModel.progressionModel, self),
         TabId.DIVISION: DivisionView(self.viewModel.divisionModel, self),
         TabId.ORDER: OrderView(self.viewModel.orderModel, self)}
        self.__currentView = None
        self.__tooltipEnabled = True
        return

    @property
    def viewModel(self):
        return super(HBMetaView, self).getViewModel()

    @property
    def currentPresenter(self):
        return self.__currentView

    def createToolTip(self, event):
        return self.__currentView.createToolTip(event) or super(HBMetaView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.historical_battles.lobby.tooltips.HbCoinTooltip():
            return HbCoinTooltip()
        if contentID == R.views.historical_battles.lobby.tooltips.OrderTooltip():
            return OrderTooltip(**self.__currentView.getTooltipData(event).specialArgs)
        if contentID == R.views.historical_battles.lobby.tooltips.HbSpecialVehiclesTooltip():
            return HBSpecialVehiclesTooltip()
        if contentID == R.views.historical_battles.lobby.tooltips.HbVehicleRewardTooltip():
            return HBVehicleRewardTooltip()
        if contentID == R.views.historical_battles.lobby.tooltips.HbMainDiscountTooltipView():
            return HbMainDiscountTooltipView()
        return HbSimpleTooltipView(event.getArgument('id')) if contentID == R.views.historical_battles.lobby.tooltips.HbSimpleTooltipView() else None

    def _getEvents(self):
        return ((self.viewModel.onTabChange, self.__onTabChange), (self.viewModel.onClose, self.__onClose), (self.viewModel.onAboutClicked, self.__onAboutClicked))

    def _onLoading(self, *args, **kwargs):
        super(HBMetaView, self)._onLoading(args, kwargs)
        self._gameEventController.setShowingProgressionView(True)
        self.__setTab(self.__tabId)
        self.__setFrontName()
        soundCtrl = self._gameEventController.soundProgressionCtrl
        if soundCtrl:
            soundCtrl.onHBProgressionViewLoaded()

    def _onLoaded(self, *args, **kwargs):
        super(HBMetaView, self)._onLoaded(args, kwargs)
        self.__enableOptimization()

    def _finalize(self):
        self.__disableOptimization()
        self._gameEventController.setShowingProgressionView(False)
        if self.__currentView:
            self.__currentView.finalize()
        self.__currentView = None
        self.__tabs.clear()
        soundCtrl = self._gameEventController.soundProgressionCtrl
        if soundCtrl:
            soundCtrl.onHBProgressionLeave()
        SoundHangarController.onEnterHangar()
        super(HBMetaView, self)._finalize()
        return

    def __setTab(self, tabID=None):
        if tabID is None:
            tabID = self.__initedTabId
        if self.__tabId != tabID:
            self.__tabId = tabID
            if self.__tabId == TabId.ORDER:
                self.__checkShowOrderInfoView()
            if self.__currentView is not None:
                self.__currentView.finalize()
            self.__currentView = self.__tabs[self.__tabId]
            if self.__currentView is None:
                return
            with self.viewModel.transaction() as tx:
                self.__currentView.initialize()
                tx.setTabId(self.__tabId)
        return

    def __setFrontName(self):
        if self.__frontId is not None:
            self._gameEventController.updateFrontData(frontId=self.__frontId)
        return

    def __onTabChange(self, *args):
        self.__setTab(TabId(first(args).get('tabId')))

    def __onClose(self):
        event_dispatcher.showHangar()

    @staticmethod
    def __onAboutClicked():
        showInfoPage()

    def __checkShowOrderInfoView(self):
        ordersInfoSeen = HBAccountSettings.getSettings(AccountSettingsKeys.SEEN_HISTORICAL_BATTLES_ORDERS)
        if not ordersInfoSeen:
            showOrdersInfoWindow()
            HBAccountSettings.setSettings(AccountSettingsKeys.SEEN_HISTORICAL_BATTLES_ORDERS, True)

    def __enableOptimization(self):
        if isPlayerAccount() and self.__hangarSpace.spaceInited:
            BigWorld.worldDrawEnabled(False)

    def __disableOptimization(self):
        if isPlayerAccount() and self.__hangarSpace.spaceInited:
            BigWorld.worldDrawEnabled(True)
