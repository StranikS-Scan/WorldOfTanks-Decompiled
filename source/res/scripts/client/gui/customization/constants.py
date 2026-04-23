# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/customization/constants.py
from enum import IntEnum

class CustomizationModes(object):
    NONE = -1
    CUSTOM = 1
    STYLED_2D = 2
    STYLED_3D = 3
    EDITABLE_STYLE = 4
    STYLED = (STYLED_2D, STYLED_3D)
    ALL_STYLES = (STYLED_2D, STYLED_3D, EDITABLE_STYLE)
    ALL = (CUSTOM,
     STYLED_2D,
     STYLED_3D,
     EDITABLE_STYLE)


class CustomizationModeSource(IntEnum):
    UNDEFINED = -1
    BOTTOM_PANEL = 1
    CAROUSEL = 2
    CONTEXT_MENU = 3
    PROPERTIES_SHEET = 4
    NOTIFICATION = 5
    REWARD_WINDOW = 6


INVALID_ID = -1
