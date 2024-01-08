# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/products_fetcher/wot_shop/descriptors/account_limits_descriptor.py
from gui.platform.products_fetcher.product_descriptor import ProductDescriptor

class AccountLimitsDescriptor(ProductDescriptor):

    @property
    def limitedQuantity(self):
        return self._getFromParams('limited_quantity', {})

    @property
    def purchaseAllowed(self):
        return self.limitedQuantity['purchase_allowed']

    @property
    def personalCount(self):
        return self.limitedQuantity['personal_count']

    @property
    def personalLimit(self):
        return self.limitedQuantity['personal_limit']
