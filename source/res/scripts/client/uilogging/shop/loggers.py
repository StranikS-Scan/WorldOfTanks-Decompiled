# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/shop/loggers.py
import json
import logging
from typing import TYPE_CHECKING, Set
from helpers.base64_utils import base64UrlDecode
from uilogging.base.logger import MetricsLogger
from uilogging.shop.base_loggers import ShopPreviewFlowLogger, ShopPreviewMetricsLogger
from uilogging.shop.logging_constants import FEATURE, ShopLogActions, ShopLogKeys, ShopLogButtons, ShopLogItemStates, ShopCloseItemStates
from wotdecorators import noexcept
if TYPE_CHECKING:
    from uilogging.types import ItemType, ItemStateType, InfoType
_logger = logging.getLogger(__name__)

class ShopMetricsLogger(MetricsLogger):
    __slots__ = ('_item',)

    def __init__(self, item):
        super(ShopMetricsLogger, self).__init__(FEATURE)
        self._item = item

    @noexcept
    def onViewClosed(self):
        self.log(action=ShopLogActions.CLOSED, item=self._item)


class ShopBuyVehicleMetricsLogger(MetricsLogger):
    __slots__ = ('_uniqueItemCode', '_itemStates')

    def __init__(self, uniqueItemCode):
        super(ShopBuyVehicleMetricsLogger, self).__init__(FEATURE)
        self._itemStates = set()
        self._uniqueItemCode = uniqueItemCode

    def reset(self):
        super(ShopBuyVehicleMetricsLogger, self).reset()
        self.clearItemStates()

    def clearItemStates(self):
        self._itemStates.clear()

    @noexcept
    def onViewOpen(self):
        self.log(action=ShopLogActions.DISPLAYED, item=ShopLogKeys.VEHICLE_BUY_VIEW, info='vehicle_{0}'.format(self._uniqueItemCode), itemState=ShopLogItemStates.CLIENT_PRODUCT)

    @noexcept
    def onViewClosed(self):
        self.log(action=ShopLogActions.CLOSED, item=ShopLogKeys.VEHICLE_BUY_VIEW, info='vehicle_{0}'.format(self._uniqueItemCode), itemState=ShopLogItemStates.CLIENT_PRODUCT)

    @noexcept
    def logVehiclePurchaseButtonClicked(self):
        self.addItemState(ShopLogItemStates.CLIENT_PRODUCT.value)
        self.log(action=ShopLogActions.VEHICLE_BUY_VIEW_PURCHASE_BUTTON_CLICKED, item=ShopLogKeys.VEHICLE_BUY_VIEW, info='vehicle_{0}'.format(self._uniqueItemCode), itemState=';'.join(self._itemStates))

    def addItemState(self, itemState):
        self._itemStates.add(itemState)


class ShopVehiclePreviewFlowLogger(ShopPreviewFlowLogger):
    __slots__ = ()

    @noexcept
    def logOpenPreview(self):
        self.log(action=ShopLogActions.DISPLAYED, sourceItem=ShopLogKeys.SHOP, destinationItem=ShopLogKeys.VEHICLE_PREVIEW, transitionMethod=ShopLogButtons.TO_PREVIEW_BUTTON)


class ShopBundleVehiclePreviewFlowLogger(ShopPreviewFlowLogger):
    __slots__ = ()

    @noexcept
    def logOpenPreview(self):
        self.log(action=ShopLogActions.DISPLAYED, sourceItem=ShopLogKeys.SHOP, destinationItem=ShopLogKeys.VEHICLE_PACK_PREVIEW, transitionMethod=ShopLogButtons.TO_PREVIEW_BUTTON)


class ShopVehicleStylePreviewFlowLogger(ShopPreviewFlowLogger):
    __slots__ = ()

    @noexcept
    def logOpenPreview(self):
        self.log(action=ShopLogActions.DISPLAYED, sourceItem=ShopLogKeys.SHOP, destinationItem=ShopLogKeys.STYLE_PREVIEW, transitionMethod=ShopLogButtons.TO_PREVIEW_BUTTON)


class ShopVehiclePreviewMetricsLogger(ShopPreviewMetricsLogger):
    __slots__ = ('_uniqueItemCode',)

    def __init__(self, uniqueItemCode):
        super(ShopVehiclePreviewMetricsLogger, self).__init__()
        self._uniqueItemCode = uniqueItemCode

    @noexcept
    def onViewOpen(self):
        self.log(action=ShopLogActions.DISPLAYED, item=ShopLogKeys.VEHICLE_PREVIEW, info='vehicle_{0}'.format(self._uniqueItemCode), itemState=ShopLogItemStates.CLIENT_PRODUCT)

    @noexcept
    def onViewClosed(self, closeItemState):
        self.log(action=ShopLogActions.CLOSED, item=ShopLogKeys.VEHICLE_PREVIEW, info='vehicle_{0}'.format(self._uniqueItemCode), itemState='{0};{1}'.format(ShopLogItemStates.CLIENT_PRODUCT.value, closeItemState))


class ShopBundleVehiclePreviewMetricsLogger(ShopPreviewMetricsLogger):
    __slots__ = ('_uniqueItemCode',)

    def __init__(self, uniqueItemCode):
        super(ShopBundleVehiclePreviewMetricsLogger, self).__init__()
        self._uniqueItemCode = uniqueItemCode

    @noexcept
    def onViewOpen(self):
        self.log(action=ShopLogActions.DISPLAYED, item=ShopLogKeys.VEHICLE_PACK_PREVIEW, info=self._uniqueItemCode, itemState=ShopLogItemStates.PLATFORM_PRODUCT)

    @noexcept
    def onViewClosed(self, closeItemState):
        self.log(action=ShopLogActions.CLOSED, item=ShopLogKeys.VEHICLE_PACK_PREVIEW, info=self._uniqueItemCode, itemState='{0};{1}'.format(ShopLogItemStates.PLATFORM_PRODUCT.value, closeItemState))

    @noexcept
    def logOpenPurchaseConfirmation(self):
        self.log(action=ShopLogActions.DISPLAYED, item=ShopLogKeys.VEHICLE_PACK_PURCHASE_CONFIRMATION, info=self._uniqueItemCode, itemState=ShopLogItemStates.PLATFORM_PRODUCT)

    @noexcept
    def logBundlePurchased(self):
        self.log(action=ShopLogActions.VEHICLE_PACK_PURCHASE_CONFIRMATION_ACCEPTED, item=ShopLogKeys.VEHICLE_PACK_PURCHASE_CONFIRMATION, info=self._uniqueItemCode, itemState=ShopLogItemStates.PLATFORM_PRODUCT)

    @noexcept
    def logPurchaseConfirmationClosed(self):
        self.log(action=ShopLogActions.CLOSED, item=ShopLogKeys.VEHICLE_PACK_PURCHASE_CONFIRMATION, info=self._uniqueItemCode, itemState=ShopLogItemStates.PLATFORM_PRODUCT)


class ShopVehicleStylePreviewMetricsLogger(ShopPreviewMetricsLogger):
    __slots__ = ('_uniqueItemCode',)

    def __init__(self, uniqueItemCode):
        super(ShopVehicleStylePreviewMetricsLogger, self).__init__()
        self._uniqueItemCode = uniqueItemCode

    @noexcept
    def onViewOpen(self):
        self.log(action=ShopLogActions.DISPLAYED, item=ShopLogKeys.STYLE_PREVIEW, info='style_{0}'.format(self._uniqueItemCode), itemState=ShopLogItemStates.CLIENT_PRODUCT)

    @noexcept
    def onViewClosed(self):
        self.log(action=ShopLogActions.CLOSED, item=ShopLogKeys.STYLE_PREVIEW, info='style_{0}'.format(self._uniqueItemCode), itemState='{0};{1}'.format(ShopLogItemStates.CLIENT_PRODUCT.value, ShopCloseItemStates.BACK_BUTTON.value))


def getPreviewUILoggers(isBundlePack, vehicleCD, buyParams):
    if isBundlePack:
        productCode = getProductCodeForPreviewLog(buyParams)
        if not productCode:
            _logger.warning('[SHOPUILOG] ShopBundleVehiclePreviewMetricsLogger expects uniqueItemCode but it is none.')
            productCode = 'UNKNOWN_PRODUCT_CODE_{0}'.format(vehicleCD)
        return (ShopBundleVehiclePreviewMetricsLogger(productCode), ShopBundleVehiclePreviewFlowLogger())
    return (ShopVehiclePreviewMetricsLogger(vehicleCD), ShopVehiclePreviewFlowLogger())


@noexcept
def getProductCodeForPreviewLog(buyParams):
    if buyParams is not None:
        partialProduct = buyParams.get('partialProduct')
        if partialProduct:
            decodeValue = base64UrlDecode(partialProduct)
            if decodeValue:
                return json.loads(decodeValue).get('productCode')
    return
