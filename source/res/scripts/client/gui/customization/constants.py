# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/customization/constants.py


class CustomizationModes(object):
    CUSTOM = 1
    STYLE_2D = 2
    STYLE_3D = 3
    STYLE_2D_EDITABLE = 4
    ALL = (CUSTOM,
     STYLE_2D,
     STYLE_3D,
     STYLE_2D_EDITABLE)
    BASE = (CUSTOM, STYLE_2D, STYLE_3D)
    BASE_STYLES = (STYLE_2D, STYLE_3D)
    STYLES = BASE_STYLES + (STYLE_2D_EDITABLE,)


class CustomizationModeSource(object):
    UNDEFINED = -1
    BOTTOM_PANEL = 1
    CAROUSEL = 2
    CONTEXT_MENU = 3
    PROPERTIES_SHEET = 4
    NOTIFICATION = 5
    REWARD_WINDOW = 6
