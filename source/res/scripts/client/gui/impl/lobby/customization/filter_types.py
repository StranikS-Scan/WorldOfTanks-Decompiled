# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/customization/filter_types.py
from enum import IntEnum, Enum
from gui.impl.gen.view_models.views.lobby.customization.customization_filter_model import StructureBlockType
from gui.impl.lobby.customization.shared import CustomizationTabs

class CarouselFilterTypes(object):
    GROUP = 'group'
    DISPLAY_GROUP = 'displayGroup'
    HISTORIC = 'historic'
    NON_HISTORIC = 'nonHistoric'
    FANTASTICAL = 'fantastical'
    INVENTORY = 'inventory'
    SALE = 'sale'
    AVAILABILITY = 'availability'
    APPLIED = 'applied'
    FAVORITE = 'favorite'
    ON_ANOTHER_VEH = 'onAnotherVeh'
    ONLY_PROGRESSION_DECALS = 'onlyProgressionDecals'
    ONLY_EDITABLE_STYLES = 'onlyEditableStyles'
    ONLY_NON_EDITABLE_STYLES = 'onlyNonEditableStyles'
    ONLY_PROGRESSION_STYLES = 'onlyProgressionStyles'
    FORMFACTOR_SQUARE = 'formfactor_square'
    FORMFACTOR_RECT1X2 = 'formfactor_rect1x2'
    FORMFACTOR_RECT1X3 = 'formfactor_rect1x3'
    FORMFACTOR_RECT1X4 = 'formfactor_rect1x4'
    FORMFACTOR_RECT1X6 = 'formfactor_rect1x6'


class FilterTypes(IntEnum):
    HISTORIC = 1
    INVENTORY = 2
    APPLIED = 3
    USED_UP = 4
    EDITABLE_STYLES = 5
    PROGRESSION = 6
    FORMFACTORS = 7
    PROGRESSION_STYLE = 8
    FAVORITE = 9
    SALE = 10


class FilterAliases(Enum):
    HISTORIC = 'historic'
    NON_HISTORIC = 'nonHistoric'
    FANTASTICAL = 'fantastical'
    EDITABLE_STYLES = 'editableStyles'
    NON_EDITABLE_STYLES = 'nonEditableStyles'
    FORMFACTOR_SQUARE = 'formfactor_square'
    FORMFACTOR_RECT1X2 = 'formfactor_rect1x2'
    FORMFACTOR_RECT1X3 = 'formfactor_rect1x3'
    FORMFACTOR_RECT1X4 = 'formfactor_rect1x4'
    FORMFACTOR_RECT1X6 = 'formfactor_rect1x6'
    LOCKED = 'locked'


FILTER_TYPES_MAPPING = {CarouselFilterTypes.HISTORIC: FilterTypes.HISTORIC,
 CarouselFilterTypes.NON_HISTORIC: FilterTypes.HISTORIC,
 CarouselFilterTypes.FANTASTICAL: FilterTypes.HISTORIC,
 CarouselFilterTypes.INVENTORY: FilterTypes.INVENTORY,
 CarouselFilterTypes.APPLIED: FilterTypes.APPLIED,
 CarouselFilterTypes.FAVORITE: FilterTypes.FAVORITE,
 CarouselFilterTypes.ON_ANOTHER_VEH: FilterTypes.USED_UP,
 CarouselFilterTypes.ONLY_PROGRESSION_DECALS: FilterTypes.PROGRESSION,
 CarouselFilterTypes.ONLY_EDITABLE_STYLES: FilterTypes.EDITABLE_STYLES,
 CarouselFilterTypes.ONLY_NON_EDITABLE_STYLES: FilterTypes.EDITABLE_STYLES,
 CarouselFilterTypes.ONLY_PROGRESSION_STYLES: FilterTypes.PROGRESSION_STYLE,
 CarouselFilterTypes.SALE: FilterTypes.SALE,
 CarouselFilterTypes.FORMFACTOR_SQUARE: FilterTypes.FORMFACTORS,
 CarouselFilterTypes.FORMFACTOR_RECT1X2: FilterTypes.FORMFACTORS,
 CarouselFilterTypes.FORMFACTOR_RECT1X3: FilterTypes.FORMFACTORS,
 CarouselFilterTypes.FORMFACTOR_RECT1X4: FilterTypes.FORMFACTORS,
 CarouselFilterTypes.FORMFACTOR_RECT1X6: FilterTypes.FORMFACTORS}
FILTER_ALIAS_MAPPING = {CarouselFilterTypes.HISTORIC: FilterAliases.HISTORIC,
 CarouselFilterTypes.NON_HISTORIC: FilterAliases.NON_HISTORIC,
 CarouselFilterTypes.FANTASTICAL: FilterAliases.FANTASTICAL,
 CarouselFilterTypes.ONLY_EDITABLE_STYLES: FilterAliases.EDITABLE_STYLES,
 CarouselFilterTypes.ONLY_NON_EDITABLE_STYLES: FilterAliases.NON_EDITABLE_STYLES,
 CarouselFilterTypes.FORMFACTOR_SQUARE: FilterAliases.FORMFACTOR_SQUARE,
 CarouselFilterTypes.FORMFACTOR_RECT1X2: FilterAliases.FORMFACTOR_RECT1X2,
 CarouselFilterTypes.FORMFACTOR_RECT1X3: FilterAliases.FORMFACTOR_RECT1X3,
 CarouselFilterTypes.FORMFACTOR_RECT1X4: FilterAliases.FORMFACTOR_RECT1X4,
 CarouselFilterTypes.FORMFACTOR_RECT1X6: FilterAliases.FORMFACTOR_RECT1X6}

class AvailabilityFilterState(object):
    ALL = 'all'
    INVENTORY = 'inventory'
    SALE = 'sale'


def getStructureList(ctx, carouselDP):
    structure = [StructureBlockType.AVAILABILITY, StructureBlockType.SPECIAL, StructureBlockType.HISTORIC]
    if ctx.tabId == CustomizationTabs.PROJECTION_DECALS:
        structure.append(StructureBlockType.FORMFACTOR)
    if ctx.tabId in CustomizationTabs.STYLES_ALL:
        structure.append(StructureBlockType.EDITABLE)
    if ctx.isItemsOnAnotherVeh:
        structure.append(StructureBlockType.ONANOTHERVEH)
    if len(carouselDP.getItemsData().groups) > 1:
        structure.extend((StructureBlockType.GROUPS, StructureBlockType.SORTING))
    if ctx.isProgressiveItemsExist:
        structure.append(StructureBlockType.PROGRESSIONDECALS)
    return structure
