# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/products_fetcher/wot_shop/descriptors/categories_descriptor.py
from gui.platform.products_fetcher.product_descriptor import ProductDescriptor

class CategoriesDescriptor(ProductDescriptor):

    @property
    def code(self):
        return self._getFromParams('code', '')

    @property
    def metadata(self):
        return self._getFromParams('metadata', {})
