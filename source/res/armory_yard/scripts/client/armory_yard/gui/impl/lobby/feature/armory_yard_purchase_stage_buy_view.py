# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/lobby/feature/armory_yard_purchase_stage_buy_view.py
from adisp import adisp_process
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_purchase_stage_buy_view_model import ArmoryYardPurchaseStageBuyViewModel
from armory_yard.gui.impl.lobby.feature.tooltips.armory_yard_wallet_not_available_tooltip_view import ArmoryYardWalletNotAvailableTooltipView
from armory_yard.gui.impl.lobby.feature.tooltips.armory_yard_token_stepper_tooltip_view import ArmoryYardTokenStepperTooltipView
from armory_yard.gui.shared.gui_items.items_actions import BUY_PURCHASE_STAGE_TOKENS
from armory_yard.gui.window_events import showBuyGoldForArmoryYard, showArmoryYardShopRewardWindow
from frameworks.wulf import WindowFlags, WindowLayer, ViewSettings, ViewFlags, ViewModel
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.wrappers.user_compound_price_model import BuyPriceModelBuilder
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import LobbySimpleEvent
from gui.shared.gui_items.items_actions import factory
from gui.shared.money import Currency
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from skeletons.gui.game_control import IArmoryYardController, IArmoryYardShopController, IWalletController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from armory_yard_constants import ARMORY_YARD_COIN_NAME

class ArmoryYardPurchaseStageBuyView(ViewImpl):
    __slots__ = ('__blur', '__onLoadedCallback')
    __armoryYardCtrl = dependency.descriptor(IArmoryYardController)
    __armoryYardShopCtrl = dependency.descriptor(IArmoryYardShopController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __wallet = dependency.descriptor(IWalletController)

    def __init__(self, layoutID, isBlurEnabled=False, onLoadedCallback=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = ArmoryYardPurchaseStageBuyViewModel()
        super(ArmoryYardPurchaseStageBuyView, self).__init__(settings)
        self.__blur = CachedBlur(ownLayer=self.layer - 1) if isBlurEnabled else None
        self.__onLoadedCallback = onLoadedCallback
        return

    @property
    def viewModel(self):
        return super(ArmoryYardPurchaseStageBuyView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(ArmoryYardPurchaseStageBuyView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.armory_yard.lobby.feature.tooltips.ArmoryYardWalletNotAvailableTooltipView():
            return ArmoryYardWalletNotAvailableTooltipView()
        if contentID == R.views.armory_yard.lobby.feature.tooltips.ArmoryYardTokenStepperTooltipView():
            return ArmoryYardTokenStepperTooltipView()
        return ViewImpl(ViewSettings(R.views.armory_yard.lobby.feature.tooltips.ShopCurrencyTooltipView(), model=ViewModel())) if contentID == R.views.armory_yard.lobby.feature.tooltips.ShopCurrencyTooltipView() else super(ArmoryYardPurchaseStageBuyView, self).createToolTipContent(event, contentID)

    @adisp_process
    def onBuy(self, args):
        tokens = int(args.get(ArmoryYardPurchaseStageBuyViewModel.ARG_TOKENS))
        currency = args.get(ArmoryYardPurchaseStageBuyViewModel.ARG_CURRENCY_TYPE)
        price = self.__armoryYardCtrl.getCurrencyTokenCost(currency) * tokens
        shortage = self.__itemsCache.items.stats.money.getShortage(price)
        if shortage and currency == Currency.GOLD:
            setCurrencies = shortage.getSetCurrencies()
            if len(setCurrencies) == 1:
                showBuyGoldForArmoryYard(price)
        else:
            isPostProgression = self.__armoryYardCtrl.isPostProgressionState
            action = factory.getAction(BUY_PURCHASE_STAGE_TOKENS, tokens, currency)
            result = yield factory.asyncDoAction(action)
            if result:
                self.__armoryYardCtrl.onPayed(isPostProgression, tokens, price, currency)
                showArmoryYardShopRewardWindow(backport.text(R.strings.armory_yard.currency.postProgression.titleCongrats()), backport.image(R.images.armory_yard.gui.maps.icons.shop.token.s360x270()), tokens, closeCallback=self.destroyWindow)
            else:
                self.__armoryYardCtrl.onPayedError()

    def destroyWindow(self):
        g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, ctx={'isOver3dScene': True}), EVENT_BUS_SCOPE.GLOBAL)
        super(ArmoryYardPurchaseStageBuyView, self).destroyWindow()

    def _onLoaded(self, *args, **kwargs):
        super(ArmoryYardPurchaseStageBuyView, self)._onLoaded(*args, **kwargs)
        if self.__onLoadedCallback is not None:
            self.__onLoadedCallback()
        return

    def _onLoading(self, *args, **kwargs):
        super(ArmoryYardPurchaseStageBuyView, self)._onLoading(*args, **kwargs)
        g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, ctx={'isOver3dScene': False}), EVENT_BUS_SCOPE.GLOBAL)
        if self.__blur is not None:
            self.__blur.enable()
        self.viewModel.setIsBlurEnabled(self.__blur is not None)
        self.__fullUpdate()
        return

    def _finalize(self):
        if self.__blur is not None:
            self.__blur.disable()
        super(ArmoryYardPurchaseStageBuyView, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onCancel, self.destroyWindow),
         (self.viewModel.onBack, self.destroyWindow),
         (self.viewModel.onBuy, self.onBuy),
         (self.__armoryYardShopCtrl.onProductsUpdate, self.__fullUpdate),
         (self.__armoryYardCtrl.onUpdated, self.__fullUpdate),
         (self.__armoryYardCtrl.onProgressUpdated, self.__fullUpdate),
         (self.__wallet.onWalletStatusChanged, self.__fullUpdate),
         (self.__itemsCache.onSyncCompleted, self.__fullUpdate))

    def __fullUpdate(self, *_):
        if not self.__armoryYardCtrl.isPurchaseStageActive():
            self.destroyWindow()
            return
        with self.viewModel.transaction() as vm:
            vm.setIsWalletAvailable(self.__wallet.isAvailable)
            vm.setTokensCount(self.__itemsCache.items.stats.dynamicCurrencies.get(ARMORY_YARD_COIN_NAME, 0))
            vm.setUserGold(self.__itemsCache.items.stats.gold)
            vm.setUserCrystal(self.__itemsCache.items.stats.crystal)
            vm.setPayedTokensLimit(self.__armoryYardCtrl.payedTokensLeft())
            BuyPriceModelBuilder.fillPriceModel(vm.price, self.__armoryYardCtrl.getCurrencyTokenCost(Currency.GOLD), checkBalanceAvailability=True)
            BuyPriceModelBuilder.fillPriceModel(vm.crystalPrice, self.__armoryYardCtrl.getCurrencyTokenCost(Currency.CRYSTAL), checkBalanceAvailability=True)


class ArmoryYardPurchaseStageBuyWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, parent=None, isBlurEnabled=False, onLoadedCallback=None):
        super(ArmoryYardPurchaseStageBuyWindow, self).__init__(wndFlags=WindowFlags.WINDOW, layer=WindowLayer.TOP_SUB_VIEW, content=ArmoryYardPurchaseStageBuyView(R.views.armory_yard.lobby.feature.ArmoryYardPurchaseStageBuyView(), isBlurEnabled, onLoadedCallback), parent=parent)
