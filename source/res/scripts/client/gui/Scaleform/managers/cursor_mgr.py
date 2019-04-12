# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/managers/cursor_mgr.py
import logging
import GUI
import BigWorld
from gui import GUI_CTRL_MODE_FLAG as _CTRL_FLAG
from gui.Scaleform.framework.entities.abstract.CursorManagerMeta import CursorManagerMeta
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
_logger = logging.getLogger(__name__)

class CursorManager(CursorManagerMeta):
    ARROW = 'arrow'
    AUTO = 'auto'
    BUTTON = 'button'
    HAND = 'hand'
    IBEAM = 'ibeam'
    ROTATE = 'rotate'
    RESIZE = 'resize'
    MOVE = 'move'
    DRAG_OPEN = 'dragopen'
    DRAG_CLOSE = 'dragclose'
    __DAAPI_ERROR = 'flashObject is Python Cursor class can`t be None!'

    def __init__(self):
        super(CursorManager, self).__init__()
        self.__savedMCursorPos = None
        return

    def attachCursor(self, flags=_CTRL_FLAG.GUI_ENABLED):
        if flags & _CTRL_FLAG.CURSOR_VISIBLE > 0:
            self.show()
        else:
            self.hide()
        mcursor = GUI.mcursor()
        if not mcursor.active:
            mouseLeft, mouseTop = mcursor.position
            self.__saveDeviceMousePosition(mouseLeft, mouseTop)
            _logger.debug('Cursor is attached')
            BigWorld.setCursor(mcursor)

    def detachCursor(self):
        mcursor = GUI.mcursor()
        if mcursor.active:
            _logger.debug('Cursor is detached')
            if self.__savedMCursorPos is not None:
                left, top = self.__savedMCursorPos
                GUI.syncMousePosition(left, top)
            BigWorld.setCursor(None)
        self.hide()
        BigWorld.callback(0.0, self.__restoreDeviceMousePosition)
        return

    def syncCursor(self, flags=_CTRL_FLAG.GUI_ENABLED):
        if flags & _CTRL_FLAG.CURSOR_ATTACHED > 0:
            self.attachCursor(flags=flags)
        elif flags & _CTRL_FLAG.CURSOR_DETACHED > 0:
            self.detachCursor()

    def show(self):
        GUI.mcursor().visible = True
        if self.flashObject is not None:
            self.__setSFMousePosition()
            self.fireEvent(GameEvent(GameEvent.SHOW_CURSOR), scope=EVENT_BUS_SCOPE.GLOBAL)
        else:
            _logger.error(self.__DAAPI_ERROR)
        return

    def hide(self):
        GUI.mcursor().visible = False
        if self.flashObject is not None:
            self.fireEvent(GameEvent(GameEvent.HIDE_CURSOR), scope=EVENT_BUS_SCOPE.GLOBAL)
        else:
            _logger.error(self.__DAAPI_ERROR)
        return

    def setCursorForced(self, cursor):
        self.as_setCursorS(cursor)

    def _populate(self):
        super(CursorManager, self)._populate()
        if self.app is not None:
            flags = self.app.ctrlModeFlags
            if flags & _CTRL_FLAG.CURSOR_ATTACHED > 0:
                self.attachCursor(flags=flags)
            else:
                self.detachCursor()
        return

    def __setSFMousePosition(self):
        mouseLeft, mouseTop = GUI.mcursor().position
        self.__saveDeviceMousePosition(mouseLeft, mouseTop)

    def __saveDeviceMousePosition(self, mouseLeft, mouseTop):
        self.__savedMCursorPos = (mouseLeft, mouseTop)

    def __restoreDeviceMousePosition(self):
        if self.__savedMCursorPos is not None:
            GUI.mcursor().position = self.__savedMCursorPos
            self.__savedMCursorPos = None
        return

    def resetMousePosition(self):
        GUI.mcursor().position = (0.0, 0.0)
        self.__saveDeviceMousePosition(0.0, 0.0)
        GUI.syncMousePosition(0.0, 0.0)
