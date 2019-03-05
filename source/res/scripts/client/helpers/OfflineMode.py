# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/OfflineMode.py
import math
import logging
import sys
import BigWorld
import GUI
import Keys
import Math
import ResMgr
import WWISE
import game_mode_emulator
_logger = logging.getLogger(__name__)
g_offlineModeEnabled = False
g_currentMoveRate = 0.5
g_gui = None
MOVE_SPEED_MAX = 200.0
MOVE_SPEED_POW = 2.0
MOVE_SPEED_ADJUST = 0.1
FOV_ADJUST = math.radians(10)
FOV_MIN = math.radians(10)
FOV_MAX = math.radians(160)
MOUSE_TOGGLE_KEYS = [Keys.KEY_ESCAPE, Keys.KEY_LEFTMOUSE]

class CameraTransform(object):
    matrix = Math.Matrix()

    def __init__(self, matrix):
        self.matrix = matrix

    def apply(self):
        BigWorld.camera().set(self.matrix)


CAMERAS_XML_NAME = ResMgr.appDirectory() + 'offline_mode_cameras.xml'
g_cameraTransforms = list()
g_curCameraTransform = 0

def _clampCameraTransformIdx(val):
    val = max(0, val)
    val = min(len(g_cameraTransforms) - 1, val)
    return val


def _loadCameraTransforms():
    rootDS = ResMgr.openSection(CAMERAS_XML_NAME)
    if rootDS is not None and rootDS['cameras'] is not None:
        for c in rootDS['cameras'].values():
            c = CameraTransform(c.readMatrix('transform'))
            g_cameraTransforms.append(c)

    _logger.info('Loaded %s', CAMERAS_XML_NAME)
    return


def _saveCameraTransforms():
    rootDS = ResMgr.openSection(CAMERAS_XML_NAME, True)
    rootDS.deleteSection('cameras')
    camerasDS = rootDS.createSection('cameras')
    for c in g_cameraTransforms:
        ds = camerasDS.createSection('camera')
        ds.writeMatrix('transform', c.matrix)

    rootDS.save()
    rootDS = None
    _logger.info('Saved %s', CAMERAS_XML_NAME)
    return


def _addCameraTransform():
    g_cameraTransforms.append(CameraTransform(Math.Matrix(BigWorld.camera().matrix)))
    _saveCameraTransforms()


def _setCameraTransform(idx):
    global g_curCameraTransform
    idx = _clampCameraTransformIdx(idx)
    try:
        g_cameraTransforms[idx].apply()
        g_curCameraTransform = idx
    except IndexError:
        pass


INSTRUCTIONS = '\nWSAD: move camera\nNumpad +/-: adjust FOV\nMouse Wheel: adjust speed\nEscape: toggle mouse mode\nF: toggle camera freeze mode\nR: add new camera view point\n0-7: change camera view point\nN: move to previous camera view point\nM: move to next camera view point\nP: toggle post-precessing\nC: toggle cinematic post-processing mode\nT: toggle temporal AA\n'

def enabled():
    global g_offlineModeEnabled
    return g_offlineModeEnabled


def onStartup():
    try:
        idx = sys.argv.index('offline')
        offlineSpace = sys.argv[idx + 1]
        launch(offlineSpace)
        return True
    except (ValueError, IndexError):
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
        BigWorld.uniprofSceneStart()
        _clearGUI()
    else:
        BigWorld.callback(1.0, _offlineLoadCheck)


g_spaceID = 0
g_avatar = None

def createFakeAvatar():
    entityID = BigWorld.createEntity('OfflineEntity', BigWorld.camera().spaceID, 0, (0, 0, 0), (0, 0, 0), {})
    entity = BigWorld.entity(entityID)
    BigWorld.player = lambda : entity


def launch(spaceName):
    global g_offlineModeEnabled
    print 'Entering offline space', spaceName
    BigWorld.clearAllSpaces()
    BigWorld.worldDrawEnabled(False)
    _displayGUI(spaceName)
    spaceID = BigWorld.createSpace()
    visibilityMask = game_mode_emulator.gameModeVisibilityMask()
    BigWorld.addSpaceGeometryMapping(spaceID, None, spaceName, visibilityMask)
    _loadCameraTransforms()
    camera = BigWorld.FreeCamera()
    camera.spaceID = spaceID
    BigWorld.camera(camera)
    _setCameraTransform(g_curCameraTransform)
    BigWorld.camera().fixed = True
    BigWorld.projection().fov = math.radians(75.0)
    BigWorld.setWatcher('Client Settings/Strafe Rate', 175.0)
    BigWorld.setWatcher('Client Settings/Camera Mass', 5.0)
    BigWorld.setCursor(GUI.mcursor())
    GUI.mcursor().visible = True
    GUI.mcursor().clipped = False
    g_offlineModeEnabled = True
    BigWorld.callback(1.0, _offlineLoadCheck)
    createFakeAvatar()
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
    if WWISE.enabled:
        WWISE.WG_loadBanks('', False)


def handleKeyEvent(event):
    global g_curCameraTransform
    if not g_offlineModeEnabled or not BigWorld.camera():
        return False
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
    elif event.key == Keys.KEY_1:
        _setCameraTransform(0)
    elif event.key == Keys.KEY_2:
        _setCameraTransform(1)
    elif event.key == Keys.KEY_3:
        _setCameraTransform(2)
    elif event.key == Keys.KEY_4:
        _setCameraTransform(3)
    elif event.key == Keys.KEY_5:
        _setCameraTransform(4)
    elif event.key == Keys.KEY_6:
        _setCameraTransform(5)
    elif event.key == Keys.KEY_7:
        _setCameraTransform(6)
    elif event.key == Keys.KEY_8:
        _setCameraTransform(7)
    elif event.key == Keys.KEY_M:
        g_curCameraTransform = _clampCameraTransformIdx(g_curCameraTransform + 1)
        _setCameraTransform(g_curCameraTransform)
    elif event.key == Keys.KEY_N:
        g_curCameraTransform = _clampCameraTransformIdx(g_curCameraTransform - 1)
        _setCameraTransform(g_curCameraTransform)
    elif event.key == Keys.KEY_R:
        _addCameraTransform()
    return True


def handleMouseEvent(event):
    if not g_offlineModeEnabled or not BigWorld.camera():
        return False
    if GUI.mcursor().visible:
        return False
    if event.dz > 0:
        adjustSpeed(+MOVE_SPEED_ADJUST)
    elif event.dz < 0:
        adjustSpeed(-MOVE_SPEED_ADJUST)
    return BigWorld.camera().handleMouseEvent(event)
