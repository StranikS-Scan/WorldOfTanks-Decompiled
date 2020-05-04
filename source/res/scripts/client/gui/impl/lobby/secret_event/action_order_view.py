# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/secret_event/action_order_view.py
import logging
from frameworks.wulf import ViewSettings, ViewFlags
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import createTooltipData, BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.secret_event.action_menu_model import ActionMenuModel
from gui.impl.gen.view_models.views.lobby.secret_event.action_order_model import ActionOrderModel
from gui.impl.gen.view_models.views.lobby.secret_event.general_filter_item_model import GeneralFilterItemModel
from gui.impl.gen.view_models.views.lobby.secret_event.order_model import OrderModel
from gui.impl.lobby.secret_event import EnergyMixin
from gui.impl.lobby.secret_event.action_view_with_menu import ActionViewWithMenu
from gui.server_events.events_dispatcher import showOrderSelectView
from gui.shared import event_dispatcher
from helpers import dependency
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class ActionOrderView(ActionViewWithMenu, EnergyMixin):
    gameEventController = dependency.descriptor(IGameEventController)
    _itemsCache = dependency.descriptor(IItemsCache)
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, layoutID, ctx=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = ActionOrderModel()
        self.__battleQuestData = None
        self.__generalID = None
        self.__layoutID = layoutID
        self._stats = self._itemsCache.items.stats
        super(ActionOrderView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            specialArgs = []
            window = None
            if tooltipId == TOOLTIPS_CONSTANTS.EVENT_ENERGY_DISCOUNT:
                specialArgs = [event.getArgument('tokenID')]
            elif tooltipId == 'orderTooltip':
                tooltipId = TOOLTIPS_CONSTANTS.EVENT_BONUSES_INFO
                specialArgs = [event.getArgument('id')]
            window = BackportTooltipWindow(createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=specialArgs), self.getParentWindow())
            if window:
                window.load()
                return window
        return super(ActionOrderView, self).createToolTip(event)

    def _initialize(self, *args, **kwargs):
        super(ActionOrderView, self)._initialize()
        self.viewModel.onBuyPack += self.__onBuyPackClick
        self.viewModel.onFilterChange += self.__onFilterChange
        self._itemsCache.onSyncCompleted += self._onInventoryResync
        self.eventsCache.onSyncCompleted += self._onInventoryResync
        self._eventCacheSubscribe()

    def _onLoading(self, *args, **kwargs):
        super(ActionOrderView, self)._onLoading()
        self.__generalID = self.gameEventController.getSelectedCommanderID()
        self.viewModel.setCurrentView(ActionMenuModel.ORDERS)
        self.__fillViewModel()
        self.__fillFilter()

    def _finalize(self):
        self.viewModel.onBuyPack -= self.__onBuyPackClick
        self.viewModel.onFilterChange -= self.__onFilterChange
        super(ActionOrderView, self)._finalize()
        self._itemsCache.onSyncCompleted -= self._onInventoryResync
        self.eventsCache.onSyncCompleted -= self._onInventoryResync
        self._eventCacheUnsubscribe()

    def _onInventoryResync(self, *args, **kwargs):
        self.__fillViewModel(self.__generalID)

    def __fillViewModel(self, generalId=None):
        if generalId is None:
            generalId = self.gameEventController.getSelectedCommanderID()
        commander = self.gameEventController.getCommanders().get(generalId)
        self.__battleQuestData = self.getBattleQuestData(commander.getQuestEnergyID())
        refillOrder = self.getEnergyData(commander, commander.getRefillEnergyID(), OrderModel.TIMER, forceEnabled=True)
        buyableOrder = self.getEnergyData(commander, commander.getBuyEnergyID(), OrderModel.BUY, forceEnabled=True)
        questOrder = self.getEnergyData(commander, commander.getQuestEnergyID(), OrderModel.EXCHANGE, forceEnabled=True)
        shop = self.gameEventController.getShop()
        shopItem = shop.getExchangePackOfGeneral(generalId)
        tokenID, amount = shopItem.getPriceInTokens()
        with self.viewModel.transaction() as vm:
            vm.orders.clearItems()
            vm.setSelectedGeneralId(generalId)
            vm.setGeneralName(R.strings.event.unit.name.num(generalId)())
            vm.exchangePack.setId(questOrder.id_)
            vm.exchangePack.setTokenCount(shop.getExchangeTokenCount())
            vm.exchangePack.setOrderExchange(1)
            vm.exchangePack.setTokenExchange(amount)
            vm.exchangePack.setCount(questOrder.currentCount)
            vm.exchangePack.setIcon(questOrder.hangarIcon250x250)
            vm.exchangePack.setTooltipId(questOrder.tooltipId)
            vm.exchangePack.setType(questOrder.orderType)
            vm.exchangePack.setOrderModifier(questOrder.modifier)
            vm.exchangePack.setIsTokenShortage(shopItem.isTokenShortage)
            vm.exchangePack.setTokenID(tokenID)
            vm.orders.addViewModel(self.__createOrder(refillOrder))
            vm.orders.addViewModel(self.__createOrder(buyableOrder))
            vm.orders.invalidate()
        return

    def __createOrder(self, orderData):
        order = OrderModel()
        order.setIcon(orderData.hangarIcon250x250)
        order.setCount(orderData.currentCount)
        order.setIsSelected(orderData.isSelected)
        order.setTimer(orderData.nextRechargeTime)
        order.setId(orderData.id_)
        order.setTooltipId(orderData.tooltipId)
        order.setRechargeCount(orderData.nextRechargeCount)
        order.setType(orderData.orderType)
        order.setOrderModifier(orderData.modifier)
        return order

    def __fillFilter(self):
        filterItems = self.viewModel.filterItems
        for id_ in self.gameEventController.getCommanders():
            filterItem = GeneralFilterItemModel()
            filterItem.setGeneralId(id_)
            filterItem.setGeneralName(R.strings.event.unit.name.num(id_)())
            filterItems.addViewModel(filterItem)

        filterItems.invalidate()

    def __onBuyPackClick(self, args=None):
        isBuy = args.get('isBuy', True)
        if isBuy:
            showOrderSelectView(self.__generalID, isExchange=False)
        else:
            shop = self.gameEventController.getShop()
            shopItem = shop.getExchangePackOfGeneral(self.__generalID)
            shop.buy(shopItem.packID)
            event_dispatcher.loadSecretEventTabMenu(ActionMenuModel.BASE)

    def __onFilterChange(self, args=None):
        if args is None:
            _logger.error("Can't find params. args=None. Please fix JS")
            return
        else:
            self.__generalID = int(args.get('id'))
            self.__fillViewModel(self.__generalID)
            return
