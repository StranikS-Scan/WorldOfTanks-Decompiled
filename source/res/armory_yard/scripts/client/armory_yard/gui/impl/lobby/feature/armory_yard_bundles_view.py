# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/lobby/feature/armory_yard_bundles_view.py
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_bundles_view_model import ArmoryYardBundlesViewModel
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_bundle_model import ArmoryYardBundleModel, BundleType
from armory_yard.gui.window_events import showArmoryYardBuyWindow, showArmoryYardBuyBundleWindow
from frameworks.wulf import WindowFlags, WindowLayer, ViewSettings, ViewFlags
from gui.impl.gen import R
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.wrappers.user_compound_price_model import PriceModelBuilder
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import LobbySimpleEvent
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency, time_utils
from skeletons.gui.game_control import IArmoryYardController, IWalletController
from skeletons.gui.shared import IItemsCache
BUNDLE_TYPES = {'small_bundle': BundleType.SMALL,
 'medium_bundle': BundleType.MEDIUM,
 'large_bundle': BundleType.LARGE}

class ArmoryYardBundlesView(ViewImpl):
    __slots__ = ('__blur', '__onLoadedCallback', '__parent')
    __armoryYardCtrl = dependency.descriptor(IArmoryYardController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __wallet = dependency.descriptor(IWalletController)

    def __init__(self, layoutID, parent=None, isBlurEnabled=False, onLoadedCallback=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = ArmoryYardBundlesViewModel()
        super(ArmoryYardBundlesView, self).__init__(settings)
        self.__blur = CachedBlur(ownLayer=self.layer - 1) if isBlurEnabled else None
        self.__onLoadedCallback = onLoadedCallback
        self.__parent = parent
        return

    @property
    def viewModel(self):
        return super(ArmoryYardBundlesView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(ArmoryYardBundlesView, self).createToolTip(event)

    def destroyWindow(self, isScene=False):
        if isScene:
            g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, ctx={'isOver3dScene': True}), EVENT_BUS_SCOPE.GLOBAL)
        super(ArmoryYardBundlesView, self).destroyWindow()

    def onClose(self):
        self.destroyWindow(isScene=True)

    def onBuyBundle(self, args):
        showArmoryYardBuyBundleWindow(args.get('bundleId'), parent=self.__parent, onLoadedCallback=self.__onLoadedCallback, onClosedCallback=self.destroyWindow)

    def onBuyTokens(self):
        showArmoryYardBuyWindow(parent=self.__parent, onLoadedCallback=self.__onLoadedCallback)
        self.destroyWindow()

    def _onLoaded(self, *args, **kwargs):
        super(ArmoryYardBundlesView, self)._onLoaded(*args, **kwargs)
        if self.__onLoadedCallback is not None:
            self.__onLoadedCallback()
        return

    def _onLoading(self, *args, **kwargs):
        super(ArmoryYardBundlesView, self)._onLoading(*args, **kwargs)
        g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, ctx={'isOver3dScene': False}), EVENT_BUS_SCOPE.GLOBAL)
        if self.__blur is not None:
            self.__blur.enable()
        self.viewModel.setIsBlurEnabled(self.__blur is not None)
        self.__onEventUpdated()
        self.__onProgressUpdated()
        return

    def _finalize(self):
        if self.__blur is not None:
            self.__blur.disable()
        super(ArmoryYardBundlesView, self)._finalize()
        return

    def __onEventUpdated(self):
        if not self.__armoryYardCtrl.isActive() or self.__armoryYardCtrl.isCompleted() or not self.__armoryYardCtrl.isStarterPackAvailable():
            self.destroyWindow(isScene=True)
            return
        packsSettings = self.__armoryYardCtrl.getStarterPackSettings()
        with self.viewModel.transaction() as vm:
            PriceModelBuilder.fillPriceModel(vm.tokenPrice, self.__armoryYardCtrl.getCurrencyTokenCost())
            vm.setCurrentTime(time_utils.getServerUTCTime())
            vm.setEndTime(packsSettings['endTime'])
            bundles = vm.getBundles()
            bundles.clear()
            for product in self.__armoryYardCtrl.bundlesProducts:
                bundleModel = ArmoryYardBundleModel()
                tokensCount = product['tokens']
                price = self.__armoryYardCtrl.getCurrencyTokenCost() * tokensCount
                discountPrice = product['price']
                discount = price - discountPrice
                currency = discountPrice.getCurrency()
                bundleType = BundleType.MEDIUM
                for tag in product['tags']:
                    if tag in BUNDLE_TYPES:
                        bundleType = BUNDLE_TYPES[tag]
                        break

                bundleModel.setType(bundleType)
                bundleModel.setIndex(product['id'])
                bundleModel.setLevelCount(tokensCount)
                bundleModel.setDiscountPercent(int(discount.getSignValue(currency) / (price.getSignValue(currency) / 100)))
                PriceModelBuilder.fillPriceModel(bundleModel.price, price, action=discountPrice, defPrice=price)
                bundles.addViewModel(bundleModel)

            bundles.invalidate()

    def __onProgressUpdated(self):
        if not self.__armoryYardCtrl.isActive() or self.__armoryYardCtrl.isCompleted() or not self.__armoryYardCtrl.isStarterPackAvailable():
            self.destroyWindow(isScene=True)
            return
        with self.viewModel.transaction() as vm:
            vm.setCurrentLevel(self.__armoryYardCtrl.getCurrentProgress())

    def _getEvents(self):
        return ((self.viewModel.onClose, self.onClose),
         (self.viewModel.onBuyBundle, self.onBuyBundle),
         (self.viewModel.onBuyTokens, self.onBuyTokens),
         (self.__armoryYardCtrl.onUpdated, self.__onEventUpdated),
         (self.__armoryYardCtrl.onProgressUpdated, self.__onProgressUpdated),
         (self.__armoryYardCtrl.onBundlesDisabled, self.__onEventUpdated))


class ArmoryYardBundlesWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, parent=None, isBlurEnabled=False, onLoadedCallback=None):
        super(ArmoryYardBundlesWindow, self).__init__(wndFlags=WindowFlags.WINDOW, layer=WindowLayer.TOP_SUB_VIEW, content=ArmoryYardBundlesView(R.views.armory_yard.lobby.feature.ArmoryYardBundlesView(), parent, isBlurEnabled, onLoadedCallback), parent=parent)
