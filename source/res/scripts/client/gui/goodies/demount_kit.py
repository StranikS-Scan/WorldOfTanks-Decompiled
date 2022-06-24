# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/goodies/demount_kit.py
from gui.goodies.goodie_items import DemountKit
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.shared import IItemsCache

def isDemountKitApplicableTo(optDevice):
    if optDevice.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE and not optDevice.isRemovable and not optDevice.isDeluxe:
        demountKit, _ = getDemountKitForOptDevice(optDevice)
        return demountKit and demountKit.enabled
    return False


def getDemountKitForOptDevice(optDevice):
    itemsCache = dependency.instance(IItemsCache)
    goodiesCache = dependency.instance(IGoodiesCache)
    currency = optDevice.getRemovalPrice(itemsCache.items).getCurrency()
    demountKit = goodiesCache.getDemountKit(currency=currency)
    return (demountKit, currency)
