# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/windows/__init__.py
from frameworks.wulf import WindowFlags
from gui.impl.windows.content_menu_id import ContextMenuID
from gui.impl.windows.context_menu_window import ContextMenuContent, ContextMenuWindow
from gui.impl.windows.popup_window import PopUpWindow
from gui.impl.windows.main_window import MainWindow
from gui.impl.windows.service_window import ServiceWindow
from gui.impl.windows.standard_window import StandardWindow
from gui.impl.windows.tooltip_window import SimpleToolTipWindow, ToolTipWindow
from gui.impl.windows.window_view import WindowView

class UserWindowFlags(WindowFlags):
    LOBBY_MAIN_WND = WindowFlags.MAIN_WINDOW | 65536
    BATTLE_MAIN_WND = WindowFlags.MAIN_WINDOW | 131072
    USER_TYPES_MASK = WindowFlags.WINDOW_TYPE_MASK | 983040


__all__ = ('ContextMenuID', 'ContextMenuContent', 'ContextMenuWindow', 'MainWindow', 'ServiceWindow', 'StandardWindow', 'SimpleToolTipWindow', 'ToolTipWindow', 'PopUpWindow', 'WindowView')
