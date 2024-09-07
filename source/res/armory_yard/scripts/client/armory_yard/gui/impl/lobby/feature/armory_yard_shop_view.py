# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/lobby/feature/armory_yard_shop_view.py
import logging
from account_helpers.AccountSettings import ArmoryYard, AccountSettings
from armory_yard.gui.impl.lobby.feature.armory_yard_shop_base import ArmoryYardShopBaseView
from armory_yard.gui.impl.lobby.feature.tooltips.armory_yard_simple_tooltip_view import ArmoryYardSimpleTooltipView
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_shop_view_model import ArmoryYardShopViewModel, BackButtonState
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_main_view_model import TabId
from armory_yard.gui.window_events import showArmoryYardShopBuyWindow
from armory_yard.gui.shared.shop_bonus_packers import packShopItem
from frameworks.wulf import WindowFlags, WindowLayer, ViewSettings, ViewFlags, ViewModel
from gui.impl.gen import R
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.wrappers.user_compound_price_model import PriceModelBuilder
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getShopRootUrl
from gui.shared.money import Money, Currency
from gui.shop import showIngameShop, Origin
from helpers import dependency
from skeletons.gui.game_control import IArmoryYardShopController, IArmoryYardController
_logger = logging.getLogger(__name__)

class ArmoryYardShopView(ArmoryYardShopBaseView):
    __slots__ = ('__isArmoryVisiting',)
    __ayShopCtrl = dependency.descriptor(IArmoryYardShopController)
    __ayCtrl = dependency.descriptor(IArmoryYardController)

    def __init__(self, layoutID, onLoadedCallback=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = ArmoryYardShopViewModel()
        super(ArmoryYardShopView, self).__init__(settings, onLoadedCallback)
        self.__isArmoryVisiting = self.__ayCtrl.isArmoryVisiting

    @property
    def viewModel(self):
        return super(ArmoryYardShopView, self).getViewModel()

    def __onBuyProduct(self, args):
        productId = int(args.get('productId', -1))
        if productId and productId in self.__ayShopCtrl.products:
            showArmoryYardShopBuyWindow(productId, onClosedCallback=self.destroyWindow)

    def __onCurrencyUpdate(self):
        with self.viewModel.transaction() as vm:
            vm.setCurrency(self.__ayShopCtrl.ayCoins)

    def __update(self):
        if not self.__ayShopCtrl.isEnabled:
            self.destroyWindow()
            return
        else:
            goldCost = self.__ayShopCtrl.conversionPrices.get(Currency.GOLD, None)
            if goldCost is None:
                _logger.error('ArmoryYardShop gold coins cost not valid')
                self.destroyWindow()
                return
            isIntroViewed = not AccountSettings.getArmoryYard(ArmoryYard.ARMORY_SHOP_INTRO_VIEWED)
            if isIntroViewed:
                AccountSettings.setArmoryYard(ArmoryYard.ARMORY_SHOP_INTRO_VIEWED, True)
            with self.viewModel.transaction() as vm:
                vm.setIsIntroVisible(isIntroViewed)
                vm.setCurrency(self.__ayShopCtrl.ayCoins)
                vm.setBackButtonState(BackButtonState.ARMORY if self.__ayCtrl.isArmoryVisiting else BackButtonState.INGAMESHOP)
                PriceModelBuilder.fillPriceModel(vm.tokenPrice, Money.makeFrom(Currency.GOLD, goldCost))
                items = vm.getItems()
                items.clear()
                for productId, product in self.__ayShopCtrl.products.iteritems():
                    item = packShopItem(productId, product)
                    if item is None:
                        _logger.error('ArmoryYardShop product %s failed pack', productId)
                    if item.getAvailable():
                        items.addViewModel(item)

                items.invalidate()
            return

    def onBack(self):
        self.destroyWindow()
        if self.__isArmoryVisiting:
            self.__ayCtrl.goToArmoryYard(tabId=TabId.PROGRESS)
        else:
            showIngameShop(getShopRootUrl(), Origin.HANGAR_TOP_MENU)

    def _getEvents(self):
        return ((self.viewModel.onBack, self.onBack),
         (self.viewModel.onClose, self.onBack),
         (self.viewModel.onBuyProduct, self.__onBuyProduct),
         (self.viewModel.onCloseIntro, lambda : self.viewModel.setIsIntroVisible(False)),
         (self.viewModel.onShowIntro, lambda : self.viewModel.setIsIntroVisible(True)),
         (self.__ayShopCtrl.onProductsUpdate, self.__update),
         (self.__ayShopCtrl.onAYCoinsUpdate, self.__onCurrencyUpdate),
         (self.__ayShopCtrl.onSettingsUpdate, self.__update),
         (self.__ayCtrl.onUpdated, self.__checkExit))

    def __checkExit(self):
        if not self.__ayCtrl.isActive() and self.__isArmoryVisiting:
            self.destroyWindow()

    def _onLoading(self, *args, **kwargs):
        super(ArmoryYardShopView, self)._onLoading(*args, **kwargs)
        self.__update()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(ArmoryYardShopView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.armory_yard.lobby.feature.tooltips.ArmoryYardSimpleTooltipView():
            return ArmoryYardSimpleTooltipView(event.getArgument('state'), event.getArgument('id'))
        return ViewImpl(ViewSettings(R.views.armory_yard.lobby.feature.tooltips.ShopCurrencyTooltipView(), model=ViewModel())) if contentID == R.views.armory_yard.lobby.feature.tooltips.ShopCurrencyTooltipView() else super(ArmoryYardShopView, self).createToolTipContent(event, contentID)


class ArmoryYardShopWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, parent=None, onLoadedCallback=None):
        super(ArmoryYardShopWindow, self).__init__(wndFlags=WindowFlags.WINDOW, layer=WindowLayer.TOP_SUB_VIEW, content=ArmoryYardShopView(R.views.armory_yard.lobby.feature.ArmoryYardShopView(), onLoadedCallback=onLoadedCallback), parent=parent)
