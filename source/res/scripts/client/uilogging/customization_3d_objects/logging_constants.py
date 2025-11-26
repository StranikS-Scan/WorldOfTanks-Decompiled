# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/customization_3d_objects/logging_constants.py
from enum import Enum
from gui.filters.carousel_filter import FILTER_KEYS
from gui.Scaleform.daapi.view.lobby.customization.shared import CustomizationTabs, CustomizationModes
from items.components.c11n_constants import AttachmentType
FEATURE = 'customization_3d_objects'

class CustomizationViewKeys(Enum):
    CUSTOMIZATION_BOTTOM_PANEL = 'customization_bottom_panel'
    HANGAR = 'hangar'
    EXTERIOR = 'exterior_view'
    ATTACHMENTS_VIDEO = '3d_attachments_video_view'
    VEHICLES_LIST = 'vehicles_list_view'
    CUSTOMIZATION_HANGAR_3D_SCENE = 'customization_hangar_3d_scene'
    CUSTOMIZATION_FILTER_POPOVER = 'customization_filter_popover'
    VEHICLE_CAROUSEL = 'vehicle_carousel'
    VEHICLE_FILTER = 'vehicle_filter'
    CUSTOMIZATION_RARITY_REWARD_VIEW = 'customization_rarity_reward_view'


class CustomizationActions(Enum):
    CLICK = 'click'
    OPEN = 'open'
    CLOSE = 'close'


class CustomizationButtons(Enum):
    TO_THE_VIDEO = 'to_the_video_button'
    TO_EXTERIOR = 'to_exterior_button'
    TO_GARAGE = 'to_garage_button'
    VEHICLE_FILTER = 'vehicle_filter_button'
    EXTERIOR = 'exterior_button'
    VEHICLES_LIST = 'vehicles_list_button'


class CustomizationChamomileButtons(object):
    ROTATE = 'rotate_button'
    MOVE = 'move_button'
    REMOVE = 'remove_button'
    CLOSE = 'close_button'
    SCALE_1X = '1x_scale_button'
    SCALE_2X = '2x_scale_button'
    SCALE_3X = '3x_scale_button'
    ALL_SCALE = (SCALE_1X, SCALE_2X, SCALE_3X)


class CustomizationCarouselStates(Enum):
    TOTAL_ZERO_STATE = 'total_zero_state'
    VEHICLE_ZERO_STATE = 'vehicle_zero_state'
    NON_ZERO_STATE = 'non_zero_state'
    NONE = None


class CustomizationTutorialStates(Enum):
    IS_NOT_TUTORIAL = 'is_not_tutorial'
    IS_TUTORIAL = 'is_tutorial'


class CustomizationCarouselTabs(Enum):
    PAINTS = 'paints_tab'
    CAMOUFLAGES = 'camouflage_tab'
    DECALS = 'decals_tab'
    EMBLEMS = 'emblems_tab'
    INSCRIPTIONS = 'inscriptions_tab'
    EFFECTS = 'effects_tab'
    STYLES_2D = '2d_styles_tab'
    STYLES_3D = '3d_styles_tab'
    ATTACHMENTS = '3d_attachments_tab'
    STAT_TRACKERS = 'statTracker_tab'


class CustomizationCarouselModes(Enum):
    STYLE_3D = '3d_style_mode'
    STYLE_2D = '2d_style_mode'
    CUSTOM = 'custom_mode'
    EDITABLE_STYLE = 'editable_style_mode'


class VehicleCustomizationFilterButtons(Enum):
    OWN_3D_STYLE = 'vehicle_3d_style_filter_button'
    CAN_INSTALL_ATTACHMENTS = 'vehicle_3d_attachment_filter_button'


class CustomizationAttachmentSlots(Enum):
    UNIVERSAL = '3d_attachment_universal_anchor'
    GUN_MANTLET = '3d_attachment_gun_mantlet_anchor'
    TURRET = '3d_attachment_turret_anchor'
    GUN = '3d_attachment_gun_anchor'


class CustomizationFilterButtons(Enum):
    FANTASTICAL = 'fictional_button'
    NON_HISTORIC = 'non_historic_button'
    HISTORIC = 'historic_button'
    IN_DEPOT = 'in_depot_button'
    APPLIED = 'applied_button'
    RESET_FILTER = 'reset_filter_button'
    RARITY_TEMPLATE = '{}_button'
    ALL_GROUPS = 'all_groups'
    GROUP_TEMPLATE = '{}_button'


class CustomizationFilterTypes(Enum):
    GROUPS = 'groups'
    RARITY = 'rarity'
    PRIMARY = 'primary'


CUSTOMIZATION_CAROUSEL_TAB_MAPPING = {CustomizationTabs.PAINTS: CustomizationCarouselTabs.PAINTS,
 CustomizationTabs.CAMOUFLAGES: CustomizationCarouselTabs.CAMOUFLAGES,
 CustomizationTabs.PROJECTION_DECALS: CustomizationCarouselTabs.DECALS,
 CustomizationTabs.EMBLEMS: CustomizationCarouselTabs.EMBLEMS,
 CustomizationTabs.INSCRIPTIONS: CustomizationCarouselTabs.INSCRIPTIONS,
 CustomizationTabs.MODIFICATIONS: CustomizationCarouselTabs.EFFECTS,
 CustomizationTabs.STYLES_2D: CustomizationCarouselTabs.STYLES_2D,
 CustomizationTabs.STYLES_3D: CustomizationCarouselTabs.STYLES_3D,
 CustomizationTabs.ATTACHMENTS: CustomizationCarouselTabs.ATTACHMENTS,
 CustomizationTabs.STAT_TRACKERS: CustomizationCarouselTabs.STAT_TRACKERS}
CUSTOMIZATION_CAROUSEL_MODE_MAPPING = {CustomizationModes.STYLE_3D: CustomizationCarouselModes.STYLE_3D,
 CustomizationModes.STYLE_2D: CustomizationCarouselModes.STYLE_2D,
 CustomizationModes.CUSTOM: CustomizationCarouselModes.CUSTOM,
 CustomizationModes.STYLE_2D_EDITABLE: CustomizationCarouselModes.EDITABLE_STYLE}
VEHICLE_CUSTOMIZATION_FILTER_MAPPING = {FILTER_KEYS.OWN_3D_STYLE: VehicleCustomizationFilterButtons.OWN_3D_STYLE,
 FILTER_KEYS.CAN_INSTALL_ATTACHMENTS: VehicleCustomizationFilterButtons.CAN_INSTALL_ATTACHMENTS}
ATTACHMENT_TYPE_MAPPING = {AttachmentType.UNIVERSAL: CustomizationAttachmentSlots.UNIVERSAL,
 AttachmentType.GUN_MANTLET: CustomizationAttachmentSlots.GUN_MANTLET,
 AttachmentType.TURRET: CustomizationAttachmentSlots.TURRET,
 AttachmentType.GUN: CustomizationAttachmentSlots.GUN}
