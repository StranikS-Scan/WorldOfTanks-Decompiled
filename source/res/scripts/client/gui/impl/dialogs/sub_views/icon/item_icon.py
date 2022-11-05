# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/dialogs/sub_views/icon/item_icon.py
import logging
from gui.impl.dialogs.sub_views.icon.icon_set import IconSet
from gui.impl.gen import R
from gui.impl.gen_utils import INVALID_RES_ID
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class ItemIcon(IconSet):
    __slots__ = ()
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, itemCD):
        iconRes = INVALID_RES_ID
        item = self._itemsCache.items.getItemByCD(itemCD)
        backgrounds = []
        overlays = []
        if item:
            artefacts = R.images.gui.maps.shop.artefacts.c_180x135
            if item.itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
                iconRes = artefacts.dyn(item.descriptor.iconName)()
                backgrounds.append(R.images.gui.maps.icons.demountKit.dyn(item.getHighlightType() + '_highlight')())
                overlays.append(artefacts.dyn(item.getOverlayIconName())())
        else:
            _logger.warning('wrong itemCD %s', itemCD)
        super(ItemIcon, self).__init__(iconRes, backgrounds, overlays)
