# Embedded file name: scripts/client/gui/Cursor.py
import BigWorld
import GUI
import Math
from debug_utils import *
from bwdebug import WARNING_MSG
_mouseModeRefCount = 0

def showCursor(show):
    global _mouseModeRefCount
    if show:
        _mouseModeRefCount += 1
        if _mouseModeRefCount > 0:
            BigWorld.setCursor(GUI.mcursor())
            GUI.mcursor().visible = True
    else:
        _mouseModeRefCount -= 1
        if _mouseModeRefCount == 0:
            BigWorld.setCursor(BigWorld.dcursor())
            GUI.mcursor().visible = False
        if _mouseModeRefCount < 0:
            WARNING_MSG('mouseModeRefCount is negative!')


def forceShowCursor(show):
    if show:
        BigWorld.setCursor(GUI.mcursor())
        GUI.mcursor().visible = True
    else:
        BigWorld.setCursor(BigWorld.dcursor())
        GUI.mcursor().visible = False


def pixelPosition():
    screenWidth, screenHeight = GUI.screenResolution()
    mouseLeft, mouseTop = GUI.mcursor().position
    width = round((1.0 + mouseLeft) / 2.0 * screenWidth)
    height = round(-(-1.0 + mouseTop) / 2.0 * screenHeight)
    return (width, height)
