# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/managers/Cursor.py
import GUI
import BigWorld
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui import GUI_CTRL_MODE_FLAG as _CTRL_FLAG
from gui.Scaleform.daapi.view.meta.CursorMeta import CursorMeta
from gui.Scaleform.framework.entities.View import View
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import GameEvent

class Cursor(CursorMeta, View):
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
        super(Cursor, self).__init__()
        self.__isActivated = False
        self.__savedMCursorPos = None
        return

    def attachCursor(self, flags=_CTRL_FLAG.GUI_ENABLED):
        """
        Mouse cursor activate. Gets mouse cursor, it hide and activate. Client
        uses Scaleform custom mouse cursor - movie clip witch receive notifications
        about mouse movement, left mouse button press and mouse wheel events.
        :param flags: determine whether Flash cursor should be shown
        """
        assert flags & _CTRL_FLAG.CURSOR_ATTACHED, 'Flag CURSOR_ATTACHED is not defined'
        if flags & _CTRL_FLAG.CURSOR_VISIBLE > 0:
            self.show()
        else:
            self.hide()
        if not self.__isActivated:
            mcursor = GUI.mcursor()
            mcursor.visible = False
            mouseLeft, mouseTop = mcursor.position
            self.__saveDeviceMousePosition(mouseLeft, mouseTop)
            LOG_DEBUG('Cursor is attached')
            BigWorld.setCursor(mcursor)
            self.__isActivated = True

    def detachCursor(self):
        """
        Mouse cursor detach and give control camera.
        """
        if self.__isActivated:
            LOG_DEBUG('Cursor is detached')
            BigWorld.setCursor(None)
            self.__isActivated = False
        self.hide()
        BigWorld.callback(0.0, self.__restoreDeviceMousePosition)
        return

    def syncCursor(self, flags=_CTRL_FLAG.GUI_ENABLED):
        if flags & _CTRL_FLAG.CURSOR_ATTACHED > 0:
            self.attachCursor(flags=flags)
        elif flags & _CTRL_FLAG.CURSOR_DETACHED > 0:
            self.detachCursor()

    def show(self):
        if self.flashObject is not None:
            self.__setSFMousePosition()
            self.as_showCursorS()
            self.fireEvent(GameEvent(GameEvent.SHOW_CURSOR), scope=EVENT_BUS_SCOPE.GLOBAL)
        else:
            LOG_ERROR(self.__DAAPI_ERROR)
        return

    def hide(self):
        if self.flashObject is not None:
            self.as_hideCursorS()
            self.fireEvent(GameEvent(GameEvent.HIDE_CURSOR), scope=EVENT_BUS_SCOPE.GLOBAL)
        else:
            LOG_ERROR(self.__DAAPI_ERROR)
        return

    def setCursorForced(self, cursor):
        self.as_setCursorS(cursor)

    def _populate(self):
        super(Cursor, self)._populate()
        flags = self.app.ctrlModeFlags
        if flags & _CTRL_FLAG.CURSOR_ATTACHED > 0:
            self.attachCursor(flags=flags)
        else:
            self.detachCursor()

    def __setSFMousePosition(self):
        """
        Sync Scaleform cursor position with BigWorld cursor position. It required
        when: show cursor in battle or load another flash with cursor.
        """
        screenWidth, screenHeight = GUI.screenResolution()
        mouseLeft, mouseTop = GUI.mcursor().position
        self.__saveDeviceMousePosition(mouseLeft, mouseTop)
        self.flashObject.x = round((1.0 + mouseLeft) / 2.0 * screenWidth)
        self.flashObject.y = round(-(-1.0 + mouseTop) / 2.0 * screenHeight)

    def __saveDeviceMousePosition(self, mouseLeft, mouseTop):
        """
        Just memorize cursor position to restore it when necessary.
        :param mouseLeft: x position
        :param mouseTop: y position
        """
        self.__savedMCursorPos = (mouseLeft, mouseTop)

    def __restoreDeviceMousePosition(self):
        """
        Restore GUI.mcursor position previously saved in syncMousePosition (WOTD-2262).
        This is required because CursorCamera will not change mcursor.position until
        any mouse movement after cursor is hidden and keeps wrong BigWorld.target etc.
        """
        if self.__savedMCursorPos is not None:
            GUI.mcursor().position = self.__savedMCursorPos
            self.__savedMCursorPos = None
        return
