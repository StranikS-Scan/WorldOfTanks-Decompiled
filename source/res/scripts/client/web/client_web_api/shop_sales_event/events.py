# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/client_web_api/shop_sales_event/events.py
from helpers import dependency
from skeletons.gui.game_control import IShopSalesEventController
from web.client_web_api.api import C2WHandler, c2w
from web.common import formatShopSalesInfo

class ShopSalesEventHandler(C2WHandler):
    __shopSalesEvent = dependency.descriptor(IShopSalesEventController)

    def init(self):
        super(ShopSalesEventHandler, self).init()
        self.__shopSalesEvent.onStateChanged += self.__onInfoChanged
        self.__shopSalesEvent.onBundlePurchased += self.__onBundlePurchased
        self.__shopSalesEvent.onCurrentBundleChanged += self.__onInfoChanged

    def fini(self):
        self.__shopSalesEvent.onCurrentBundleChanged -= self.__onInfoChanged
        self.__shopSalesEvent.onBundlePurchased -= self.__onBundlePurchased
        self.__shopSalesEvent.onStateChanged -= self.__onInfoChanged
        super(ShopSalesEventHandler, self).fini()

    @c2w(name='shop_sales_info_updated')
    def __onInfoChanged(self):
        return formatShopSalesInfo()

    @c2w(name='shop_sales_bundle_purchased', preventIdentical=False)
    def __onBundlePurchased(self, messageData):
        return {'product_id': (messageData or {}).get('meta', {}).get('product_id', '')}
