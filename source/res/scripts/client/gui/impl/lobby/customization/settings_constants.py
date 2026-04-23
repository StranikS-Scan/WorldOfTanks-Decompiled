# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/customization/settings_constants.py
from shared_utils import getFullClassName
from skeletons.account_helpers.settings_repository import SettingsSerializable
APPLY_TO_ALL_SEASONS_ENABLED = 'applyToAllSeasonsEnabled'
CAROUSEL_ARROWS_HINT_SHOWN_FIELD = 'isCarouselsArrowsHintShown'
CUSTOMIZATION_STYLE_ITEMS_VISITED = 'CustomizationStyleItemsVisited'
IS_CUSTOMIZATION_INTRO_VIEWED = 'isCustomizationIntroViewed'
IS_AUTO_RENT_ENABLED_SET = 'isAutoRentEnabledSet'
AUTO_RENT_GLOBAL_CD = 0

class CustomizationFilter(object):
    CUSTOMIZATION_FILTER = 'customizationFilter'
    CAMOUFLAGE_GROUP = 'camouflageGroup'
    PAINTS_GROUP = 'paintsGroup'
    PROJECTION_DECALS_GROUP = 'projectionDecalsGroup'
    EMBLEMS_GROUP = 'emblemsGroup'
    INSCRIPTIONS_GROUP = 'inscriptionsGroup'
    STYLES_2D_GROUP = 'styles2dGroup'
    STYLES_3D_GROUP = 'styles3dGroup'
    DISPLAY_GROUP = 'displayGroup'
    FORMFACTOR_SQUARE = 'formfactor_square'
    FORMFACTOR_RECT1X2 = 'formfactor_rect1x2'
    FORMFACTOR_RECT1X3 = 'formfactor_rect1x3'
    FORMFACTOR_RECT1X4 = 'formfactor_rect1x4'
    FORMFACTOR_RECT1X6 = 'formfactor_rect1x6'
    HISTORIC = 'historic'
    NON_HISTORIC = 'nonHistoric'
    FANTASTICAL = 'fantastical'
    INVENTORY = 'inventory'
    SALE = 'sale'
    APPLIED = 'applied'
    FAVORITE = 'favorite'
    ON_ANOTHER_VEH = 'onAnotherVeh'
    ONLY_PROGRESSION_DECALS = 'onlyProgressionDecals'
    ONLY_EDITABLE_STYLES = 'onlyEditableStyles'
    ONLY_NON_EDITABLE_STYLES = 'onlyNonEditableStyles'
    ONLY_PROGRESSION_STYLES = 'onlyProgressionStyles'


def getCustomizationFilterDefaults():
    return {CustomizationFilter.CAMOUFLAGE_GROUP: -1,
     CustomizationFilter.PAINTS_GROUP: -1,
     CustomizationFilter.PROJECTION_DECALS_GROUP: -1,
     CustomizationFilter.EMBLEMS_GROUP: -1,
     CustomizationFilter.INSCRIPTIONS_GROUP: -1,
     CustomizationFilter.STYLES_2D_GROUP: -1,
     CustomizationFilter.STYLES_3D_GROUP: -1,
     CustomizationFilter.DISPLAY_GROUP: 0,
     CustomizationFilter.FORMFACTOR_SQUARE: False,
     CustomizationFilter.FORMFACTOR_RECT1X2: False,
     CustomizationFilter.FORMFACTOR_RECT1X3: False,
     CustomizationFilter.FORMFACTOR_RECT1X4: False,
     CustomizationFilter.FORMFACTOR_RECT1X6: False,
     CustomizationFilter.HISTORIC: False,
     CustomizationFilter.NON_HISTORIC: False,
     CustomizationFilter.FANTASTICAL: False,
     CustomizationFilter.INVENTORY: False,
     CustomizationFilter.APPLIED: False,
     CustomizationFilter.SALE: False,
     CustomizationFilter.FAVORITE: False,
     CustomizationFilter.ON_ANOTHER_VEH: False,
     CustomizationFilter.ONLY_PROGRESSION_DECALS: False,
     CustomizationFilter.ONLY_EDITABLE_STYLES: False,
     CustomizationFilter.ONLY_NON_EDITABLE_STYLES: False,
     CustomizationFilter.ONLY_PROGRESSION_STYLES: False}


class CustomizationSettingsSerializable(SettingsSerializable):

    @classmethod
    def getSettingsID(cls):
        return getFullClassName(CustomizationSettingsSerializable)
