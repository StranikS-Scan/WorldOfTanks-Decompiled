# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/dialogs/sub_views/icon/item_icon.py
import logging
from gui.impl.gen import R
from gui.impl.dialogs.sub_views.common import IconSetData
from gui.impl.dialogs.sub_views.icon.multiple_icons_set import MultipleIconsSet
from gui.impl.dialogs.sub_views.common.simple_text import ImageSubstitution
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import getNationLessName, getIconResourceName
from gui.shared.utils.functions import replaceHyphenToUnderscore
from helpers import dependency, int2roman
from skeletons.gui.shared import IItemsCache
from typing import TYPE_CHECKING
_logger = logging.getLogger(__name__)
if TYPE_CHECKING:
    from typing import List, Optional
    from gui.shared.gui_items.Vehicle import Vehicle
    from gui.shared.gui_items.artefacts import OptionalDevice

def vehicleToIconSetDataFormatter(vehicle, backgrounds, overlays):
    artefacts = R.images.gui.maps.shop.vehicles.num('180x135')
    return IconSetData(artefacts.dyn(getNationLessName(replaceHyphenToUnderscore(vehicle.name)))(), '{}  %(typeIcon)  {}'.format(int2roman(vehicle.level), vehicle.shortUserName), [ImageSubstitution(R.images.gui.maps.icons.vehicleTypes.dyn(getIconResourceName(vehicle.type))(), 'typeIcon', 3, -5, -5, -5)])


def optionalDeviceToIconSetDataFormatter(optDevice, backgrounds, overlays):
    artefacts = R.images.gui.maps.shop.artefacts.num('180x135')
    backgrounds.append(R.images.gui.maps.icons.demountKit.dyn(optDevice.getHighlightType() + '_highlight')())
    overlays.append(artefacts.dyn(optDevice.getOverlayIconName())())
    return IconSetData(artefacts.dyn(optDevice.descriptor.iconName)(), None, None)


ITEM_FORMATTERS = {GUI_ITEM_TYPE.VEHICLE: vehicleToIconSetDataFormatter,
 GUI_ITEM_TYPE.OPTIONALDEVICE: optionalDeviceToIconSetDataFormatter}

class ItemIcons(MultipleIconsSet):
    __slots__ = ()
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, items, isItemExchange=False):
        iconsRes = []
        backgrounds = []
        overlays = []
        for itemCD in items:
            item = self._itemsCache.items.getItemByCD(itemCD)
            if not item:
                _logger.warning('wrong itemCD %s', itemCD)
                continue
            if item.itemTypeID in ITEM_FORMATTERS:
                iconsRes.append(ITEM_FORMATTERS[item.itemTypeID](item, backgrounds, overlays))

        if isItemExchange:
            iconsRes.insert(len(iconsRes) // 2, IconSetData(R.images.gui.maps.icons.library.dialog_change_arrow(), None, None))
        super(ItemIcons, self).__init__(iconsRes, backgrounds, overlays)
        return
