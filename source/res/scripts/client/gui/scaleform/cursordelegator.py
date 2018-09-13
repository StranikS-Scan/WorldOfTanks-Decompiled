# Embedded file name: scripts/client/gui/Scaleform/CursorDelegator.py
import BigWorld, GUI
from debug_utils import LOG_DEBUG

class CursorDelegator(object):
    RESIZE = 'RESIZE'
    WAITING = 'WAITING'
    HAND_RIGHT_LEFT = 'HAND_RIGHT_LEFT'
    HAND_ROTATION = 'HAND_ROTATION'
    DRAG_OPEN = 'DRAG_OPEN'
    DRAG_CLOSE = 'DRAG_CLOSE'
    HAND = 'HAND'
    ARROW = 'ARROW'
    IBEAM = 'IBEAM'

    def __init__(self):
        super(CursorDelegator, self).__init__()
        self.__activated = False
        self.__savedMCursorPos = None
        return

    def activateCursor(self):
        if not self.__activated:
            mcursor = GUI.mcursor()
            mcursor.visible = False
            BigWorld.setCursor(mcursor)
            self.__activated = True

    def detachCursor(self):
        if self.__activated:
            BigWorld.setCursor(None)
            self.__activated = False
        return

    def syncMousePosition(self, flash, flashX = None, flashY = None, customCall = False):
        screenWidth, screenHeight = GUI.screenResolution()
        mouseLeft, mouseTop = GUI.mcursor().position
        if not customCall:
            self.__savedMCursorPos = (mouseLeft, mouseTop)
        x = round((1.0 + mouseLeft) / 2.0 * screenWidth) if flashX is None else flashX
        y = round(-(-1.0 + mouseTop) / 2.0 * screenHeight) if flashY is None else flashY
        if flashX is not None and flashY is not None:
            GUI.mcursor().position = (x * 2.0 / screenWidth - 1.0, -y * 2.0 / screenHeight + 1.0)
        flash.call('Cursor.SetPosition', [x, y])
        return

    def setForcedCursor(self, flash, forcedCursor = None):
        flash.call('Cursor.SetForcedCursorType', [forcedCursor])

    def restoreMousePosition(self):
        if self.__savedMCursorPos is not None:
            GUI.mcursor().position = self.__savedMCursorPos
            self.__savedMCursorPos = None
        return

    def setForcedGuiControlMode(self, flash, hold):
        flash.call('Cursor.Hold', [hold])
        if hasattr(BigWorld.player(), 'setForcedGuiControlMode'):
            BigWorld.player().setForcedGuiControlMode(hold)


g_cursorDelegator = CursorDelegator()
