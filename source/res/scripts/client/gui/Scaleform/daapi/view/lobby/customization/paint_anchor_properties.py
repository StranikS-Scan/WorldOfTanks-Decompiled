# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/paint_anchor_properties.py
from gui.Scaleform.daapi.view.lobby.customization.anchor_properties import ANCHOR_TYPE
from gui.Scaleform.daapi.view.lobby.customization.anchor_properties import AnchorDataVO
from gui.Scaleform.daapi.view.meta.CustomizationPaintAnchorPropertiesMeta import CustomizationPaintAnchorPropertiesMeta
from gui.Scaleform.locale.RES_ICONS import RES_ICONS

class PaintDataVO(AnchorDataVO):
    pass


class PaintAnchorProperties(CustomizationPaintAnchorPropertiesMeta):

    def _getAnchorType(self):
        return ANCHOR_TYPE.PAINT

    def _getData(self):
        itemData = self._getItemData()
        if itemData is None:
            itemData = {'intCD': 0,
             'icon': RES_ICONS.MAPS_ICONS_LIBRARY_TANKITEM_BUY_TANK_POPOVER_SMALL}
        return PaintDataVO(self._name, self._desc, self._isEmpty, itemData).asDict()
