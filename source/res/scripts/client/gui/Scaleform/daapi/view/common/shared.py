# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/common/shared.py
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import VEHICLE_CAROUSEL_COUNTERS_SEEN
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_filter import FILTER_KEYS
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Optional
_CAN_BE_MARKED_AS_SEEN_VEHICLE_FILTERS = (FILTER_KEYS.OWN_3D_STYLE, FILTER_KEYS.CAN_INSTALL_ATTACHMENTS)

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def __hasAttachmentsOnAccount(itemsCache=None):
    items = itemsCache.items.getItems(GUI_ITEM_TYPE.ATTACHMENT, REQ_CRITERIA.CUSTOMIZATION.ON_ACCOUNT | REQ_CRITERIA.CUSTOM(lambda item: not item.descriptor.isHiddenInUI()))
    return bool(items)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def __hasVehiclesWith3DStylesOnAccount(itemsCache=None):
    styles = itemsCache.items.getItems(GUI_ITEM_TYPE.STYLE, REQ_CRITERIA.CUSTOMIZATION.ON_ACCOUNT | REQ_CRITERIA.CUSTOM(lambda item: item.is3D) | REQ_CRITERIA.CUSTOM(lambda item: not item.isHiddenInUI()))
    vehicles3DStyled = None
    if styles:
        vehicles3DStyled = itemsCache.items.getVehicles(REQ_CRITERIA.VEHICLE.CAN_INSTALL_C11N(GUI_ITEM_TYPE.STYLE, REQ_CRITERIA.CUSTOMIZATION.ON_ACCOUNT | REQ_CRITERIA.CUSTOM(lambda item: item.is3D) | REQ_CRITERIA.CUSTOM(lambda item: not item.isHiddenInUI())))
    return bool(vehicles3DStyled)


def isVehicleFilterNew(entry):
    if entry not in _CAN_BE_MARKED_AS_SEEN_VEHICLE_FILTERS:
        return False
    if AccountSettings.getCounters(VEHICLE_CAROUSEL_COUNTERS_SEEN).get(entry, False):
        return False
    if entry == FILTER_KEYS.CAN_INSTALL_ATTACHMENTS:
        return __hasAttachmentsOnAccount()
    return __hasVehiclesWith3DStylesOnAccount() if entry == FILTER_KEYS.OWN_3D_STYLE else False
