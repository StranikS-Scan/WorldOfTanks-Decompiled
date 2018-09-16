# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/LightingGenerationMode.py
import sys
import math
import BigWorld
import GUI
import Keys
import Math
import ResMgr
import WWISE
from debug_utils import LOG_DEBUG, LOG_ERROR
g_lightGenModeEnabled = False
g_currentMoveRate = 0.5
g_gui = None
g_enableCameraInput = False
MOVE_SPEED_MAX = 200.0
MOVE_SPEED_POW = 2.0
MOVE_SPEED_ADJUST = 0.1
FOV_ADJUST = math.radians(10)
FOV_MIN = math.radians(10)
FOV_MAX = math.radians(160)
SCRIPT_ARG_NAME = 'lightingGen'
MOUSE_TOGGLE_KEYS = [Keys.KEY_ESCAPE, Keys.KEY_LEFTMOUSE]

class CameraTransform:
    matrix = Math.Matrix()

    def __init__(self, matrix):
        self.matrix = matrix

    def apply(self):
        BigWorld.camera().set(self.matrix)


PROFILE_CAMERA_TRANSFORMS_XML_NAME = 'scripts/profile_camera_transforms.xml'
g_cameraTransforms = list()
g_curCameraTransform = 0

def _clampCameraTransformIdx(val):
    global g_cameraTransforms
    val = max(0, val)
    val = min(len(g_cameraTransforms) - 1, val)
    return val


def _loadCameraTransforms():
    rootDS = ResMgr.openSection(PROFILE_CAMERA_TRANSFORMS_XML_NAME)
    if rootDS is not None and rootDS['cameras'] is not None:
        for c in rootDS['cameras'].values():
            c = CameraTransform(c.readMatrix('transform'))
            g_cameraTransforms.append(c)

    else:
        m = Math.Matrix()
        m.lookAt((41, 14, -337), (-0.2, -0.05, 0.97), (0, 1, 0))
        g_cameraTransforms.append(CameraTransform(m))
    return


def _setCameraTransform(idx):
    global g_curCameraTransform
    idx = _clampCameraTransformIdx(idx)
    g_cameraTransforms[idx].apply()
    g_curCameraTransform = idx


def enabled():
    global g_lightGenModeEnabled
    return g_lightGenModeEnabled


def onStartup():
    try:
        LOG_DEBUG(str(sys.argv))
        idx = sys.argv.index(SCRIPT_ARG_NAME)
        manifestFilename = sys.argv[idx + 1]
        LOG_DEBUG(str(manifestFilename))
        spacePath = BigWorld.lightingGenLoadManifest(manifestFilename)
        LOG_DEBUG(str(spacePath))
        if not spacePath:
            LOG_ERROR('error reading manifest: %s' % manifestFilename)
            raise ValueError
        launch(spacePath)
        return True
    except ValueError:
        return False
    except IndexError:
        LOG_ERROR('lightGen mode: Expected lighting manifest file argument ' + "after '%s' command line argument" % SCRIPT_ARG_NAME)
        return False


def _clearGUI():
    global g_gui
    if g_gui is not None:
        GUI.delRoot(g_gui)
        g_gui = None
    return


def _displayGUI(text):
    global g_gui
    _clearGUI()
    g_gui = GUI.Text(text)
    g_gui.multiline = True
    g_gui.horizontalAnchor = 'CENTER'
    GUI.addRoot(g_gui)


def _close():
    LOG_DEBUG('exiting client')
    BigWorld.quit()


def _tick():
    workLeft = BigWorld.isLightingGenRunning()
    if workLeft:
        BigWorld.callback(0.2, _tick)
    else:
        LOG_DEBUG('finished lighting gen work!')
        LOG_DEBUG('shutting down lighting gen systems')
        BigWorld.lightingGenShutdown()
        BigWorld.callback(2.0, _close)


def _startLightingGeneration():
    LOG_DEBUG('triggering lighting gen....')
    BigWorld.lightingGenStart()
    BigWorld.callback(5.0, _tick)


def _offlineLoadCheck():
    if BigWorld.spaceLoadStatus() >= 1.0:
        BigWorld.worldDrawEnabled(True)
        BigWorld.uniprofSceneStart()
        _clearGUI()
        BigWorld.callback(1.0, _startLightingGeneration)
    else:
        BigWorld.callback(1.0, _offlineLoadCheck)


g_spaceID = 0
g_avatar = None

class FakeAvatar:
    spaceID = property(lambda self: BigWorld.camera().spaceID)


g_fakeAvatar = FakeAvatar()

def launch(spaceName):
    global g_lightGenModeEnabled
    print 'Entering offline space', spaceName
    BigWorld.clearAllSpaces()
    BigWorld.worldDrawEnabled(False)
    guitext = 'Client Lighting Generation Mode\n  entering: %s' % spaceName
    _displayGUI(guitext)
    spaceID = BigWorld.createSpace()
    BigWorld.addSpaceGeometryMapping(spaceID, None, spaceName)
    _loadCameraTransforms()
    camera = BigWorld.FreeCamera()
    camera.spaceID = spaceID
    BigWorld.camera(camera)
    _setCameraTransform(g_curCameraTransform)
    BigWorld.camera().fixed = False
    BigWorld.projection().fov = math.radians(75.0)
    BigWorld.setWatcher('Client Settings/Strafe Rate', 175.0)
    BigWorld.setWatcher('Client Settings/Camera Mass', 5.0)
    BigWorld.setCursor(GUI.mcursor())
    GUI.mcursor().visible = True
    GUI.mcursor().clipped = False
    g_lightGenModeEnabled = True
    BigWorld.callback(1.0, _offlineLoadCheck)
    return


def adjustSpeed(diff):
    global g_currentMoveRate
    g_currentMoveRate = max(0.1, g_currentMoveRate + diff)
    strafeRate = float(BigWorld.getWatcher('Client Settings/Strafe Rate'))
    strafeRate = 1.0 + math.pow(g_currentMoveRate, MOVE_SPEED_POW) * MOVE_SPEED_MAX
    BigWorld.setWatcher('Client Settings/Strafe Rate', strafeRate)


def adjustFOV(diff):
    newFov = BigWorld.projection().fov + diff
    newFov = min(max(newFov, FOV_MIN), FOV_MAX)
    BigWorld.projection().rampFov(newFov, 0.1)
    BigWorld.player = lambda : g_fakeAvatar
    if WWISE.enabled:
        WWISE.WG_loadBanks('', False)


def handleKeyEvent(event):
    if not g_lightGenModeEnabled or not BigWorld.camera():
        return False
    if g_enableCameraInput:
        BigWorld.camera().handleKeyEvent(event)
    if not event.isKeyDown():
        return False
    if event.key in MOUSE_TOGGLE_KEYS:
        GUI.mcursor().visible = not GUI.mcursor().visible
    elif event.key == Keys.KEY_ADD:
        adjustFOV(+FOV_ADJUST)
    elif event.key == Keys.KEY_NUMPADMINUS:
        adjustFOV(-FOV_ADJUST)
    elif event.key == Keys.KEY_F:
        newFixed = not BigWorld.camera().fixed
        BigWorld.camera().fixed = newFixed
        GUI.mcursor().visible = newFixed
        GUI.mcursor().clipped = not newFixed
    return True


def handleMouseEvent(event):
    if not g_lightGenModeEnabled or not BigWorld.camera():
        return False
    if GUI.mcursor().visible:
        return False
    if g_enableCameraInput:
        if event.dz > 0:
            adjustSpeed(+MOVE_SPEED_ADJUST)
        elif event.dz < 0:
            adjustSpeed(-MOVE_SPEED_ADJUST)
        return BigWorld.camera().handleMouseEvent(event)
    return False
