# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/customization/shared.py
from gui.shared.gui_items import GUI_ITEM_TYPE
from items.components.c11n_constants import CustomizationType
from shared_utils import CONST_CONTAINER
C11N_ITEM_TYPE_MAP = {GUI_ITEM_TYPE.PAINT: CustomizationType.PAINT,
 GUI_ITEM_TYPE.CAMOUFLAGE: CustomizationType.CAMOUFLAGE,
 GUI_ITEM_TYPE.MODIFICATION: CustomizationType.MODIFICATION,
 GUI_ITEM_TYPE.DECAL: CustomizationType.DECAL,
 GUI_ITEM_TYPE.EMBLEM: CustomizationType.DECAL,
 GUI_ITEM_TYPE.INSCRIPTION: CustomizationType.DECAL,
 GUI_ITEM_TYPE.STYLE: CustomizationType.STYLE}

class HighlightingMode(CONST_CONTAINER):
    """ Modes of the highlighter.
    
    This constants has same values as in ESelectionMode
    from bigworld_client/lib/romp/tank_region_selector.hpp.
    """
    PAINT_REGIONS = 0
    CAMO_REGIONS = 1
    WHOLE_VEHICLE = 2
    REPAINT_REGIONS_MERGED = 3


MODE_TO_C11N_TYPE = {HighlightingMode.PAINT_REGIONS: GUI_ITEM_TYPE.PAINT,
 HighlightingMode.REPAINT_REGIONS_MERGED: GUI_ITEM_TYPE.PAINT,
 HighlightingMode.CAMO_REGIONS: GUI_ITEM_TYPE.CAMOUFLAGE,
 HighlightingMode.WHOLE_VEHICLE: GUI_ITEM_TYPE.STYLE}
