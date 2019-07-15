# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/frameworks/wulf/gui_constants.py
from shared_utils import CONST_CONTAINER

class ViewStatus(CONST_CONTAINER):
    UNDEFINED = 0
    CREATED = 1
    LOADING = 2
    LOADED = 3
    DESTROYING = 4
    DESTROYED = 5


class ViewFlags(CONST_CONTAINER):
    VIEW = 1
    WINDOW_DECORATOR = 2
    POP_OVER_DECORATOR = 4 | WINDOW_DECORATOR
    COMPONENT = 16
    OLD_STYLE_VIEW = 32
    MARKER_VIEW = 256 | OLD_STYLE_VIEW
    WINDOW_VIEW = 512 | OLD_STYLE_VIEW
    BROWSER_VIEW = 768 | OLD_STYLE_VIEW
    TOP_WINDOW_VIEW = 1024 | OLD_STYLE_VIEW
    COMPONENT_VIEW = 1280 | OLD_STYLE_VIEW
    OVERLAY_VIEW = 1536 | OLD_STYLE_VIEW
    SERVICE_LAYOUT_VIEW = 1792 | OLD_STYLE_VIEW
    WAITING_VIEW = 2048 | OLD_STYLE_VIEW
    CURSOR_VIEW = 2304 | OLD_STYLE_VIEW
    LOBBY_SUB_VIEW = 4096 | OLD_STYLE_VIEW
    LOBBY_TOP_SUB_VIEW = 4352 | OLD_STYLE_VIEW
    VIEW_TYPE_MASK = 65520

    @classmethod
    def getViewType(cls, flags):
        from gui.Scaleform.framework import ViewTypes
        flags = flags & ViewFlags.VIEW_TYPE_MASK
        if flags == ViewFlags.VIEW:
            return ViewTypes.INVALID
        if flags == ViewFlags.WINDOW_DECORATOR:
            return ViewTypes.INVALID
        if flags == ViewFlags.COMPONENT:
            return ViewTypes.INVALID
        if flags == ViewFlags.MARKER_VIEW:
            return ViewTypes.MARKER
        if flags == ViewFlags.OLD_STYLE_VIEW:
            return ViewTypes.VIEW
        if flags == ViewFlags.LOBBY_SUB_VIEW:
            return ViewTypes.LOBBY_SUB
        if flags == ViewFlags.LOBBY_TOP_SUB_VIEW:
            return ViewTypes.LOBBY_TOP_SUB
        if flags == ViewFlags.WINDOW_VIEW:
            return ViewTypes.WINDOW
        if flags == ViewFlags.BROWSER_VIEW:
            return ViewTypes.BROWSER
        if flags == ViewFlags.TOP_WINDOW_VIEW:
            return ViewTypes.TOP_WINDOW
        if flags == ViewFlags.COMPONENT_VIEW:
            return ViewTypes.COMPONENT
        if flags == ViewFlags.SERVICE_LAYOUT_VIEW:
            return ViewTypes.SERVICE_LAYOUT
        if flags == ViewFlags.OVERLAY_VIEW:
            return ViewTypes.OVERLAY
        if flags == ViewFlags.WAITING_VIEW:
            return ViewTypes.WAITING
        return ViewTypes.CURSOR if flags == ViewFlags.CURSOR_VIEW else None


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
    BROWSER = 32 | WINDOW
    POP_OVER = 48 | WINDOW
    TOOLTIP = 64 | WINDOW
    CONTEXT_MENU = 80 | WINDOW
    DROP_DOWN = 96 | WINDOW
    OVERLAY = 112 | WINDOW
    SERVICE_WINDOW = 128 | GLOBAL_WINDOW
    WAITING = 144 | GLOBAL_WINDOW
    WINDOW_TYPE_MASK = 255
    WINDOW_MINIMIZED = 256
    WINDOW_MAXIMIZED = 512
    WINDOW_FULL_SCREEN = 768
    WINDOW_STATE_MASK = 3840
    WINDOW_MODAL = 4096
    APP_MODAL = 8192
    WINDOW_MODALITY_MASK = 12288


class WindowLayer(CONST_CONTAINER):
    ROOT = 0
    MARKER = 1
    VIEW = 2
    WINDOW = 3
    BROWSER = 4
    TOP_WINDOW = 5
    COMPONENT = 6
    SERVICE_LAYOUT = 7
    OVERLAY = 8
    WAITING = 9
    CURSOR = 10


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
