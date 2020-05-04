# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/secret_event/order_select_view.py
import logging
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.gen.view_models.views.lobby.secret_event.action_menu_model import ActionMenuModel
from gui.impl.gen.view_models.views.lobby.secret_event.order_exchange_model import OrderExchangeModel
from gui.impl.gen.view_models.views.lobby.secret_event.order_model import OrderModel
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
from frameworks.wulf import ViewSettings, ViewFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.secret_event.order_select_model import OrderSelectModel
from gui.impl.gen.view_models.views.lobby.secret_event.pack_card_model import PackCardModel
from gui.impl.lobby.secret_event import EnergyMixin, convertPriceToMoney, EventViewMixin, convertPriceToTuple
from gui.impl.pub import ViewImpl
from gui.ingame_shop import showBuyGoldForSecretEventItem
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE, event_dispatcher
from gui.shared.event_dispatcher import showOrderBuyDialog
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class OrderSelectView(ViewImpl, EnergyMixin, EventViewMixin):
    gameEventController = dependency.descriptor(IGameEventController)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, layoutID=R.views.lobby.secretEvent.OrderSelectWindow(), generalID=None, isExchange=False):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.TOP_WINDOW_VIEW
        settings.model = OrderSelectModel()
        self.__generalID = generalID if generalID is not None else self.gameEventController.getSelectedCommanderID()
        self.__layoutID = layoutID
        self.__isExchange = isExchange
        self._stats = self._itemsCache.items.stats
        super(OrderSelectView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            specialArgs = []
            window = None
            if tooltipId == TOOLTIPS_CONSTANTS.ACTION_PRICE:
                packId = event.getArgument('packID')
                item = self.gameEventController.getShop().getItem(packId)
                args = (ACTION_TOOLTIPS_TYPE.ITEM,
                 GUI_ITEM_TYPE.VEHICLE,
                 convertPriceToTuple(*item.getPrice()),
                 convertPriceToTuple(*item.getDefPrice()),
                 True)
                window = BackportTooltipWindow(createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=args), self.getParentWindow())
            elif tooltipId == TOOLTIPS_CONSTANTS.EVENT_ENERGY_DISCOUNT:
                specialArgs = [event.getArgument('tokenID')]
            elif tooltipId == 'orderTooltip':
                tooltipId = TOOLTIPS_CONSTANTS.EVENT_BONUSES_INFO
                specialArgs = [event.getArgument('id')]
            if window is None:
                window = BackportTooltipWindow(createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=specialArgs), self.getParentWindow())
            if window:
                window.load()
                return window
        return super(OrderSelectView, self).createToolTip(event)

    def _initialize(self, *args, **kwargs):
        super(OrderSelectView, self)._initialize()
        self.viewModel.onBuyPack += self.__onBuyPackClick
        self.viewModel.onClose += self.__onClose
        self._itemsCache.onSyncCompleted += self._onInventoryResync
        self._eventCacheSubscribe()

    def _onLoading(self, *args, **kwargs):
        super(OrderSelectView, self)._onLoading()
        self.__fillViewModel(self.__generalID)

    def _finalize(self):
        self.viewModel.onBuyPack -= self.__onBuyPackClick
        self.viewModel.onClose -= self.__onClose
        self._itemsCache.onSyncCompleted -= self._onInventoryResync
        self._eventCacheUnsubscribe()
        super(OrderSelectView, self)._finalize()

    def _onInventoryResync(self, *args, **kwargs):
        self.__fillViewModel(self.__generalID)

    def _closeView(self):
        self.destroy()

    def __fillExchangePack(self):
        generalID = self.gameEventController.getSelectedCommanderID()
        commander = self.gameEventController.getSelectedCommander()
        questOrder = self.getEnergyData(commander, commander.getQuestEnergyID(), OrderModel.EXCHANGE, forceEnabled=True)
        shop = self.gameEventController.getShop()
        shopItem = shop.getExchangePackOfGeneral(generalID)
        tokenID, amount = shopItem.getPriceInTokens()
        with self.viewModel.exchangePack.transaction() as vm:
            vm.setId(questOrder.id_)
            vm.setTokenCount(shop.getExchangeTokenCount())
            vm.setOrderExchange(shopItem.energyCount)
            vm.setTokenExchange(amount)
            vm.setCount(questOrder.currentCount)
            vm.setIcon(questOrder.hangarIcon250x250)
            vm.setTooltipId(questOrder.tooltipId)
            vm.setType(questOrder.orderType)
            vm.setOrderModifier(questOrder.modifier)
            vm.setIsTokenShortage(shopItem.isTokenShortage)
            vm.setTokenID(tokenID)

    def __fillViewModel(self, generalId=None):
        if generalId is None:
            generalId = self.gameEventController.getSelectedCommanderID()
        commander = self.gameEventController.getCommanders().get(generalId)
        energyData = self.getEnergyData(commander, commander.getBuyEnergyID(), forceEnabled=True)
        self.viewModel.setGeneralID(generalId)
        self.__setStats()
        self.viewModel.packItems.clearItems()
        self.viewModel.setIsExchange(self.__isExchange)
        if self.__isExchange:
            self.__fillExchangePack()
            return
        else:
            with self.viewModel.transaction() as vm:
                lst = sorted(self.getShopItems(self.gameEventController, generalId, energyData.modifier).itervalues(), key=lambda x: x.energyCount)
                for item in lst:
                    packItem = PackCardModel()
                    packItem.setType(item.packGuiType)
                    packItem.setOrderModifier(energyData.modifier)
                    packItem.setId(item.packID)
                    packItem.setBuyCount(item.energyCount)
                    self.fillPriceByShopItem(packItem.price, item)
                    vm.packItems.addViewModel(packItem)

                vm.packItems.invalidate()
            return

    def __setStats(self):
        with self.viewModel.transaction() as vm:
            vm.setCredits(int(self._stats.money.getSignValue(Currency.CREDITS)))
            vm.setGolds(int(self._stats.money.getSignValue(Currency.GOLD)))
            vm.setCrystals(int(self._stats.money.getSignValue(Currency.CRYSTAL)))
            vm.setFreexp(self._stats.freeXP)

    def __onBuyPackClick(self, args=None):
        if args is not None:
            orderID = args.get('orderId')
            isBuyPack = args.get('isBuy', False)
            if not isBuyPack:
                shop = self.gameEventController.getShop()
                shopItem = shop.getExchangePackOfGeneral(self.gameEventController.getSelectedCommanderID())
                shop.buy(shopItem.packID)
                g_eventBus.handleEvent(events.DestroyUnboundViewEvent(self.__layoutID))
                event_dispatcher.loadSecretEventTabMenu(ActionMenuModel.BASE)
            if orderID:
                item = self.gameEventController.getShop().getItem(orderID)
                currency, price = item.getPrice()
                if not bool(self._stats.money.getShortage(convertPriceToMoney(currency, price))):
                    showOrderBuyDialog(generalID=self.__generalID, orderID=orderID, parentID=self.__layoutID)
                else:
                    showBuyGoldForSecretEventItem(price)
            else:
                _logger.error("Can't find orderId in params. Please fix JS")
        else:
            _logger.error("Can't find params. args=None. Please fix JS")
        return

    def __onClose(self):
        g_eventBus.handleEvent(events.DestroyUnboundViewEvent(self.__layoutID), scope=EVENT_BUS_SCOPE.LOBBY)
