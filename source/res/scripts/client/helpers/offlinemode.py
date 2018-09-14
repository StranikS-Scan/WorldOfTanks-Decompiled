# Embedded file name: scripts/client/helpers/OfflineMode.py
import BigWorld
import AvatarInputHandler
from AvatarInputHandler.VideoCamera import VideoCamera
from AvatarInputHandler import mathUtils
import GUI
import Keys
import Math
import ResMgr
import sys
import math
from functools import partial
from constants import IS_DEVELOPMENT
g_offlineModeEnabled = False
g_gui = None
g_videoCamera = None
INSTRUCTIONS = '\nHave Fun!\n'

def enabled():
    global g_offlineModeEnabled
    return g_offlineModeEnabled


def onStartup():
    if not IS_DEVELOPMENT:
        return False
    try:
        idx = sys.argv.index('offline')
        offlineSpace = sys.argv[idx + 1]
        launch(offlineSpace)
        return True
    except ValueError as IndexError:
        return False


def _clearGUI():
    global g_gui
    if g_gui is not None:
        GUI.delRoot(g_gui)
        g_gui = None
    return


def _displayGUI(spaceName):
    global g_gui
    _clearGUI()
    g_gui = GUI.Text("Entering offline space '%s'...\n%s" % (spaceName, INSTRUCTIONS))
    g_gui.multiline = True
    g_gui.horizontalAnchor = 'CENTER'
    GUI.addRoot(g_gui)


def _offlineLoadCheck():
    if BigWorld.spaceLoadStatus() > 0.5:
        BigWorld.worldDrawEnabled(True)
        _clearGUI()
    else:
        BigWorld.callback(1.0, _offlineLoadCheck)


g_spaceID = 0
g_avatar = None

class FakeAvatar:
    spaceID = property(lambda self: BigWorld.camera().spaceID)


g_fakeAvatar = FakeAvatar()

def launch(spaceName):
    global g_offlineModeEnabled
    global g_spaceID
    global g_videoCamera
    print 'Entering offline space', spaceName
    BigWorld.clearAllSpaces()
    BigWorld.worldDrawEnabled(False)
    _displayGUI(spaceName)
    g_spaceID = BigWorld.createSpace()
    BigWorld.addSpaceGeometryMapping(g_spaceID, None, spaceName)
    BigWorld.setCursor(GUI.mcursor())
    GUI.mcursor().visible = False
    GUI.mcursor().clipped = True
    g_offlineModeEnabled = True
    BigWorld.callback(1.0, _offlineLoadCheck)
    rootSection = ResMgr.openSection(AvatarInputHandler._INPUT_HANDLER_CFG)
    videoSection = rootSection['videoMode']
    videoCameraSection = videoSection['camera']
    g_videoCamera = VideoCamera(videoCameraSection)
    g_videoCamera.enable(camMatrix=mathUtils.createTranslationMatrix((0.0, 0.0, 0.0)))
    BigWorld.camera().spaceID = g_spaceID
    import game
    game.handleKeyEvent = handleKeyEvent
    game.handleMouseEvent = handleMouseEvent
    BigWorld.player = lambda : g_fakeAvatar
    return


def handleKeyEvent(event):
    if not g_offlineModeEnabled or not BigWorld.camera():
        return False
    g_videoCamera.handleKeyEvent(event.key, event.isKeyDown())
    return False


def handleMouseEvent(event):
    if not g_offlineModeEnabled or not BigWorld.camera():
        return False
    if GUI.mcursor().visible:
        return False
    g_videoCamera.handleMouseEvent(event.dx, event.dy, event.dz)
    return False
