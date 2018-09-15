# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/control_modes.py
import weakref
from collections import namedtuple
import BigWorld
import BattleReplay
import CommandMapping
import GUI
import Keys
import Math
import ResMgr
import SoundGroups
import TriggersManager
import VideoCamera
import cameras
import constants
from AvatarInputHandler import mathUtils, AimingSystems, aih_global_binding, gun_marker_ctrl
from AvatarInputHandler.aih_constants import CTRL_MODE_NAME, GUN_MARKER_FLAG, STRATEGIC_CAMERA
from AvatarInputHandler.StrategicCamerasInterpolator import StrategicCamerasInterpolator
from DynamicCameras import SniperCamera, StrategicCamera, ArcadeCamera, ArtyCamera
from PostmortemDelay import PostmortemDelay
from ProjectileMover import collideDynamicAndStatic, getCollidableEntities
from TriggersManager import TRIGGER_TYPE
from constants import AIMING_MODE
from debug_utils import LOG_DEBUG, LOG_CURRENT_EXCEPTION
from helpers import dependency
from post_processing import g_postProcessing
from skeletons.gui.battle_session import IBattleSessionProvider
from constants import VEHICLE_SIEGE_STATE
from gui import GUI_SETTINGS
from gui.battle_control import avatar_getter
_ARCADE_CAM_PIVOT_POS = Math.Vector3(0, 4, 3)

class IControlMode(object):

    def prerequisites(self):
        return []

    def create(self):
        pass

    def destroy(self):
        pass

    def enable(self, **args):
        pass

    def disable(self):
        pass

    def handleKeyEvent(self, isDown, key, mods, event=None):
        pass

    def handleMouseEvent(self, dx, dy, dz):
        pass

    def setGunMarkerFlag(self, positive, bit):
        pass

    def updateGunMarker(self, markerType, pos, dir, size, relaxTime, collData):
        pass

    def resetGunMarkers(self):
        pass

    def setAimingMode(self, enable, mode):
        pass

    def getAimingMode(self, mode):
        pass

    def resetAimingMode(self):
        pass

    def getDesiredShotPoint(self, ignoreAimingMode=False):
        pass

    def updateShootingStatus(self, canShoot):
        pass

    def updateTrajectory(self):
        pass

    def onRecreateDevice(self):
        pass

    def setGUIVisible(self, isVisible):
        pass

    def selectPlayer(self, vehID):
        pass

    def selectViewPoint(self, pointID):
        pass

    def onMinimapClicked(self, worldPos):
        pass

    def onSwitchViewpoint(self, vehicleID, cameraPos):
        pass

    def setObservedVehicle(self, vehicleID):
        pass

    def isSelfVehicle(self):
        return True

    def isManualBind(self):
        return False

    def getPreferredAutorotationMode(self):
        return None

    def enableSwitchAutorotationMode(self):
        return True

    def setForcedGuiControlMode(self, enable):
        pass


class _GunControlMode(IControlMode):
    aimingMode = property(lambda self: self._aimingMode)
    camera = property(lambda self: self._cam)
    _aimOffset = aih_global_binding.bindRW(aih_global_binding.BINDING_ID.AIM_OFFSET)

    def __init__(self, dataSection, avatarInputHandler, mode=CTRL_MODE_NAME.ARCADE, isStrategic=False):
        self._aih = weakref.proxy(avatarInputHandler)
        self._defaultOffset = dataSection.readVector2('defaultOffset')
        self._gunMarker = gun_marker_ctrl.createGunMarker(isStrategic)
        self._isEnabled = False
        self._cam = None
        self._aimingMode = 0
        self._canShot = False
        self._currentMode = mode
        return

    @property
    def currentMode(self):
        return self._currentMode

    def prerequisites(self):
        return []

    def create(self):
        self._gunMarker.create()
        self.disable()

    def enable(self, **args):
        self._isEnabled = True
        self._aimOffset = self._defaultOffset
        self._aimingMode = args.get('aimingMode', self._aimingMode)
        self._gunMarker.enable()

    def disable(self):
        self._isEnabled = False
        self._cam.disable()
        self._gunMarker.disable()

    def destroy(self):
        self._gunMarker.destroy()
        self._aih = None
        self._cam.destroy()
        self._cam = None
        return

    def setGunMarkerFlag(self, positive, bit):
        self._gunMarker.setFlag(positive, bit)

    def updateGunMarker(self, markerType, pos, dir, size, relaxTime, collData):
        assert self._isEnabled
        self._gunMarker.update(markerType, pos, dir, size, relaxTime, collData)

    def setAimingMode(self, enable, mode):
        if enable:
            self._aimingMode |= mode
        else:
            self._aimingMode &= -1 - mode

    def resetAimingMode(self):
        self._aimingMode = 0

    def getDesiredShotPoint(self, ignoreAimingMode=False):
        assert self._isEnabled
        return self._cam.aimingSystem.getDesiredShotPoint() if self._aimingMode == 0 and self._cam is not None or ignoreAimingMode else None

    def getAimingMode(self, mode):
        return self._aimingMode & mode == mode

    def onRecreateDevice(self):
        self._gunMarker.onRecreateDevice()

    def updateShootingStatus(self, canShot):
        assert self._isEnabled
        self._canShot = canShot


class CameraLocationPoint(object):

    def __init__(self, name, matrix):
        self.name = name
        self.matrix = matrix

    @staticmethod
    def keyForSortLocationPoint(point):
        return point.name


class VideoCameraControlMode(_GunControlMode):
    curVehicleID = property(lambda self: self.__curVehicleID)
    __locationPoints = []

    def __init__(self, dataSection, avatarInputHandler):
        super(VideoCameraControlMode, self).__init__(dataSection, avatarInputHandler)
        self.__prevModeName = None
        self.__isGunMarkerEnabled = False
        cameraDataSection = dataSection['camera'] if dataSection is not None else ResMgr.DataSection('camera')
        self.__showGunMarkerKey = getattr(Keys, cameraDataSection.readString('keyShowGunMarker', ''), None)
        self._cam = VideoCamera.VideoCamera(cameraDataSection)
        self.__curVehicleID = None
        locationXmlPath = 'spaces/' + BigWorld.player().arena.arenaType.geometryName + '/locations.xml'
        xmlSec = ResMgr.openSection(locationXmlPath)
        self.__locationPoints = []
        if xmlSec is not None:
            for name, section in xmlSec.items():
                if name == 'bookmark':
                    matrix = section.readMatrix('view', Math.Matrix())
                    point = CameraLocationPoint(section.readString('name', ''), matrix)
                    self.__locationPoints.append(point)

        return

    def enable(self, **args):
        super(VideoCameraControlMode, self).enable(**args)
        self.__prevModeName = args.get('prevModeName')
        self._cam.enable(**args)
        self.__curVehicleID = args.get('curVehicleID')
        if self.__curVehicleID is None:
            self.__curVehicleID = BigWorld.player().playerVehicleID
        return

    def getDesiredShotPoint(self, ignoreAimingMode=False):
        return None

    def setForcedGuiControlMode(self, enable):
        if not enable:
            self._cam.resetMovement()

    def isSelfVehicle(self):
        return False

    def handleKeyEvent(self, isDown, key, mods, event=None):
        if self._cam.handleKeyEvent(key, isDown):
            return True
        elif BigWorld.isKeyDown(Keys.KEY_CAPSLOCK) and isDown and key == Keys.KEY_F3 and self.__prevModeName is not None:
            self._aih.onControlModeChanged(self.__prevModeName)
            return True
        else:
            if isDown:
                if self.__showGunMarkerKey is not None and self.__showGunMarkerKey == key:
                    self.__isGunMarkerEnabled = not self.__isGunMarkerEnabled
                    self._gunMarker.setFlag(self.__isGunMarkerEnabled, GUN_MARKER_FLAG.VIDEO_MODE_ENABLED)
                    return True
            return False

    def teleport(self, index):
        assert index > 0 and index <= len(self.__locationPoints), 'Out of range'
        self._cam.setViewMatrix(self.__locationPoints[index - 1].matrix)

    def teleportByName(self, name):
        for point in self.__locationPoints:
            if point.name == name:
                self._cam.setViewMatrix(point.matrix)
                return

        assert False, 'Location with name %s not found' % name

    def handleMouseEvent(self, dx, dy, dz):
        self._cam.handleMouseEvent(dx, dy, dz)
        return True

    def onPostmortemActivation(self):
        self.__prevModeName = 'postmortem'


class DebugControlMode(IControlMode):

    def __init__(self, dataSection, avatarInputHandler):
        self.__aih = weakref.proxy(avatarInputHandler)
        self.__cam = cameras.FreeCamera()
        self.__isCreated = False
        self.__isEnabled = False
        self.__prevModeName = None
        self.__videoControl = None
        return

    def prerequisites(self):
        return []

    def create(self):
        self.__isCreated = True

    def destroy(self):
        self.disable()
        self.__cam.destroy()
        self.__cam = None
        self.__isCreated = False
        return

    def enable(self, **args):
        self.__prevModeName = args.get('prevModeName')
        camMatrix = args.get('camMatrix')
        self.__cam.enable(camMatrix)
        BigWorld.setWatcher('Client Settings/Strafe Rate', 50)
        BigWorld.setWatcher('Client Settings/Camera Mass', 1)
        assert constants.HAS_DEV_RESOURCES
        import Cat
        Cat.Tasks.VideoEngineer.SetEnable(True)
        self.__videoControl = Cat.Tasks.VideoEngineer.VideoControl(self.__cam)
        self.__videoControl.setEnable(True)
        self.__isEnabled = True
        g_postProcessing.enable('debug')

    def disable(self):
        self.__isEnabled = False
        if self.__videoControl is not None:
            self.__videoControl.setEnable(False)
            self.__videoControl.destroy()
            self.__videoControl = None
        self.__cam.disable()
        g_postProcessing.disable()
        return

    def handleKeyEvent(self, isDown, key, mods, event=None):
        assert self.__isEnabled
        if key == Keys.KEY_SYSRQ:
            return False
        if BigWorld.isKeyDown(Keys.KEY_CAPSLOCK) and constants.HAS_DEV_RESOURCES and isDown and key == Keys.KEY_F1:
            self.__aih.onControlModeChanged(self.__prevModeName)
            return True
        return True if self.__videoControl.handleKeyEvent(isDown, key, mods, event) else self.__cam.handleKey(event)

    def handleMouseEvent(self, dx, dy, dz):
        assert self.__isEnabled
        GUI.mcursor().position = (0, 0)
        return self.__videoControl.handleMouseEvent(dx, dy, dz)

    def getDesiredShotPoint(self, ignoreAimingMode=False):
        assert self.__isEnabled
        return None

    def updateShootingStatus(self, canShot):
        assert self.__isEnabled
        return None

    def setCameraPosition(self, x, y, z):
        mat = Math.Matrix()
        mat.lookAt(Math.Vector3(x, y, z), (0, 0, 1), (0, 1, 0))
        self.__cam.camera.set(mat)

    def getDebugVideoControl(self):
        return self.__videoControl

    def isManualBind(self):
        return True


class CatControlMode(IControlMode):

    def __init__(self, dataSection, avatarInputHandler):
        self.__aih = weakref.proxy(avatarInputHandler)
        self.__cam = cameras.FreeCamera()
        self.__isCreated = False
        self.__isEnabled = False
        self.__shellingControl = None
        self.__sens = (3.0, 3.0, 3.0)
        return

    def prerequisites(self):
        return []

    def create(self):
        self.__shellingControl = _ShellingControl(self.__cam)
        self.__isCreated = True

    def destroy(self):
        self.disable()
        if self.__shellingControl is not None:
            self.__shellingControl.destroy()
            self.__shellingControl = None
        if self.__cam is not None:
            self.__cam.destroy()
            self.__cam = None
        self.__isCreated = False
        return

    def enable(self, **args):
        camMatrix = args.get('camMatrix')
        self.__cam.enable(camMatrix)
        BigWorld.setWatcher('Client Settings/Strafe Rate', 50)
        BigWorld.setWatcher('Client Settings/Camera Mass', 1)
        self.__shellingControl.setEnable(True)
        self.__isEnabled = True

    def setForcedGuiControlMode(self, enable):
        if not enable:
            self.__cam.resetMovement()

    def isSelfVehicle(self):
        return False

    def disable(self):
        if self.__shellingControl is not None:
            self.__shellingControl.setEnable(False)
        if self.__cam is not None:
            self.__cam.disable()
        self.__isEnabled = False
        return

    def handleKeyEvent(self, isDown, key, mods, event=None):
        assert self.__isEnabled
        if BigWorld.isKeyDown(Keys.KEY_CAPSLOCK) and constants.HAS_DEV_RESOURCES and isDown and key == Keys.KEY_F2:
            self.__aih.onControlModeChanged('arcade')
        self.__shellingControl.handleKeyEvent(isDown, key, mods, event)
        return self.__cam.handleKey(event)

    def handleMouseEvent(self, dx, dy, dz):
        assert self.__isEnabled
        GUI.mcursor().position = (0, 0)
        return self.__cam.handleMouse(int(self.__sens[0] * dx), int(self.__sens[1] * dy), int(self.__sens[2] * dz))

    def onRecreateDevice(self):
        self.__shellingControl.recreate()

    def getEnabled(self):
        return bool(self.__isEnabled)

    def setCameraPosition(self, x, y, z):
        mat = Math.Matrix()
        mat.lookAt(Math.Vector3(x, y, z), (0, 0, 1), (0, 1, 0))
        self.__cam.camera.set(mat)

    def getCameraPosition(self):
        return tuple(self.__cam.camera.position)

    def setSensitivity(self, sens):
        self.__sens = tuple(sens)

    def getShellingControl(self):
        return self.__shellingControl

    def isManualBind(self):
        return True


class ArcadeControlMode(_GunControlMode):
    postmortemCamParams = property(lambda self: (self._cam.angles, self._cam.camera.pivotMaxDist))
    strategicControlMode = CTRL_MODE_NAME.STRATEGIC

    def __init__(self, dataSection, avatarInputHandler):
        super(ArcadeControlMode, self).__init__(dataSection, avatarInputHandler, mode=CTRL_MODE_NAME.ARCADE)
        self._cam = ArcadeCamera.ArcadeCamera(dataSection['camera'], defaultOffset=self._defaultOffset)
        self.__mouseVehicleRotator = _MouseVehicleRotator()
        self.__videoControlModeAvailable = dataSection.readBool('videoModeAvailable', constants.HAS_DEV_RESOURCES)
        self.__videoControlModeAvailable &= BattleReplay.g_replayCtrl.isPlaying or constants.HAS_DEV_RESOURCES

    @property
    def curVehicleID(self):
        return BigWorld.player().playerVehicleID

    def create(self):
        self._cam.create(_ARCADE_CAM_PIVOT_POS, self.onChangeControlModeByScroll)
        super(ArcadeControlMode, self).create()

    def destroy(self):
        self.disable()
        self.__mouseVehicleRotator.destroy()
        self.__mouseVehicleRotator = None
        self._cam.writeUserPreferences()
        super(ArcadeControlMode, self).destroy()
        return

    def enable(self, **args):
        super(ArcadeControlMode, self).enable(**args)
        SoundGroups.g_instance.changePlayMode(0)
        self._cam.enable(args.get('preferredPos'), args.get('closesDist', False), turretYaw=args.get('turretYaw', 0.0), gunPitch=args.get('gunPitch', 0.0))
        g_postProcessing.enable('arcade')
        player = BigWorld.player()
        if player.isObserver():
            player.updateObservedVehicleData()

    def disable(self):
        super(ArcadeControlMode, self).disable()
        g_postProcessing.disable()

    def handleKeyEvent(self, isDown, key, mods, event=None):
        assert self._isEnabled
        cmdMap = CommandMapping.g_instance
        if self._cam.handleKeyEvent(isDown, key, mods, event):
            return True
        elif BigWorld.isKeyDown(Keys.KEY_CAPSLOCK) and constants.HAS_DEV_RESOURCES and isDown and key == Keys.KEY_F1:
            self._aih.onControlModeChanged(CTRL_MODE_NAME.DEBUG, prevModeName=CTRL_MODE_NAME.ARCADE, camMatrix=self._cam.camera.matrix)
            return True
        elif BigWorld.isKeyDown(Keys.KEY_CAPSLOCK) and constants.HAS_DEV_RESOURCES and isDown and key == Keys.KEY_F2:
            self._aih.onControlModeChanged(CTRL_MODE_NAME.CAT, camMatrix=self._cam.camera.matrix)
            return True
        elif BigWorld.isKeyDown(Keys.KEY_CAPSLOCK) and isDown and key == Keys.KEY_F3 and self.__videoControlModeAvailable:
            self._aih.onControlModeChanged(CTRL_MODE_NAME.VIDEO, prevModeName=CTRL_MODE_NAME.ARCADE, camMatrix=self._cam.camera.matrix)
            return True
        isFiredFreeCamera = cmdMap.isFired(CommandMapping.CMD_CM_FREE_CAMERA, key)
        isFiredLockTarget = cmdMap.isFired(CommandMapping.CMD_CM_LOCK_TARGET, key) and isDown
        if isFiredFreeCamera or isFiredLockTarget:
            if isFiredFreeCamera:
                self.setAimingMode(isDown, AIMING_MODE.USER_DISABLED)
            if isFiredLockTarget:
                BigWorld.player().autoAim(BigWorld.target())
        if cmdMap.isFired(CommandMapping.CMD_CM_SHOOT, key) and isDown:
            BigWorld.player().shoot()
            return True
        elif cmdMap.isFired(CommandMapping.CMD_CM_LOCK_TARGET_OFF, key) and isDown:
            BigWorld.player().autoAim(None)
            return True
        elif cmdMap.isFired(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION, key) and isDown:
            self._aih.switchAutorotation()
            return True
        elif cmdMap.isFiredList((CommandMapping.CMD_CM_CAMERA_ROTATE_LEFT,
         CommandMapping.CMD_CM_CAMERA_ROTATE_RIGHT,
         CommandMapping.CMD_CM_CAMERA_ROTATE_UP,
         CommandMapping.CMD_CM_CAMERA_ROTATE_DOWN,
         CommandMapping.CMD_CM_INCREASE_ZOOM,
         CommandMapping.CMD_CM_DECREASE_ZOOM), key):
            dx = dy = dz = 0.0
            if cmdMap.isActive(CommandMapping.CMD_CM_CAMERA_ROTATE_LEFT):
                dx = -1.0
            if cmdMap.isActive(CommandMapping.CMD_CM_CAMERA_ROTATE_RIGHT):
                dx = 1.0
            if cmdMap.isActive(CommandMapping.CMD_CM_CAMERA_ROTATE_UP):
                dy = -1.0
            if cmdMap.isActive(CommandMapping.CMD_CM_CAMERA_ROTATE_DOWN):
                dy = 1.0
            if cmdMap.isActive(CommandMapping.CMD_CM_INCREASE_ZOOM):
                dz = 1.0
            if cmdMap.isActive(CommandMapping.CMD_CM_DECREASE_ZOOM):
                dz = -1.0
            self._cam.update(dx, dy, dz, True, True, False if dx == dy == dz == 0.0 else True)
            return True
        elif cmdMap.isFired(CommandMapping.CMD_CM_ALTERNATE_MODE, key) and isDown:
            self.__activateAlternateMode()
            return True
        elif cmdMap.isFired(CommandMapping.CMD_CM_CAMERA_RESTORE_DEFAULT, key) and isDown:
            self._cam.restoreDefaultsState()
            return True
        else:
            return False

    def handleMouseEvent(self, dx, dy, dz):
        assert self._isEnabled
        GUI.mcursor().position = self._aimOffset
        if not self._aih.isObserverFPV:
            self._cam.update(dx, dy, mathUtils.clamp(-1, 1, dz))
            self.__mouseVehicleRotator.handleMouse(dx)
        return True

    def onMinimapClicked(self, worldPos):
        if self._aih.isSPG:
            self.__activateAlternateMode(worldPos)

    def onChangeControlModeByScroll(self):
        if self._cam.getUserConfigValue('sniperModeByShift'):
            return
        else:
            self.__activateAlternateMode(pos=None, bByScroll=True)
            return

    def setForcedGuiControlMode(self, enable):
        if not enable:
            self._cam.update(0, 0, 0, False, False)

    def __activateAlternateMode(self, pos=None, bByScroll=False):
        ownVehicle = BigWorld.entity(BigWorld.player().playerVehicleID)
        if ownVehicle is not None and ownVehicle.isStarted and avatar_getter.isVehicleBarrelUnderWater() or BigWorld.player().isGunLocked:
            return
        elif self._aih.isSPG and not bByScroll:
            self._cam.update(0, 0, 0, False, False)
            equipmentID = None
            if BattleReplay.isPlaying():
                mode = BattleReplay.g_replayCtrl.getControlMode()
                pos = BattleReplay.g_replayCtrl.getGunMarkerPos()
                equipmentID = BattleReplay.g_replayCtrl.getEquipmentId()
            else:
                mode = ArcadeControlMode.strategicControlMode
                if pos is None:
                    pos = self.camera.aimingSystem.getDesiredShotPoint()
                    if pos is None:
                        pos = self._gunMarker.getPosition()
            self._aih.onControlModeChanged(mode, preferredPos=pos, aimingMode=self._aimingMode, saveDist=True, equipmentID=equipmentID)
            return
        elif not self._aih.isSPG:
            self._cam.update(0, 0, 0, False, False)
            if BattleReplay.isPlaying() and BigWorld.player().isGunLocked:
                mode = BattleReplay.g_replayCtrl.getControlMode()
                desiredShotPoint = BattleReplay.g_replayCtrl.getGunMarkerPos()
                equipmentID = BattleReplay.g_replayCtrl.getEquipmentId()
            else:
                mode = CTRL_MODE_NAME.SNIPER
                equipmentID = None
                desiredShotPoint = self.camera.aimingSystem.getDesiredShotPoint()
            self._aih.onControlModeChanged(mode, preferredPos=desiredShotPoint, aimingMode=self._aimingMode, saveZoom=not bByScroll, equipmentID=equipmentID)
            return
        else:
            return


class _TrajectoryControlMode(_GunControlMode):
    curVehicleID = property(lambda self: self.__curVehicleID)
    strategicCamera = aih_global_binding.bindRW(aih_global_binding.BINDING_ID.STRATEGIC_CAMERA)
    __interpolator = StrategicCamerasInterpolator()

    def __init__(self, dataSection, avatarInputHandler, modeName, trajectoryUpdateInterval):
        super(_TrajectoryControlMode, self).__init__(dataSection, avatarInputHandler, modeName, True)
        self.__trajectoryDrawer = BigWorld.wg_trajectory_drawer()
        self.__trajectoryDrawerClbk = None
        self.__updateInterval = trajectoryUpdateInterval
        self._nextControlMode = modeName
        self.__curVehicleID = None
        return

    def create(self):
        self._cam.create(None)
        super(_TrajectoryControlMode, self).create()
        self.__initTrajectoryDrawer()
        return

    def destroy(self):
        self.disable()
        self.__delTrajectoryDrawer()
        self._cam.writeUserPreferences()
        super(_TrajectoryControlMode, self).destroy()

    def enable(self, **args):
        super(_TrajectoryControlMode, self).enable(**args)
        SoundGroups.g_instance.changePlayMode(2)
        self._cam.enable(args['preferredPos'], args['saveDist'])
        self.__trajectoryDrawer.visible = self._aih.isGuiVisible
        BigWorld.player().autoAim(None)
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying and replayCtrl.isControllingCamera:
            self.__trajectoryDrawerClbk = BigWorld.callback(0.0, self.__updateTrajectoryDrawer)
        else:
            self.__updateTrajectoryDrawer()
        g_postProcessing.enable(CTRL_MODE_NAME.STRATEGIC)
        self.__curVehicleID = args.get('curVehicleID')
        if self.__curVehicleID is None:
            self.__curVehicleID = BigWorld.player().getVehicleAttached()
        return

    def disable(self):
        super(_TrajectoryControlMode, self).disable()
        self.__trajectoryDrawer.visible = False
        if self.__trajectoryDrawerClbk is not None:
            BigWorld.cancelCallback(self.__trajectoryDrawerClbk)
            self.__trajectoryDrawerClbk = None
        g_postProcessing.disable()
        return

    def setObservedVehicle(self, vehicleID):
        self.__trajectoryDrawer.setGetDynamicCollidersCallback(lambda start, end: [ e.collideSegment for e in getCollidableEntities((vehicleID,), start, end) ])

    def handleKeyEvent(self, isDown, key, mods, event=None):
        assert self._isEnabled
        cmdMap = CommandMapping.g_instance
        if cmdMap.isFired(CommandMapping.CMD_CM_SHOOT, key) and isDown:
            BigWorld.player().shoot()
            return True
        elif cmdMap.isFired(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION, key) and isDown:
            self._aih.switchAutorotation()
            return True
        elif cmdMap.isFired(CommandMapping.CMD_CM_ALTERNATE_MODE, key) and isDown:
            self.__interpolator.disable()
            pos = self._cam.aimingSystem.getDesiredShotPoint()
            if pos is None:
                pos = self._gunMarker.getPosition()
            self._aih.onControlModeChanged(CTRL_MODE_NAME.ARCADE, preferredPos=pos, aimingMode=self._aimingMode, closesDist=False)
            return True
        if cmdMap.isFired(CommandMapping.CMD_CM_FREE_CAMERA, key):
            self.setAimingMode(isDown, AIMING_MODE.USER_DISABLED)
        if cmdMap.isFiredList((CommandMapping.CMD_CM_CAMERA_ROTATE_LEFT,
         CommandMapping.CMD_CM_CAMERA_ROTATE_RIGHT,
         CommandMapping.CMD_CM_CAMERA_ROTATE_UP,
         CommandMapping.CMD_CM_CAMERA_ROTATE_DOWN,
         CommandMapping.CMD_CM_INCREASE_ZOOM,
         CommandMapping.CMD_CM_DECREASE_ZOOM), key):
            replayCtrl = BattleReplay.g_replayCtrl
            if replayCtrl.isPlaying and replayCtrl.isControllingCamera:
                return True
            dx = dy = dz = 0.0
            if cmdMap.isActive(CommandMapping.CMD_CM_CAMERA_ROTATE_LEFT):
                dx = -1.0
            if cmdMap.isActive(CommandMapping.CMD_CM_CAMERA_ROTATE_RIGHT):
                dx = 1.0
            if cmdMap.isActive(CommandMapping.CMD_CM_CAMERA_ROTATE_UP):
                dy = -1.0
            if cmdMap.isActive(CommandMapping.CMD_CM_CAMERA_ROTATE_DOWN):
                dy = 1.0
            if cmdMap.isActive(CommandMapping.CMD_CM_INCREASE_ZOOM):
                dz = 1.0
            if cmdMap.isActive(CommandMapping.CMD_CM_DECREASE_ZOOM):
                dz = -1.0
            self._cam.update(dx, dy, dz, False if dx == dy == dz == 0.0 else True)
            return True
        if cmdMap.isFired(CommandMapping.CMD_CM_TRAJECTORY_VIEW, key) and isDown:
            if self.__switchToNextControlMode():
                return True
        if cmdMap.isFired(CommandMapping.CMD_CM_CAMERA_RESTORE_DEFAULT, key) and isDown:
            self._cam.update(0, 0, 0, False)
            self._cam.restoreDefaultsState()
            return True
        else:
            return False

    def handleMouseEvent(self, dx, dy, dz):
        assert self._isEnabled
        GUI.mcursor().position = self._aimOffset
        if not self._aih.isObserverFPV:
            self._cam.update(dx, dy, dz)
        return True

    def onMinimapClicked(self, worldPos):
        self._cam.teleport(worldPos)

    def resetGunMarkers(self):
        self._gunMarker.reset()

    def setGUIVisible(self, isVisible):
        self.__trajectoryDrawer.visible = isVisible

    def isManualBind(self):
        return True

    def __switchToNextControlMode(self):
        if GUI_SETTINGS.spgAlternativeAimingCameraEnabled:
            pos = self._cam.aimingSystem.planePosition
            if pos is None:
                pos = self._gunMarker.getPosition()
            source = self._cam.camera
            sourceFov = BigWorld.projection().fov
            self._aih.onControlModeChanged(self._nextControlMode, preferredPos=pos, aimingMode=self._aimingMode, saveDist=True)
            self.__interpolator.enable(source, self._aih.ctrl.camera.camera, sourceFov, BigWorld.projection().fov)
            ArcadeControlMode.strategicControlMode = self._nextControlMode
            isStrategicMode = ArcadeControlMode.strategicControlMode == CTRL_MODE_NAME.STRATEGIC
            self.__trajectoryDrawer.setStrategicMode(isStrategicMode)
            return True
        else:
            return False

    def __updateTrajectoryDrawer(self):
        self.__trajectoryDrawerClbk = BigWorld.callback(self.__updateInterval, self.__updateTrajectoryDrawer)
        try:
            R = self.camera.aimingSystem.getDesiredShotPoint()
            if R is None:
                return
            r0, v0, g0 = BigWorld.player().gunRotator.getShotParams(R, True)
            self.__trajectoryDrawer.update(R, r0, v0, self.__updateInterval)
        except:
            LOG_CURRENT_EXCEPTION()

        return

    def __onGunShotChanged(self):
        shotDescr = BigWorld.player().getVehicleDescriptor().shot
        self.__trajectoryDrawer.setParams(shotDescr.maxDistance, Math.Vector3(0, -shotDescr.gravity, 0), self._aimOffset)

    def __initTrajectoryDrawer(self):
        player = BigWorld.player()
        player.onGunShotChanged += self.__onGunShotChanged
        self.__trajectoryDrawer.setColors(Math.Vector4(0, 255, 0, 255), Math.Vector4(255, 0, 0, 255), Math.Vector4(128, 128, 128, 255))
        nonCollideVehicleID = player.playerVehicleID
        if player.getVehicleAttached() is not None:
            nonCollideVehicleID = player.getVehicleAttached().id
        self.__trajectoryDrawer.setGetDynamicCollidersCallback(lambda start, end: [ e.collideSegment for e in getCollidableEntities((nonCollideVehicleID,), start, end) ])
        self.__onGunShotChanged()
        return

    def __delTrajectoryDrawer(self):
        BigWorld.player().onGunShotChanged -= self.__onGunShotChanged
        self.__trajectoryDrawer = None
        return


class StrategicControlMode(_TrajectoryControlMode):
    _TRAJECTORY_UPDATE_INTERVAL = 0.1

    def __init__(self, dataSection, avatarInputHandler):
        super(StrategicControlMode, self).__init__(dataSection, avatarInputHandler, CTRL_MODE_NAME.STRATEGIC, StrategicControlMode._TRAJECTORY_UPDATE_INTERVAL)
        self._nextControlMode = CTRL_MODE_NAME.ARTY
        self._cam = StrategicCamera.StrategicCamera(dataSection['camera'])

    def enable(self, **args):
        super(StrategicControlMode, self).enable(**args)
        BigWorld.setFloraEnabled(False)

    def disable(self):
        super(StrategicControlMode, self).disable()
        BigWorld.setFloraEnabled(True)


class ArtyControlMode(_TrajectoryControlMode):
    _TRAJECTORY_UPDATE_INTERVAL = 0.05

    def __init__(self, dataSection, avatarInputHandler):
        super(ArtyControlMode, self).__init__(dataSection, avatarInputHandler, CTRL_MODE_NAME.ARTY, ArtyControlMode._TRAJECTORY_UPDATE_INTERVAL)
        self._nextControlMode = CTRL_MODE_NAME.STRATEGIC
        self._cam = ArtyCamera.ArtyCamera(dataSection['camera'])

    def enable(self, **args):
        super(ArtyControlMode, self).enable(**args)
        self.strategicCamera = STRATEGIC_CAMERA.TRAJECTORY
        BigWorld.setFloraEnabled(True)

    def disable(self):
        super(ArtyControlMode, self).disable()
        self.strategicCamera = STRATEGIC_CAMERA.AERIAL
        BigWorld.setFloraEnabled(True)


class SniperControlMode(_GunControlMode):
    _LENS_EFFECTS_ENABLED = True
    _BINOCULARS_MODE_SUFFIX = ['usual', 'coated']
    BinocularsModeDesc = namedtuple('BinocularsModeDesc', ('background', 'distortion', 'rgbCube', 'greenOffset', 'blueOffset', 'aberrationRadius', 'distortionAmount'))

    @staticmethod
    def enableLensEffects(enable):
        SniperControlMode._LENS_EFFECTS_ENABLED = enable
        curCtrl = getattr(getattr(BigWorld.player(), 'inputHandler', None), 'ctrl', None)
        if isinstance(curCtrl, SniperControlMode) and curCtrl.__binoculars is not None:
            curCtrl.__binoculars.setEnableLensEffects(SniperControlMode._LENS_EFFECTS_ENABLED)
        return

    def __init__(self, dataSection, avatarInputHandler):
        super(SniperControlMode, self).__init__(dataSection, avatarInputHandler, CTRL_MODE_NAME.SNIPER)
        self.__binoculars = BigWorld.wg_binoculars()
        self._cam = SniperCamera.SniperCamera(dataSection['camera'], defaultOffset=self._defaultOffset, binoculars=self.__binoculars)
        self.__coatedOptics = False
        self.__binocularsModes = {}
        for suffix in SniperControlMode._BINOCULARS_MODE_SUFFIX:
            prefPath = 'binoculars_' + suffix
            modeDesc = SniperControlMode.BinocularsModeDesc(dataSection.readString(prefPath + '/background'), dataSection.readString(prefPath + '/distortion'), dataSection.readString(prefPath + '/rgbCube'), dataSection.readFloat(prefPath + '/greenOffset'), dataSection.readFloat(prefPath + '/blueOffset'), dataSection.readFloat(prefPath + '/aberrationRadius'), dataSection.readFloat(prefPath + '/distortionAmount'))
            self.__binocularsModes[suffix] = modeDesc

    def create(self):
        self._cam.create(self.onChangeControlModeByScroll)
        super(SniperControlMode, self).create()
        from items.vehicles import g_cache
        self.__setupBinoculars(g_cache.optionalDevices()[5] in BigWorld.entities[BigWorld.player().playerVehicleID].typeDescriptor.optionalDevices)

    def destroy(self):
        self.disable(True)
        self.__binoculars.enabled = False
        self.__binoculars.resetTextures()
        self._cam.writeUserPreferences()
        super(SniperControlMode, self).destroy()

    def enable(self, **args):
        super(SniperControlMode, self).enable(**args)
        SoundGroups.g_instance.changePlayMode(1)
        self._cam.enable(args['preferredPos'], args['saveZoom'])
        self.__binoculars.enabled = True
        self.__binoculars.setEnableLensEffects(SniperControlMode._LENS_EFFECTS_ENABLED)
        BigWorld.wg_setLowDetailedMode(True)
        BigWorld.wg_enableTreeHiding(True)
        BigWorld.wg_setTreeHidingRadius(15.0, 10.0)
        BigWorld.wg_havokSetSniperMode(True)
        if not BattleReplay.g_replayCtrl.isPlaying:
            TriggersManager.g_manager.activateTrigger(TRIGGER_TYPE.SNIPER_MODE)
        if BattleReplay.g_replayCtrl.isRecording:
            BattleReplay.g_replayCtrl.onSniperModeChanged(True)
        g_postProcessing.enable('sniper')
        desc = BigWorld.player().getVehicleDescriptor()
        isHorizontalStabilizerAllowed = desc.gun.turretYawLimits is None
        self._cam.aimingSystem.enableHorizontalStabilizerRuntime(isHorizontalStabilizerAllowed)
        self._cam.aimingSystem.forceFullStabilization(self.__isFullStabilizationRequired())
        if self._aih.siegeModeControl is not None:
            self._aih.siegeModeControl.onSiegeStateChanged += self.__siegeModeStateChanged
        return

    def disable(self, isDestroy=False):
        super(SniperControlMode, self).disable()
        self.__binoculars.enabled = False
        BigWorld.wg_havokSetSniperMode(False)
        BigWorld.wg_enableTreeHiding(False)
        g_postProcessing.disable()
        BigWorld.wg_setLowDetailedMode(False)
        if not BattleReplay.g_replayCtrl.isPlaying:
            if TriggersManager.g_manager is not None:
                TriggersManager.g_manager.deactivateTrigger(TRIGGER_TYPE.SNIPER_MODE)
        if self._aih.siegeModeControl is not None:
            self._aih.siegeModeControl.onSiegeStateChanged -= self.__siegeModeStateChanged
        if BattleReplay.g_replayCtrl.isRecording:
            BattleReplay.g_replayCtrl.onSniperModeChanged(False)
        return

    def setObservedVehicle(self, vehicleID):
        vehicle = BigWorld.entities.get(vehicleID, None)
        if vehicle is None:
            return
        else:
            vehicleDescr = vehicle.typeDescriptor
            from items.vehicles import g_cache
            self.__setupBinoculars(g_cache.optionalDevices()[5] in vehicleDescr.optionalDevices)
            isHorizontalStabilizerAllowed = vehicleDescr.gun.turretYawLimits is None
            if self._cam.aimingSystem is not None:
                self._cam.aimingSystem.enableHorizontalStabilizerRuntime(isHorizontalStabilizerAllowed)
            return

    def handleKeyEvent(self, isDown, key, mods, event=None):
        assert self._isEnabled
        cmdMap = CommandMapping.g_instance
        isFiredFreeCamera = cmdMap.isFired(CommandMapping.CMD_CM_FREE_CAMERA, key)
        isFiredLockTarget = cmdMap.isFired(CommandMapping.CMD_CM_LOCK_TARGET, key) and isDown
        if isFiredFreeCamera or isFiredLockTarget:
            if isFiredFreeCamera:
                self.setAimingMode(isDown, AIMING_MODE.USER_DISABLED)
            if isFiredLockTarget:
                BigWorld.player().autoAim(BigWorld.target())
        if cmdMap.isFired(CommandMapping.CMD_CM_SHOOT, key) and isDown:
            BigWorld.player().shoot()
            return True
        elif cmdMap.isFired(CommandMapping.CMD_CM_LOCK_TARGET_OFF, key) and isDown:
            BigWorld.player().autoAim(None)
            return True
        elif cmdMap.isFired(CommandMapping.CMD_CM_ALTERNATE_MODE, key) and isDown:
            self._aih.onControlModeChanged(CTRL_MODE_NAME.ARCADE, preferredPos=self.camera.aimingSystem.getDesiredShotPoint(), turretYaw=self._cam.aimingSystem.turretYaw, gunPitch=self._cam.aimingSystem.gunPitch, aimingMode=self._aimingMode, closesDist=False)
            return True
        elif cmdMap.isFired(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION, key) and isDown:
            self._aih.switchAutorotation()
            return True
        elif cmdMap.isFiredList((CommandMapping.CMD_CM_CAMERA_ROTATE_LEFT,
         CommandMapping.CMD_CM_CAMERA_ROTATE_RIGHT,
         CommandMapping.CMD_CM_CAMERA_ROTATE_UP,
         CommandMapping.CMD_CM_CAMERA_ROTATE_DOWN,
         CommandMapping.CMD_CM_INCREASE_ZOOM,
         CommandMapping.CMD_CM_DECREASE_ZOOM), key):
            dx = dy = dz = 0.0
            if cmdMap.isActive(CommandMapping.CMD_CM_CAMERA_ROTATE_LEFT):
                dx = -1.0
            if cmdMap.isActive(CommandMapping.CMD_CM_CAMERA_ROTATE_RIGHT):
                dx = 1.0
            if cmdMap.isActive(CommandMapping.CMD_CM_CAMERA_ROTATE_UP):
                dy = -1.0
            if cmdMap.isActive(CommandMapping.CMD_CM_CAMERA_ROTATE_DOWN):
                dy = 1.0
            if cmdMap.isActive(CommandMapping.CMD_CM_INCREASE_ZOOM):
                dz = 1.0
            if cmdMap.isActive(CommandMapping.CMD_CM_DECREASE_ZOOM):
                dz = -1.0
            replayCtrl = BattleReplay.g_replayCtrl
            if replayCtrl.isPlaying and replayCtrl.isControllingCamera:
                return True
            self._cam.update(dx, dy, dz, False if dx == dy == 0.0 else True)
            return True
        else:
            return False

    def handleMouseEvent(self, dx, dy, dz):
        assert self._isEnabled
        GUI.mcursor().position = self._aimOffset
        if not self._aih.isObserverFPV:
            self._cam.update(dx, dy, dz)
        return True

    def onRecreateDevice(self):
        super(SniperControlMode, self).onRecreateDevice()
        self._cam.onRecreateDevice()

    def getPreferredAutorotationMode(self):
        vehicle = BigWorld.entities.get(BigWorld.player().playerVehicleID)
        if vehicle is None:
            return
        else:
            desc = vehicle.typeDescriptor
            isRotationAroundCenter = desc.chassis.rotationIsAroundCenter
            turretHasYawLimits = desc.gun.turretYawLimits is not None
            yawHullAimingAvailable = desc.isYawHullAimingAvailable
            return isRotationAroundCenter and not turretHasYawLimits or yawHullAimingAvailable

    def enableSwitchAutorotationMode(self):
        return self.getPreferredAutorotationMode() is not False

    def onChangeControlModeByScroll(self, switchToClosestDist=True):
        assert self._isEnabled
        if self._cam.getUserConfigValue('sniperModeByShift'):
            return
        self._aih.onControlModeChanged(CTRL_MODE_NAME.ARCADE, preferredPos=self.camera.aimingSystem.getDesiredShotPoint(), turretYaw=self._cam.aimingSystem.turretYaw, gunPitch=self._cam.aimingSystem.gunPitch, aimingMode=self._aimingMode, closesDist=switchToClosestDist)

    def recreateCamera(self):
        preferredPos = self.camera.aimingSystem.getDesiredShotPoint()
        self._cam.disable()
        self._cam.enable(preferredPos, True)

    def setForcedGuiControlMode(self, enable):
        if not enable:
            self._cam.update(0, 0, 0, False)

    def __setupBinoculars(self, isCoatedOptics):
        modeDesc = self.__binocularsModes[SniperControlMode._BINOCULARS_MODE_SUFFIX[1 if isCoatedOptics else 0]]
        self.__binoculars.setBackgroundTexture(modeDesc.background)
        self.__binoculars.setDistortionTexture(modeDesc.distortion)
        self.__binoculars.setColorGradingTexture(modeDesc.rgbCube)
        self.__binoculars.setParams(modeDesc.greenOffset, modeDesc.blueOffset, modeDesc.aberrationRadius, modeDesc.distortionAmount)

    def __siegeModeStateChanged(self, newState, timeToNewMode):
        if newState == VEHICLE_SIEGE_STATE.ENABLED or newState == VEHICLE_SIEGE_STATE.DISABLED:
            self._cam.aimingSystem.forceFullStabilization(self.__isFullStabilizationRequired())

    def __isFullStabilizationRequired(self):
        descriptor = BigWorld.player().vehicleTypeDescriptor
        return descriptor.isPitchHullAimingAvailable or descriptor.isYawHullAimingAvailable


class PostMortemControlMode(IControlMode):
    _POSTMORTEM_DELAY_ENABLED = True
    camera = property(lambda self: self.__cam)
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    __aimOffset = aih_global_binding.bindRW(aih_global_binding.BINDING_ID.AIM_OFFSET)

    @staticmethod
    def getIsPostmortemDelayEnabled():
        return PostMortemControlMode._POSTMORTEM_DELAY_ENABLED

    @staticmethod
    def setIsPostmortemDelayEnabled(value):
        PostMortemControlMode._POSTMORTEM_DELAY_ENABLED = value

    __CAM_FLUENCY = 0.0
    OBSERVE_VEH_DATA = namedtuple('OBSERVE_VEH_DATA', ['isAlive',
     'level',
     'type',
     'vehicleName',
     'playerName',
     'isSquadMan',
     'id',
     'team'])

    def __init__(self, dataSection, avatarInputHandler):
        self.__aih = weakref.proxy(avatarInputHandler)
        self.__cam = ArcadeCamera.ArcadeCamera(dataSection['camera'], dataSection.readVector2('defaultOffset'))
        self.__curVehicleID = None
        self.__selfVehicleID = None
        self.__isEnabled = False
        self.__postmortemDelay = None
        self.__isObserverMode = False
        self.__videoControlModeAvailable = dataSection.readBool('videoModeAvailable', constants.HAS_DEV_RESOURCES)
        return

    def prerequisites(self):
        return []

    def create(self):
        self.__cam.create(_ARCADE_CAM_PIVOT_POS, None, True)
        return

    def destroy(self):
        self.disable()
        self.__cam.destroy()
        self.__cam = None
        return

    def enable(self, **args):
        SoundGroups.g_instance.changePlayMode(0)
        player = BigWorld.player()
        if player:
            self.__selfVehicleID = player.playerVehicleID
            self.__isObserverMode = 'observer' in player.vehicleTypeDescriptor.type.tags
            self.__curVehicleID = self.__selfVehicleID
        self.__cam.enable(None, False, args.get('postmortemParams'))
        self.__cam.vehicleMProv = BigWorld.player().consistentMatrices.attachedVehicleMatrix
        self.__connectToArena()
        _setCameraFluency(self.__cam.camera, self.__CAM_FLUENCY)
        self.__isEnabled = True
        BigWorld.player().consistentMatrices.onVehicleMatrixBindingChanged += self.__onMatrixBound
        if not BattleReplay.g_replayCtrl.isPlaying:
            if self.__isObserverMode:
                vehicleID = args.get('vehicleID')
                if vehicleID is None:
                    self.__switch()
                else:
                    self.__fakeSwitchToVehicle(vehicleID)
                return
            if PostMortemControlMode.getIsPostmortemDelayEnabled() and bool(args.get('bPostmortemDelay')):
                self.__postmortemDelay = PostmortemDelay(self.__cam, self.__aih.onPostmortemKillerVision, self.__onPostmortemDelayStop)
                self.__postmortemDelay.start()
            else:
                self.__switchToVehicle(None)
        g_postProcessing.enable('postmortem')
        return

    def disable(self):
        BigWorld.player().consistentMatrices.onVehicleMatrixBindingChanged -= self.__onMatrixBound
        self.__destroyPostmortemDelay()
        self.__isEnabled = False
        self.__disconnectFromArena()
        self.__cam.disable()
        self.__curVehicleID = None
        self.__selfVehicleID = None
        g_postProcessing.disable()
        return

    def handleKeyEvent(self, isDown, key, mods, event=None):
        assert self.__isEnabled
        cmdMap = CommandMapping.g_instance
        guiCtrlEnabled = BigWorld.player().isForcedGuiControlMode()
        if BigWorld.isKeyDown(Keys.KEY_CAPSLOCK) and constants.HAS_DEV_RESOURCES and isDown and key == Keys.KEY_F1:
            self.__aih.onControlModeChanged(CTRL_MODE_NAME.DEBUG, prevModeName=CTRL_MODE_NAME.POSTMORTEM, camMatrix=self.__cam.camera.matrix)
            return True
        if BigWorld.isKeyDown(Keys.KEY_CAPSLOCK) and isDown and key == Keys.KEY_F3 and (self.__videoControlModeAvailable or self.guiSessionProvider.getCtx().isPlayerObserver()):
            self.__aih.onControlModeChanged(CTRL_MODE_NAME.VIDEO, prevModeName=CTRL_MODE_NAME.POSTMORTEM, camMatrix=self.__cam.camera.matrix, curVehicleID=self.__curVehicleID)
            return True
        if cmdMap.isFired(CommandMapping.CMD_CM_POSTMORTEM_NEXT_VEHICLE, key) and isDown and not guiCtrlEnabled:
            self.__switch()
            return True
        if cmdMap.isFired(CommandMapping.CMD_CM_POSTMORTEM_SELF_VEHICLE, key) and isDown and not guiCtrlEnabled:
            self.__switch(False)
            return True
        if cmdMap.isFiredList((CommandMapping.CMD_CM_CAMERA_ROTATE_LEFT,
         CommandMapping.CMD_CM_CAMERA_ROTATE_RIGHT,
         CommandMapping.CMD_CM_CAMERA_ROTATE_UP,
         CommandMapping.CMD_CM_CAMERA_ROTATE_DOWN,
         CommandMapping.CMD_CM_INCREASE_ZOOM,
         CommandMapping.CMD_CM_DECREASE_ZOOM), key):
            dx = dy = dz = 0.0
            if cmdMap.isActive(CommandMapping.CMD_CM_CAMERA_ROTATE_LEFT):
                dx = -1.0
            if cmdMap.isActive(CommandMapping.CMD_CM_CAMERA_ROTATE_RIGHT):
                dx = 1.0
            if cmdMap.isActive(CommandMapping.CMD_CM_CAMERA_ROTATE_UP):
                dy = -1.0
            if cmdMap.isActive(CommandMapping.CMD_CM_CAMERA_ROTATE_DOWN):
                dy = 1.0
            if cmdMap.isActive(CommandMapping.CMD_CM_INCREASE_ZOOM):
                dz = 1.0
            if cmdMap.isActive(CommandMapping.CMD_CM_DECREASE_ZOOM):
                dz = -1.0
            self.__cam.update(dx, dy, dz, True, True, False if dx == dy == dz == 0.0 else True)
            return True
        return False

    def handleMouseEvent(self, dx, dy, dz):
        assert self.__isEnabled
        GUI.mcursor().position = self.__aimOffset
        if self.__postmortemDelay is not None:
            return True
        else:
            self.__cam.update(dx, dy, mathUtils.clamp(-1, 1, dz))
            return True

    def onRecreateDevice(self):
        pass

    def selectPlayer(self, vehID):
        self.__switchToVehicle(vehID)

    def selectViewPoint(self, pointID):
        self.__switchToViewpoint(pointID)

    def setGUIVisible(self, isVisible):
        pass

    def __destroyPostmortemDelay(self):
        if self.__postmortemDelay is not None:
            self.__postmortemDelay.destroy()
            self.__postmortemDelay = None
        return

    def __onPostmortemDelayStop(self):
        self.__cam.vehicleMProv = BigWorld.player().consistentMatrices.attachedVehicleMatrix
        self.__destroyPostmortemDelay()
        self.__switchToVehicle(None)
        return

    def __fakeSwitchToVehicle(self, vehicleID):
        if self.__postmortemDelay is not None:
            return
        else:
            self.__doPreBind()
            self.onSwitchViewpoint(vehicleID, Math.Vector3(0.0, 0.0, 0.0))
            return

    def __switchToViewpoint(self, toId):
        if self.__postmortemDelay is not None:
            return
        else:
            assert isinstance(toId, int)
            self.__doPreBind()
            self.guiSessionProvider.shared.viewPoints.selectViewPoint(toId)
            return

    def __switch(self, isNext=True):
        if self.__postmortemDelay is not None:
            return
        else:
            assert isinstance(isNext, bool)
            self.__doPreBind()
            self.guiSessionProvider.shared.viewPoints.switch(isNext)
            return

    def __switchToVehicle(self, toId=None):
        if self.__postmortemDelay is not None:
            return
        else:
            assert not toId or isinstance(toId, int) and toId >= 0
            self.__doPreBind()
            self.__changeVehicle(toId)
            self.guiSessionProvider.shared.viewPoints.selectVehicle(toId)
            return

    def __doPreBind(self):
        if self.__curVehicleID is not None:
            vehicle = BigWorld.entity(self.__curVehicleID)
            if vehicle is not None:
                self.__cam.removeVehicleToCollideWith(vehicle)
        return

    def onSwitchViewpoint(self, vehicleID, cameraPos):
        player = BigWorld.player()
        replayCtrl = BattleReplay.g_replayCtrl
        self.__curVehicleID = vehicleID if vehicleID != -1 else self.__selfVehicleID
        self.__changeVehicle(vehicleID)
        if self.__curVehicleID != player.playerVehicleID and self.__curVehicleID is not None and BigWorld.entity(self.__curVehicleID) is None and not replayCtrl.isPlaying and not self.__isObserverMode and player.arena.positions.get(self.__curVehicleID) is None:
            self.__switch()
        return

    def __changeVehicle(self, vehicleID):
        """
        Do all the job to switch to another vehicle in postmortem:
        - calls postmortem event
        - sets vehicle in state controller and resets other controllers in guiSessionProvider
        - calls camera update event
        :param vehicleID: controlling vehicle ID
        """
        self.__aih.onPostmortemVehicleChanged(vehicleID)
        self.guiSessionProvider.switchVehicle(vehicleID)
        if vehicleID in BigWorld.entities.keys():
            self.__aih.onCameraChanged(CTRL_MODE_NAME.POSTMORTEM, vehicleID)

    def __onPeriodChange(self, period, *args):
        if period != constants.ARENA_PERIOD.AFTERBATTLE:
            return
        elif self.__isObserverMode:
            return
        else:
            self.__switchToVehicle(None)
            return

    def __onVehicleLeaveWorld(self, vehicle):
        if vehicle.id == self.__curVehicleID:
            vehicleID = BigWorld.player().playerVehicleID
            vehicle = BigWorld.entities.get(vehicleID)
            if vehicle is not None and 'observer' in vehicle.typeDescriptor.type.tags:
                return
            self.__switchToVehicle(None)
        return

    def __connectToArena(self):
        player = BigWorld.player()
        player.arena.onPeriodChange += self.__onPeriodChange
        player.onVehicleLeaveWorld += self.__onVehicleLeaveWorld

    def __disconnectFromArena(self):
        player = BigWorld.player()
        player.arena.onPeriodChange -= self.__onPeriodChange
        player.onVehicleLeaveWorld -= self.__onVehicleLeaveWorld

    def __onMatrixBound(self, isStatic):
        if isStatic:
            return
        else:
            vehicle = BigWorld.player().vehicle
            if vehicle is None or self.__curVehicleID != vehicle.id or not vehicle.inWorld:
                return
            self.__cam.addVehicleToCollideWith(vehicle)
            replayCtrl = BattleReplay.g_replayCtrl
            if replayCtrl.isRecording:
                replayCtrl.setPlayerVehicleID(self.__curVehicleID)
            self.__cam.vehicleMProv = BigWorld.player().consistentMatrices.attachedVehicleMatrix
            self.__aih.onCameraChanged(CTRL_MODE_NAME.POSTMORTEM, self.__curVehicleID)
            return

    def isSelfVehicle(self):
        return self.__curVehicleID == self.__selfVehicleID

    @property
    def curVehicleID(self):
        return self.__curVehicleID


class _ShellingControl():
    __TARGET_MODEL_FILE_NAME = 'cat/models/position_gizmo.model'
    __TARGET_POINTER_FILE_NAME = 'cat/target_pointer.dds'

    def __init__(self, camera):
        self.__bEnable = False
        self.__shellingObject = None
        self.__camera = camera
        self.__targetPointer = self.__createTargetPointer()
        self.__targetModel = self.__createTargetModel()
        self.__targetModelVisible = False
        self.__targetModelAutoUpdateCallbackID = None
        self.__targetModelAutoUpdateOnGetMatrix = None
        return

    def destroy(self):
        self.setEnable(False)
        if self.__shellingObject is not None:
            self.__shellingObject.deselectTarget()
            self.installShellingObject(None)
        self.__createTargetPointer(bDelete=True)
        self.__targetModelVisible = None
        self.__createTargetModel(bDelete=True)
        self.__camera = None
        return

    def setEnable(self, value):
        if self.__bEnable == value:
            return
        if value:
            self.__showTargetPointer_directly(True)
            self.__showTargetModel_directly(self.__targetModelVisible)
        else:
            self.__showTargetPointer_directly(False)
            self.__showTargetModel_directly(False)
        self.__bEnable = value

    def installShellingObject(self, shellingObject):
        if shellingObject is not None:
            self.installShellingObject(None)
            self.__shellingObject = shellingObject
            self.__shellingObject._setCamera(self.__camera.camera)
        elif self.__shellingObject is not None:
            self.__shellingObject._setCamera(None)
            self.__shellingObject = None
        return

    def getShellingObjectInstalled(self):
        return self.__shellingObject is not None

    def getShellingObject(self):
        return self.__shellingObject

    def showTargetPointer(self, value):
        self.__showTargetPointer_directly(value)

    def showTargetModel(self, value):
        self.__targetModelVisible = value
        if self.__bEnable:
            self.__showTargetModel_directly(value)

    def setTargetModelMatrix(self, worldMatrix):
        self.__targetModel.motors[0].signal = Math.Matrix(worldMatrix)

    def setTargetModelAutoUpdate(self, onGetMatrix=None):
        if self.__targetModelAutoUpdateCallbackID is not None:
            BigWorld.cancelCallback(self.__targetModelAutoUpdateCallbackID)
            self.__targetModelAutoUpdateCallbackID = None
        self.__targetModelAutoUpdateOnGetMatrix = onGetMatrix
        if self.__targetModelAutoUpdateOnGetMatrix is not None:
            self.__targetModelAutoUpdateCallbackID = BigWorld.callback(0.001, self.__targetModelAutoUpdateCallbackFunc)
        return

    def recreate(self):
        isVisible = self.__targetPointer.visible
        self.__createTargetPointer(bDelete=True)
        self.__targetPointer = self.__createTargetPointer()
        self.__targetPointer.visible = isVisible
        isVisible = self.__targetModel.visible
        self.__createTargetModel(bDelete=True)
        self.__targetModel = self.__createTargetModel()
        self.__targetModel.visible = isVisible

    def handleKeyEvent(self, isDown, key, mods, event=None):
        if self.__shellingObject is not None:
            if key == Keys.KEY_LEFTMOUSE and isDown:
                self.__shellingObject.shoot()
                return True
            if key == Keys.KEY_RIGHTMOUSE and isDown:
                self.__shellingObject.selectTarget()
                return True
            if key == Keys.KEY_MIDDLEMOUSE and isDown:
                self.__shellingObject.deselectTarget()
                return True
        return False

    def __targetModelAutoUpdateCallbackFunc(self):
        self.__targetModelAutoUpdateCallbackID = None
        nextCallbackInterval = 0.001
        try:
            newMatrix = self.__targetModelAutoUpdateOnGetMatrix()
            if newMatrix is not None:
                self.__targetModel.motors[0].signal = Math.Matrix(newMatrix)
            else:
                nextCallbackInterval = 2.0
        except:
            nextCallbackInterval = 2.0
            LOG_DEBUG('<_targetModelAutoUpdateCallbackFunc>: target model is not updated')

        self.__targetModelAutoUpdateCallbackID = BigWorld.callback(nextCallbackInterval, self.__targetModelAutoUpdateCallbackFunc)
        return

    def __createTargetPointer(self, bDelete=False):
        result = None
        if not bDelete:
            result = GUI.Simple(_ShellingControl.__TARGET_POINTER_FILE_NAME)
            result.position[2] = 0.7
            result.size = (2, 2)
            result.materialFX = 'BLEND_INVERSE_COLOUR'
            result.filterType = 'LINEAR'
            result.visible = False
            GUI.addRoot(result)
        elif self.__targetPointer is not None:
            GUI.delRoot(self.__targetPointer)
            self.__targetPointer = None
        return result

    def __createTargetModel(self, bDelete=False):
        result = None
        if not bDelete:
            result = BigWorld.Model(_ShellingControl.__TARGET_MODEL_FILE_NAME)
            result.addMotor(BigWorld.Servo(Math.Matrix()))
            result.visible = False
            BigWorld.addModel(result)
        elif self.__targetModel is not None:
            self.setTargetModelAutoUpdate(None)
            BigWorld.delModel(self.__targetModel)
            self.__targetModel = None
        return result

    def __showTargetPointer_directly(self, value):
        self.__targetPointer.visible = value

    def __showTargetModel_directly(self, value):
        self.__targetModel.visible = value


class _PlayerGunInformation(object):

    @staticmethod
    def getCurrentShotInfo():
        player = BigWorld.player()
        gunRotator = player.gunRotator
        shotDesc = player.getVehicleDescriptor().shot
        gunMat = AimingSystems.getPlayerGunMat(gunRotator.turretYaw, gunRotator.gunPitch)
        position = gunMat.translation
        velocity = gunMat.applyVector(Math.Vector3(0, 0, shotDesc.speed))
        return (position, velocity, Math.Vector3(0, -shotDesc.gravity, 0))

    @staticmethod
    def updateMarkerDispersion(spgMarkerComponent, isServerAim=False):
        dispersionAngle = BigWorld.player().gunRotator.dispersionAngle
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying and replayCtrl.isClientReady:
            d, s = replayCtrl.getSPGGunMarkerParams()
            if d != -1.0 and s != -1.0:
                dispersionAngle = d
        elif replayCtrl.isRecording:
            if replayCtrl.isServerAim and isServerAim:
                replayCtrl.setSPGGunMarkerParams(dispersionAngle, 0.0)
            elif not isServerAim:
                replayCtrl.setSPGGunMarkerParams(dispersionAngle, 0.0)
        spgMarkerComponent.setupConicDispersion(dispersionAngle)

    @staticmethod
    def updateServerMarkerDispersion(spgMarkerComponent):
        _PlayerGunInformation.updateMarkerDispersion(spgMarkerComponent, True)


class _MouseVehicleRotator():
    ROTATION_ACTIVITY_INTERVAL = 0.2

    def __init__(self):
        self.__rotationState = 0
        self.__cbIDActivity = None
        return

    def destroy(self):
        self.unforceRotation(isDestroy=True)

    def handleMouse(self, dx):
        import Avatar
        player = BigWorld.player()
        if not isinstance(player, Avatar.PlayerAvatar):
            return
        else:
            cmdMap = CommandMapping.g_instance
            if not cmdMap.isActive(CommandMapping.CMD_MOVE_FORWARD_SPEC):
                return
            if dx * self.__rotationState > 0:
                return
            self.__rotationState = mathUtils.clamp(-1, 1, dx)
            bStartRotation = dx != 0
            if self.__cbIDActivity is not None:
                BigWorld.cancelCallback(self.__cbIDActivity)
                self.__cbIDActivity = None
            if bStartRotation:
                self.__cbIDActivity = BigWorld.callback(self.ROTATION_ACTIVITY_INTERVAL, self.__cbActivity)
            if bStartRotation:
                forceMask = 12
                if dx < 0:
                    forceFlags = 4
                if dx > 0:
                    forceFlags = 8
            else:
                forceMask = 0
                forceFlags = 204
            BigWorld.player().moveVehicleByCurrentKeys(bStartRotation, forceFlags, forceMask)
            return

    def unforceRotation(self, isDestroy=False):
        self.__rotationState = 0
        if self.__cbIDActivity is not None:
            BigWorld.cancelCallback(self.__cbIDActivity)
            self.__cbIDActivity = None
        if not isDestroy:
            import Avatar
            player = BigWorld.player()
            if not isinstance(player, Avatar.PlayerAvatar):
                return
            player.moveVehicleByCurrentKeys(False)
        return

    def __cbActivity(self):
        self.__cbIDActivity = None
        self.unforceRotation()
        return


def getFocalPoint():
    dir, start = cameras.getWorldRayAndPoint(0, 0)
    end = start + dir.scale(100000.0)
    point = collideDynamicAndStatic(start, end, (BigWorld.player().playerVehicleID,), 0)
    if point is not None:
        return point[0]
    else:
        return AimingSystems.shootInSkyPoint(start, dir)
        return


def _sign(val):
    if val > 0:
        return 1.0
    elif val < 0:
        return -1.0
    else:
        return 0.0


def _buildTexCoord(vec4, textureSize):
    out = ((vec4[0] / textureSize[0], vec4[1] / textureSize[1]),
     (vec4[0] / textureSize[0], vec4[3] / textureSize[1]),
     (vec4[2] / textureSize[0], vec4[3] / textureSize[1]),
     (vec4[2] / textureSize[0], vec4[1] / textureSize[1]))
    return out


def _setCameraFluency(cam, value):
    pass


def _swap(data, index1, index2):
    if index1 == index2:
        return
    tmp = data[index1]
    data[index1] = data[index2]
    data[index2] = tmp
