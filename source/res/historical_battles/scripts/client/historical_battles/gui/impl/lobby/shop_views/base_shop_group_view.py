# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/shop_views/base_shop_group_view.py
import typing
import BigWorld
from historical_battles.gui.impl.lobby.base_event_view import BaseEventView
if typing.TYPE_CHECKING:
    from EventShopAccountComponentBase import ShopBundle
    from HBShopAccountComponent import HBShopAccountComponent

class BaseShopGroupView(BaseEventView):
    SHOP_GROUP_NAME = None

    @property
    def shop(self):
        return getattr(BigWorld.player(), 'HBShopAccountComponent', None)

    @property
    def bundles(self):
        return self.shop.getBundlesByGroup(self.SHOP_GROUP_NAME)

    def getGroupPurchasesLeft(self, default=None):
        return self.shop.getGroupPurchasesLeft(self.SHOP_GROUP_NAME, default)

    def _onLoading(self, *args, **kwargs):
        super(BaseShopGroupView, self)._onLoading(*args, **kwargs)
        self.shop.onShopUpdated += self._onShopUpdated
        self.shop.onBundlePurchased += self._onBundlePurchased
        self._fillBundles()

    def _finalize(self):
        if self.shop is not None:
            self.shop.onShopUpdated -= self._onShopUpdated
            self.shop.onBundlePurchased -= self._onBundlePurchased
        super(BaseShopGroupView, self)._finalize()
        return

    def _onShopUpdated(self):
        self._fillBundles()

    def _onBundlePurchased(self, bundleId):
        bundle = self.shop.getBundle(bundleId)
        if bundle.purchasesLimit is not None:
            self._fillBundles()
        return

    def _fillBundles(self):
        raise NotImplementedError
