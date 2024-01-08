# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/platform/product_purchase_controller.py
from collections import namedtuple
WotShopPrice = namedtuple('WotShopPrice', ('currency', 'value'))

class IWotShopPurchaseController(object):

    def purchaseProduct(self, storefront, productCode, productPrice):
        raise NotImplementedError
