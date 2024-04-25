# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/pre_battle_queue_view.py
import BigWorld
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
from gui.impl.gen import R
from gui.prb_control import prbEntityProperty
from helpers import dependency
from historical_battles.gui.impl.gen.view_models.views.lobby.order_model import OrderModel, OrderType
from historical_battles.gui.impl.gen.view_models.views.lobby.base_frontman_model import FrontmanRole
from historical_battles.gui.impl.lobby.tooltips.order_tooltip import OrderTooltip
from historical_battles.gui.impl.gen.view_models.views.lobby.pre_battle_queue_view_model import PreBattleQueueViewModel
from historical_battles.gui.impl.lobby.base_event_view import BaseEventView
from historical_battles.gui.impl.lobby.selectable_view_impl import SelectableViewImpl
from historical_battles.gui.impl.lobby.widgets.frontman_widget import FrontmanRoleIDToRole
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.shared import IItemsCache

class PreBattleQueueView(BaseEventView, SelectableViewImpl):
    __slots__ = ('__timerCallback', '__createTime')
    gameEventController = dependency.descriptor(IGameEventController)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = PreBattleQueueViewModel()
        super(PreBattleQueueView, self).__init__(settings)
        self.__createTime = 0
        self.__timerCallback = None
        return

    @property
    def viewModel(self):
        return super(PreBattleQueueView, self).getViewModel()

    @prbEntityProperty
    def prbEntity(self):
        return None

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.historical_battles.lobby.tooltips.OrderTooltip():
            orderType = event.getArgument('orderType')
            isPreview = event.getArgument('isPreview')
            isUsedInBattle = event.getArgument('isUsedInBattle')
            return OrderTooltip(orderType, isPreview, isUsedInBattle)
        return super(PreBattleQueueView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(PreBattleQueueView, self)._onLoading(*args, **kwargs)
        self._addListeners()
        self._loadModel()

    def isQuitButtonNeedDisable(self):
        prbState = self.prbDispatcher.getFunctionalState()
        battleSelectorItems = battle_selector_items.getItems()
        selected = battleSelectorItems.update(prbState)
        return True if selected.isInSquad(prbState) and not self.prbEntity.getPlayerInfo().isCommander() else False

    def _loadModel(self):
        with self.getViewModel().transaction() as model:
            self._fillOrders(model)
            model.setTimePassed(self.getTimeString())
            currentFrontman = self.gameEventController.frontController.getSelectedFrontman()
            currentVehicle = currentFrontman.getSelectedVehicle()
            if currentFrontman.hasRole():
                model.setSelectedFrontmanRole(FrontmanRoleIDToRole.get(currentFrontman.getRoleID(), FrontmanRole.AVIATION))
            model.setSelectedVehicleName(currentVehicle.shortUserName)
            model.setIsQuitButtonDisabled(self.isQuitButtonNeedDisable())

    def _fillOrders(self, model):
        activeFrontCoupon = self._gameEventController.frontCoupons.getActiveFrontCoupon()
        model.setSelectedOrderId(activeFrontCoupon.getLabel() if activeFrontCoupon and activeFrontCoupon.isDrawActive() else '')
        ordersModel = model.getOrders()
        ordersModel.clear()
        orders = self.gameEventController.frontCoupons.getGroupedFrontCoupons()
        for item in orders:
            if not item.isDrawActive():
                continue
            orderModel = OrderModel()
            orderModel.setId(item.getLabel())
            orderModel.setCount(item.getCurrentCount())
            orderModel.setIsActive(item.isActive())
            orderModel.setType(OrderType(item.getLabel()))
            ordersModel.addViewModel(orderModel)

        ordersModel.invalidate()

    def _onSyncCompleted(self, *_):
        with self.getViewModel().transaction() as model:
            self._fillOrders(model)

    def _initialize(self, *args, **kwargs):
        super(PreBattleQueueView, self)._initialize(*args, **kwargs)
        self.__timerCallback = BigWorld.callback(1, self.__updateTimer)

    def _finalize(self):
        self.__stopUpdateScreen()
        self._removeListeners()
        super(PreBattleQueueView, self)._finalize()

    def _addListeners(self):
        self.viewModel.onExitBattle += self.__onExitBattleButtonClick
        g_playerEvents.onArenaCreated += self.__onArenaCreated
        self.gameEventController.frontCoupons.onFrontCouponsUpdated += self._onSyncCompleted

    def _removeListeners(self):
        self.viewModel.onExitBattle -= self.__onExitBattleButtonClick
        g_playerEvents.onArenaCreated -= self.__onArenaCreated
        if self.gameEventController.frontCoupons:
            self.gameEventController.frontCoupons.onFrontCouponsUpdated -= self._onSyncCompleted

    def __onArenaCreated(self):
        self.__stopUpdateScreen()

    def __stopUpdateScreen(self):
        if self.__timerCallback is not None:
            BigWorld.cancelCallback(self.__timerCallback)
            self.__timerCallback = None
        return

    def __updateTimer(self):
        self.__timerCallback = BigWorld.callback(1, self.__updateTimer)
        self.viewModel.setTimePassed(self.getTimeString())
        self.__createTime += 1

    def getTimeString(self):
        timeStr = '%02d:%02d'
        return timeStr % divmod(self.__createTime, 60)

    def __onExitBattleButtonClick(self):
        self.prbEntity.exitFromQueue()
