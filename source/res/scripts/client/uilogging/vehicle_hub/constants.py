# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/vehicle_hub/constants.py
from enum import Enum
TIME_LIMIT = 2

class Features(str, Enum):
    ARMOR_INSPECTOR = 'armor_inspector'


class Tabs(str, Enum):
    ARMOR_TAB = 'armor_tab'


class LogItems(str, Enum):
    VIDEO = 'video_button'
    ARMOR_TOOLTIP = 'armor_tooltip'
    LEGEND = 'legend'


class LogActions(str, Enum):
    OPEN = 'open'
    CLOSE = 'close'
    CLICK = 'click'
    TOOLTIP_ACTION = 'watched'
    EXPAND = 'expand'
    COLLAPSE = 'collapse'
