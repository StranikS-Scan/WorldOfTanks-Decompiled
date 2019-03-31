# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/CursorDelegator.py
# Compiled at: 2011-05-10 15:47:16
import BigWorld, GUI
from debug_utils import LOG_DEBUG

class CursorDelegator(object):

    def __init__(self):
        super(CursorDelegator, self).__init__()
        self.__activated = False
        self.__savedMCursorPos = None
        return

    def activateCursor(self):
        if not self.__activated:
            mcursor = GUI.mcursor()
            mcursor.visible = False
            LOG_DEBUG('Cursor activate', mcursor.position)
            BigWorld.setCursor(mcursor)
            self.__activated = True

    def detachCursor(self):
        if self.__activated:
            LOG_DEBUG('Cursor detach')
            BigWorld.setCursor(None)
            self.__activated = False
        return

    def syncMousePosition(self, flash):
        screenWidth, screenHeight = GUI.screenResolution()
        mouseLeft, mouseTop = GUI.mcursor().position
        self.__savedMCursorPos = (mouseLeft, mouseTop)
        x = round((1.0 + mouseLeft) / 2.0 * screenWidth)
        y = round(-(-1.0 + mouseTop) / 2.0 * screenHeight)
        LOG_DEBUG('Sync Scaleform cursor position with BigWorld cursor', x, y)
        flash.call('Cursor.SetPosition', [x, y])

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
