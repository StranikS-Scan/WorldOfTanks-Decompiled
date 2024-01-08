# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/frameworks/wulf/gui_constants.py
from enum import Enum
from shared_utils import CONST_CONTAINER

class ViewStatus(CONST_CONTAINER):
    UNDEFINED = 0
    CREATED = 1
    LOADING = 2
    LOADED = 3
    DESTROYING = 4
    DESTROYED = 5


class ShowingStatus(Enum):
    SHOWING = 0
    SHOWN = 1
    HIDING = 2
    HIDDEN = 3


class ViewFlags(CONST_CONTAINER):
    VIEW = 1
    WINDOW_DECORATOR = 2
    POP_OVER_DECORATOR = 4 | WINDOW_DECORATOR
    MAIN_VIEW = 8
    OLD_STYLE_VIEW = 32
    LOBBY_SUB_VIEW = 4096 | OLD_STYLE_VIEW
    LOBBY_TOP_SUB_VIEW = 4352 | OLD_STYLE_VIEW
    VIEW_TYPE_MASK = 65520

    @classmethod
    def getViewType(cls, flags):
        flags = flags & ViewFlags.VIEW_TYPE_MASK
        if flags == ViewFlags.OLD_STYLE_VIEW:
            return WindowLayer.VIEW
        if flags == ViewFlags.LOBBY_SUB_VIEW:
            return WindowLayer.SUB_VIEW
        return WindowLayer.TOP_SUB_VIEW if flags == ViewFlags.LOBBY_TOP_SUB_VIEW else None


class ViewEventType(CONST_CONTAINER):
    UNDEFINED = 0
    TOOLTIP = 1
    POP_OVER = 2
    CONTEXT_MENU = 4
    DROP_DOWN = 8


class WindowStatus(CONST_CONTAINER):
    UNDEFINED = 0
    CREATED = 1
    LOADING = 2
    LOADED = 3
    DESTROYING = 4
    DESTROYED = 5


class WindowFlags(CONST_CONTAINER):
    UNDEFINED = 0
    WINDOW = 1
    GLOBAL_WINDOW = 2
    MAIN_WINDOW = 4 | GLOBAL_WINDOW
    DIALOG = 16 | WINDOW
    POP_OVER = 32 | WINDOW
    TOOLTIP = 48 | WINDOW
    CONTEXT_MENU = 64 | WINDOW
    DROP_DOWN = 80 | WINDOW
    SERVICE_WINDOW = 96 | GLOBAL_WINDOW
    WAITING = 112 | GLOBAL_WINDOW
    WINDOW_TYPE_MASK = 255
    WINDOW_MINIMIZED = 256
    WINDOW_MAXIMIZED = 512
    WINDOW_FULLSCREEN = 1024
    WINDOW_STATE_MASK = 3840
    WINDOW_MODAL = 4096
    APP_MODAL = 8192
    WINDOW_MODALITY_MASK = 12288


class WindowLayer(CONST_CONTAINER):
    UNDEFINED = 0
    ROOT = 1
    HIDDEN_SERVICE_LAYOUT = 2
    MARKER = 3
    VIEW = 4
    SUB_VIEW = 5
    TOP_SUB_VIEW = 6
    WINDOW = 7
    FULLSCREEN_WINDOW = 8
    SYSTEM_MESSAGE = 9
    TOP_WINDOW = 10
    OVERLAY = 11
    IME = 12
    SERVICE_LAYOUT = 13
    TOOLTIP = 14
    CURSOR = 15
    WAITING = 16


class PropertyType(CONST_CONTAINER):
    NONE = 0
    NUMBER = 1
    REAL = 2
    BOOL = 3
    STRING = 4
    VIEW_MODEL = 5
    VIEW = 6
    RESOURCE = 7
    ARRAY = 8


class PositionAnchor(CONST_CONTAINER):
    LEFT = 0
    RIGHT = 1
    TOP = 2
    BOTTOM = 3


class NumberFormatType(CONST_CONTAINER):
    INTEGRAL = 0
    GOLD = 1


class RealFormatType(CONST_CONTAINER):
    FRACTIONAL = 0
    WO_ZERO_DIGITS = 1


class TimeFormatType(CONST_CONTAINER):
    SHORT_FORMAT = 0
    LONG_FORMAT = 1


class DateFormatType(CONST_CONTAINER):
    SHORT_FORMAT = 0
    LONG_FORMAT = 1
    YEAR_MONTH = 2


class CaseType(CONST_CONTAINER):
    UPPERCASE = 0
    LOWERCASE = 1


class ChildFlags(CONST_CONTAINER):
    EMPTY = 0
    AUTO_DESTROY = 1
