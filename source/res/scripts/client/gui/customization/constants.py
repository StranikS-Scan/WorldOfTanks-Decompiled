# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/customization/constants.py


class CustomizationModes(object):
    NONE = -1
    CUSTOM = 1
    STYLED = 2
    EDITABLE_STYLE = 3
    ALL = (CUSTOM, STYLED, EDITABLE_STYLE)


class CustomizationModeSource(object):
    UNDEFINED = -1
    BOTTOM_PANEL = 1
    CAROUSEL = 2
    CONTEXT_MENU = 3
    PROPERTIES_SHEET = 4
    NOTIFICATION = 5
    REWARD_WINDOW = 6
