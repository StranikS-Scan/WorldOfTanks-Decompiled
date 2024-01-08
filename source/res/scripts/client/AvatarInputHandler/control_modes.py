# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/control_modes.py
import logging
import time
import weakref
from collections import namedtuple
from functools import partial
import BigWorld
import GUI
import Keys
import Math
import ResMgr
import BattleReplay
import CommandMapping
import SoundGroups
import TriggersManager
import VideoCamera
import cameras
import constants
import math_utils
from AimingSystems import getShotTargetInfo
from AimingSystems.magnetic_aim import magneticAimProcessor, MagneticAimSettings
from AvatarInputHandler import AimingSystems, aih_global_binding, gun_marker_ctrl
from AvatarInputHandler.DynamicCameras.camera_switcher import SwitchToPlaces
from AvatarInputHandler.StrategicCamerasInterpolator import StrategicCamerasInterpolator
from AvatarInputHandler.spg_marker_helpers.spg_marker_helpers import getSPGShotResult, getSPGShotFlyTime
from DynamicCameras import SniperCamera, StrategicCamera, ArcadeCamera, ArtyCamera, DualGunCamera, OnlyArtyCamera, AssaultCamera
from PostmortemDelay import PostmortemDelay
from ProjectileMover import collideDynamicAndStatic
from TriggersManager import TRIGGER_TYPE
from Vehicle import Vehicle as VehicleEntity
from account_helpers.AccountSettings import AccountSettings, WHEELED_DEATH_DELAY_COUNT, LAST_ARTY_CTRL_MODE
from account_helpers.settings_core.settings_constants import SPGAim, SPGAimEntranceModeOptions, GAME
from aih_constants import CTRL_MODE_NAME, GUN_MARKER_FLAG, STRATEGIC_CAMERA, CTRL_MODES, CHARGE_MARKER_STATE
from constants import AIMING_MODE
from constants import VEHICLE_SIEGE_STATE
from debug_utils import LOG_DEBUG, LOG_WARNING, LOG_CURRENT_EXCEPTION
from gui import GUI_SETTINGS, g_repeatKeyHandlers
from gui.battle_control import avatar_getter, vehicle_getter
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
from helpers import dependency, uniprof
from items import _xml
from shared_utils import findFirst
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)
_WHEELED_VEHICLE_POSTMORTEM_DELAY = 3

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

    def alwaysReceiveKeyEvents(self, isDown=True):
        return False

    def handleMouseEvent(self, dx, dy, dz):
        pass

    def setGunMarkerFlag(self, positive, bit):
        pass

    def updateGunMarker(self, markerType, pos, direction, size, relaxTime, collData):
        pass

    def updateTargetedEnemiesForGuns(self, collDataList):
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
        return False

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

    def enableSwitchAutorotationMode(self, triggeredByKey=False):
        return not (triggeredByKey and BigWorld.player().isVehicleMoving())

    def setForcedGuiControlMode(self, enable):
        pass

    def onAutorotationChanged(self, value):
        pass


class _GunControlMode(IControlMode):
    isEnabled = property(lambda self: self._isEnabled)
    aimingMode = property(lambda self: self._aimingMode)
    camera = property(lambda self: self._cam)
    curVehicleID = property(lambda self: self.__curVehicleID)
    _aimOffset = aih_global_binding.bindRW(aih_global_binding.BINDING_ID.AIM_OFFSET)
    __slots__ = ('_aih', '_defaultOffset', '_cameraTransitionDurations', '_gunMarker', '_isEnabled', '_cam', '_aimingMode', '_canShot', '_currentMode', '_lockedDown', '__curVehicleID')

    def __init__(self, dataSection, avatarInputHandler, mode=CTRL_MODE_NAME.ARCADE, isStrategic=False):
        self._aih = weakref.proxy(avatarInputHandler)
        self._defaultOffset = dataSection.readVector2('defaultOffset')
        self._cameraTransitionDurations = _readCameraTransitionSettings(dataSection['camera'])
        self._gunMarker = gun_marker_ctrl.createGunMarker(isStrategic)
        self._isEnabled = False
        self._cam = None
        self._aimingMode = 0
        self._canShot = False
        self._currentMode = mode
        self._lockedDown = False
        self.__curVehicleID = None
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
        uniprof.enterToRegion('avatar.control_mode.{}'.format(self._currentMode))
        self._isEnabled = True
        self._aimOffset = self._defaultOffset
        self._aimingMode = args.get('aimingMode', self._aimingMode)
        self._gunMarker.enable()
        self.__curVehicleID = args.get('curVehicleID')
        if self.__curVehicleID is None:
            self.__curVehicleID = BigWorld.player().playerVehicleID
        return

    def disable(self):
        self._isEnabled = False
        self._cam.disable()
        self._gunMarker.disable()
        uniprof.exitFromRegion('avatar.control_mode.{}'.format(self._currentMode))
        self.__curVehicleID = None
        return

    def destroy(self):
        self._gunMarker.destroy()
        self._aih = None
        self._cam.destroy()
        self._cam = None
        return

    def setGunMarkerFlag(self, positive, bit):
        self._gunMarker.setFlag(positive, bit)

    def updateGunMarker(self, markerType, pos, direction, size, relaxTime, collData):
        self._gunMarker.update(markerType, pos, direction, size, relaxTime, collData)

    def setAimingMode(self, enable, mode):
        if enable:
            self._aimingMode |= mode
        else:
            self._aimingMode &= -1 - mode

    def resetAimingMode(self):
        self._aimingMode = 0

    def getDesiredShotPoint(self, ignoreAimingMode=False):
        return self._cam.aimingSystem.getDesiredShotPoint() if self._aimingMode == 0 and self._cam is not None or ignoreAimingMode else None

    def getAimingMode(self, mode):
        return self._aimingMode & mode == mode

    def onRecreateDevice(self):
        self._gunMarker.onRecreateDevice()

    def updateShootingStatus(self, canShot):
        self._canShot = canShot


class CameraLocationPoint(object):

    def __init__(self, name, matrix):
        self.name = name
        self.matrix = matrix

    @staticmethod
    def keyForSortLocationPoint(point):
        return point.name


class VideoCameraControlMode(_GunControlMode):
    __locationPoints = []

    def __init__(self, dataSection, avatarInputHandler):
        super(VideoCameraControlMode, self).__init__(dataSection, avatarInputHandler)
        self.__prevModeName = None
        self.__previousArgs = None
        self.__isGunMarkerEnabled = False
        cameraDataSection = dataSection['camera'] if dataSection is not None else ResMgr.DataSection('camera')
        self.__showGunMarkerKey = getattr(Keys, cameraDataSection.readString('keyShowGunMarker', ''), None)
        self._createCamera(cameraDataSection)
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
        self.__previousArgs = args
        self.__prevModeName = args.get('prevModeName')
        self._cam.enable(**args)

    def getDesiredShotPoint(self, ignoreAimingMode=False):
        return None

    def setForcedGuiControlMode(self, enable):
        if enable:
            self._cam.resetMovement()

    def isSelfVehicle(self):
        return False

    def handleKeyEvent(self, isDown, key, mods, event=None):
        if self._cam.handleKeyEvent(key, isDown):
            return True
        elif BigWorld.isKeyDown(Keys.KEY_CAPSLOCK) and isDown and key == Keys.KEY_F3 and self.__prevModeName is not None:
            if not self._aih.isControlModeChangeAllowed():
                return
            self._aih.onControlModeChanged(self.__prevModeName, **self.__previousArgs)
            return True
        else:
            if isDown:
                if self.__showGunMarkerKey is not None and self.__showGunMarkerKey == key:
                    self.__isGunMarkerEnabled = not self.__isGunMarkerEnabled
                    self._gunMarker.setFlag(self.__isGunMarkerEnabled, GUN_MARKER_FLAG.VIDEO_MODE_ENABLED)
                    return True
            return False

    def teleport(self, index):
        self._cam.setViewMatrix(self.__locationPoints[index - 1].matrix)

    def teleportByName(self, name):
        for point in self.__locationPoints:
            if point.name == name:
                self._cam.setViewMatrix(point.matrix)
                return

    def handleMouseEvent(self, dx, dy, dz):
        self._cam.handleMouseEvent(dx, dy, dz)
        return True

    def onPostmortemActivation(self, eMode, **kwargs):
        self.__prevModeName = eMode
        self.__previousArgs = kwargs

    def _createCamera(self, cameraDataSection):
        self._cam = VideoCamera.VideoCamera(cameraDataSection)


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
        import Cat
        Cat.Tasks.VideoEngineer.SetEnable(True)
        self.__videoControl = Cat.Tasks.VideoEngineer.VideoControl(self.__cam)
        self.__videoControl.setEnable(True)
        self.__isEnabled = True

    def disable(self):
        self.__isEnabled = False
        if self.__videoControl is not None:
            self.__videoControl.setEnable(False)
            self.__videoControl.destroy()
            self.__videoControl = None
        self.__cam.disable()
        return

    def handleKeyEvent(self, isDown, key, mods, event=None):
        if key == Keys.KEY_SYSRQ:
            return False
        if BigWorld.isKeyDown(Keys.KEY_CAPSLOCK) and constants.HAS_DEV_RESOURCES and isDown and key == Keys.KEY_F1:
            self.__aih.onControlModeChanged(self.__prevModeName)
            return True
        return True if self.__videoControl.handleKeyEvent(isDown, key, mods, event) else self.__cam.handleKey(event)

    def handleMouseEvent(self, dx, dy, dz):
        GUI.mcursor().position = (0, 0)
        return self.__videoControl.handleMouseEvent(dx, dy, dz)

    def getDesiredShotPoint(self, ignoreAimingMode=False):
        return None

    def updateShootingStatus(self, canShot):
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
        if enable:
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
        if BigWorld.isKeyDown(Keys.KEY_CAPSLOCK) and constants.HAS_DEV_RESOURCES and isDown and key == Keys.KEY_F2:
            self.__aih.onControlModeChanged('arcade')
        self.__shellingControl.handleKeyEvent(isDown, key, mods, event)
        return self.__cam.handleKey(event)

    def handleMouseEvent(self, dx, dy, dz):
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
    __settingsCore = dependency.descriptor(ISettingsCore)
    postmortemCamParams = property(lambda self: (self._cam.angles, self._cam.camera.pivotMaxDist))
    __chargeMarkerState = aih_global_binding.bindRW(aih_global_binding.BINDING_ID.CHARGE_MARKER_STATE)

    def __init__(self, dataSection, avatarInputHandler):
        super(ArcadeControlMode, self).__init__(dataSection, avatarInputHandler, mode=CTRL_MODE_NAME.ARCADE)
        self._setupCamera(dataSection)
        self.__mouseVehicleRotator = _MouseVehicleRotator()
        self.__videoControlModeAvailable = dataSection.readBool('videoModeAvailable', constants.HAS_DEV_RESOURCES)
        self.__videoControlModeAvailable &= BattleReplay.g_replayCtrl.isPlaying or constants.HAS_DEV_RESOURCES
        self.__lockKeyPressedTime = None
        self.__lockKeyUpTime = None
        self.__simpleAimTarget = None
        self.__magneticAimTarget = None
        return

    def create(self):
        self._cam.create(self.onChangeControlModeByScroll)
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
        self._cam.enable(args.get('preferredPos'), args.get('closesDist', False), turretYaw=args.get('turretYaw', None), gunPitch=args.get('gunPitch', None), initialVehicleMatrix=args.get('initialVehicleMatrix', None), arcadeState=args.get('arcadeState', None), camTransitionParams=args.get('camTransitionParams', {}))
        player = BigWorld.player()
        if player.isObserver() and not player.observerSeesAll():
            player.updateObservedVehicleData()
        vehicle = player.getVehicleAttached()
        if vehicle is not None and not vehicle.isUpgrading:
            GUI.mcursor().position = self._aimOffset
        cursorX, cursorY = self._aimOffset
        GUI.syncMousePosition(cursorX, cursorY)
        return

    def handleKeyEvent(self, isDown, key, mods, event=None):
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
            if not self._aih.isControlModeChangeAllowed():
                return
            self._aih.onControlModeChanged(CTRL_MODE_NAME.VIDEO, prevModeName=CTRL_MODE_NAME.ARCADE, camMatrix=self._cam.camera.matrix)
            return True
        else:
            isMagneticAimEnabled = self._aih.isMagneticAimEnabled
            if isMagneticAimEnabled and cmdMap.isFired(CommandMapping.CMD_CM_LOCK_TARGET, key):
                if isDown:
                    self.__lockKeyPressedTime = time.time()
                else:
                    self.__lockKeyUpTime = time.time()
            if self._aih.dualGunControl and self._aih.dualGunControl.handleKeyEvent(isDown, key, mods, event):
                return True
            isFiredFreeCamera = cmdMap.isFired(CommandMapping.CMD_CM_FREE_CAMERA, key)
            isFiredLockTarget = cmdMap.isFired(CommandMapping.CMD_CM_LOCK_TARGET, key)
            if isFiredFreeCamera:
                self.setAimingMode(isDown, AIMING_MODE.USER_DISABLED)
            if isFiredLockTarget and isDown:
                BigWorld.player().autoAim(BigWorld.target())
                self.__simpleAimTarget = BigWorld.target()
            if isMagneticAimEnabled and isFiredLockTarget and not isDown:
                if self.__lockKeyPressedTime is not None and self.__lockKeyUpTime is not None:
                    if self.__lockKeyUpTime - self.__lockKeyPressedTime <= MagneticAimSettings.KEY_DELAY_SEC:
                        self.__magneticAimTarget = magneticAimProcessor(self.__simpleAimTarget, self.__magneticAimTarget)
            if cmdMap.isFired(CommandMapping.CMD_CM_SHOOT, key) and isDown:
                BigWorld.player().shoot()
                return True
            elif cmdMap.isFired(CommandMapping.CMD_CM_LOCK_TARGET_OFF, key) and isDown:
                BigWorld.player().autoAim(None)
                return True
            elif cmdMap.isFired(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION, key) and isDown:
                self._aih.switchAutorotation(True)
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
            if cmdMap.isFired(CommandMapping.CMD_CM_ALTERNATE_MODE, key) and isDown:
                ownVehicle = BigWorld.entity(BigWorld.player().playerVehicleID)
                if ownVehicle and ownVehicle.isStarted:
                    self.__activateAlternateMode()
                    return True
            return False

    def handleMouseEvent(self, dx, dy, dz):
        GUI.mcursor().position = self._aimOffset
        if not self._aih.isObserverFPV:
            self._cam.update(dx, dy, math_utils.clamp(-1, 1, dz))
            self.__mouseVehicleRotator.handleMouse(dx)
        return True

    def onMinimapClicked(self, worldPos):
        if not self._aih.isSPG:
            return False
        self.__activateAlternateMode(worldPos)
        return True

    def onChangeControlModeByScroll(self):
        if not _isEnabledChangeModeByScroll(self._cam, self._aih):
            return
        else:
            self.__activateAlternateMode(pos=None, bByScroll=True)
            return

    def setForcedGuiControlMode(self, enable):
        if enable:
            self._cam.update(0, 0, 0, False, False)
            if self._aih.dualGunControl:
                self._aih.dualGunControl.cancelShootKeyEvent()

    def updateTargetedEnemiesForGuns(self, gunsData):
        self.__chargeMarkerState = CHARGE_MARKER_STATE.VISIBLE if any(gunsData) else CHARGE_MARKER_STATE.DIMMED

    def alwaysReceiveKeyEvents(self, isDown=True):
        return True if self._aih.dualGunControl is not None and isDown is False else False

    def _setupCamera(self, dataSection):
        self._cam = ArcadeCamera.ArcadeCamera(dataSection['camera'], defaultOffset=self._defaultOffset)

    def __getAssaultSpgTargetPos(self):
        pos = None
        normal = Math.Vector3(0, -1, 0)
        cursorPosition = GUI.mcursor().position
        ray, wpoint = cameras.getWorldRayAndPoint(cursorPosition.x, cursorPosition.y)
        ray.normalise()
        res = BigWorld.wg_collideDynamicStatic(BigWorld.player().spaceID, wpoint, wpoint + ray * 5500, 128, BigWorld.player().playerVehicleID, -1, 0)
        if res is not None:
            pos = res[0]
            normal = res[6]
        waterCollisionDist = BigWorld.wg_collideWater(wpoint, wpoint + ray * 5500, False)
        if waterCollisionDist > -1.0 and (pos is None or waterCollisionDist < (pos - wpoint).length):
            pos = wpoint + ray * waterCollisionDist
            normal = Math.Vector3(0, 1, 0)
        if pos is None:
            pos = self.camera.aimingSystem.getDesiredShotPoint()
            position, velocity, gravity = BigWorld.player().gunRotator.getShotParams(pos, ignoreYawLimits=True)
            hitPoint = BigWorld.wg_simulateProjectileTrajectory(position, velocity, gravity, constants.SERVER_TICK_LENGTH, constants.SHELL_TRAJECTORY_EPSILON_CLIENT, 128, 0)
            checkWaterDirection = Math.Vector3(0.0, -1.0, 0.0)
            if hitPoint is not None:
                pos = hitPoint[1]
                projectileDir = hitPoint[2]
                projectileDir.normalise()
                checkWaterDirection = projectileDir
                hit = BigWorld.wg_collideDynamicStatic(BigWorld.player().spaceID, pos - projectileDir.scale(0.1), pos + projectileDir.scale(0.1), 128, BigWorld.player().playerVehicleID, -1, 0)
                if hit is not None:
                    normal = hit[6]
            p0 = pos + checkWaterDirection.scale(1000.0)
            p1 = pos - checkWaterDirection.scale(1000.0)
            waterDist = BigWorld.wg_collideWater(p0, p1, False)
            if waterDist > 0 and waterDist > (pos - p0).length:
                pos = p0 - checkWaterDirection.scale(waterDist)
                normal = Math.Vector3(0, 1, 0)
        return (pos, normal)

    def __activateAlternateMode(self, pos=None, bByScroll=False):
        ownVehicle = BigWorld.entity(BigWorld.player().playerVehicleID)
        if ownVehicle is not None and ownVehicle.isStarted and avatar_getter.isVehicleBarrelUnderWater() or BigWorld.player().isGunLocked or BigWorld.player().isObserver():
            return
        elif self._aih.isAssaultSPG:
            self._cam.update(0, 0, 0, False, False)
            equipmentID = None
            normal = Math.Vector3(0, -1, 0)
            if BattleReplay.isPlaying():
                mode = BattleReplay.g_replayCtrl.getControlMode()
                equipmentID = BattleReplay.g_replayCtrl.getEquipmentId()
            else:
                mode = CTRL_MODE_NAME.ASSAULT_SPG
            if pos is None:
                pos, normal = self.__getAssaultSpgTargetPos()
            self._aih.onControlModeChanged(mode, preferredPos=pos, hitNormal=normal, aimingMode=self._aimingMode, saveDist=True, equipmentID=equipmentID)
            return
        elif self._aih.isSPG and not bByScroll or self._aih.isOnlyArty:
            self._cam.update(0, 0, 0, False, False)
            equipmentID = None
            if BattleReplay.isPlaying():
                mode = BattleReplay.g_replayCtrl.getControlMode()
                pos = BattleReplay.g_replayCtrl.getGunMarkerPos()
                equipmentID = BattleReplay.g_replayCtrl.getEquipmentId()
            else:
                mode = CTRL_MODE_NAME.SPG_ONLY_ARTY_MODE if self._aih.isOnlyArty else self.__getSpgAlternativeMode()
                if pos is None:
                    pos = self.camera.aimingSystem.getDesiredShotPoint()
                    if pos is None:
                        pos = self._gunMarker.getPosition()
                    vehicle = BigWorld.player().getVehicleAttached()
                    checkHitPoint = True
                    if ownVehicle.model is not None:
                        gunNode = ownVehicle.model.node('gun')
                        if gunNode is not None:
                            gunPosition = Math.Matrix(gunNode).translation
                            checkHitPoint = BigWorld.player().arena.isPointInsideArenaBB(gunPosition)
                    if checkHitPoint:
                        hitPoint, _ = getShotTargetInfo(vehicle, pos, BigWorld.player().gunRotator)
                        if vehicle.position.distTo(hitPoint) < vehicle.position.distTo(pos):
                            pos = hitPoint
            self._aih.onControlModeChanged(mode, preferredPos=pos, aimingMode=self._aimingMode, saveDist=True, equipmentID=equipmentID)
            return
        elif not self._aih.isSPG:
            self._cam.update(0, 0, 0, False, False)
            if BattleReplay.isPlaying() and BigWorld.player().isGunLocked:
                mode = BattleReplay.g_replayCtrl.getControlMode()
                desiredShotPoint = BattleReplay.g_replayCtrl.getGunMarkerPos()
                equipmentID = BattleReplay.g_replayCtrl.getEquipmentId()
            else:
                mode = CTRL_MODE_NAME.DUAL_GUN if self._aih.isDualGun else CTRL_MODE_NAME.SNIPER
                equipmentID = None
                desiredShotPoint = self.camera.aimingSystem.getDesiredShotPoint()
            self._aih.onControlModeChanged(mode, preferredPos=desiredShotPoint, aimingMode=self._aimingMode, saveZoom=not bByScroll, equipmentID=equipmentID)
            return
        else:
            return

    def __getSpgAlternativeMode(self):
        value = self.__settingsCore.getSetting(SPGAim.AIM_ENTRANCE_MODE)
        option = SPGAimEntranceModeOptions.SETTINGS_OPTIONS[value]
        if option == SPGAimEntranceModeOptions.LAST:
            return AccountSettings.getSettings(LAST_ARTY_CTRL_MODE)
        return CTRL_MODE_NAME.STRATEGIC if option == SPGAimEntranceModeOptions.STRATEGIC else CTRL_MODE_NAME.ARTY


class _TrajectoryControlMode(_GunControlMode):
    strategicCamera = aih_global_binding.bindRW(aih_global_binding.BINDING_ID.STRATEGIC_CAMERA)
    spgShotsIndicatorState = aih_global_binding.bindRW(aih_global_binding.BINDING_ID.SPG_SHOTS_INDICATOR_STATE)
    __interpolator = StrategicCamerasInterpolator()
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __settingsCore = dependency.descriptor(ISettingsCore)
    _FLOAT_SQUARE_ERROR = 1e-06
    _SWITCH_SOUND = {CTRL_MODE_NAME.ARTY: 'artillery_camera_switcher_trajectory_view',
     CTRL_MODE_NAME.STRATEGIC: 'artillery_camera_switcher_top_view'}
    __slots__ = ('__trajectoryDrawer', '__dataUpdateCallback', '__updateInterval', '__controllingVehicleID', '__targetVehicleID', '_nextControlMode')

    def __init__(self, dataSection, avatarInputHandler, modeName, trajectoryUpdateInterval):
        super(_TrajectoryControlMode, self).__init__(dataSection, avatarInputHandler, modeName, True)
        self.__trajectoryDrawer = BigWorld.wg_trajectory_drawer()
        self.__dataUpdateCallback = None
        self.__updateInterval = trajectoryUpdateInterval
        self.__controllingVehicleID = None
        self.__targetVehicleID = None
        self._nextControlMode = modeName
        return

    def create(self):
        self._cam.create(self.onChangeControlModeByScroll)
        super(_TrajectoryControlMode, self).create()
        self.__initTrajectoryDrawer()
        self.__interpolator.onInterpolationStart += self.__onInterpolationStart
        self.__interpolator.onInterpolationStop += self.__onInterpolationStop

    def destroy(self):
        self.disable()
        self.__delTrajectoryDrawer()
        self.__interpolator.onInterpolationStart -= self.__onInterpolationStart
        self.__interpolator.onInterpolationStop -= self.__onInterpolationStop
        super(_TrajectoryControlMode, self).destroy()

    def enable(self, **args):
        super(_TrajectoryControlMode, self).enable(**args)
        SoundGroups.g_instance.changePlayMode(2)
        self._cam.enable(args['preferredPos'], args['saveDist'], args.get('switchToPos'), args.get('switchToPlace'))
        self.__trajectoryDrawer.visible = self._aih.isGuiVisible
        target = BigWorld.target()
        self.__targetVehicleID = target.id if isinstance(target, VehicleEntity) else None
        self.__updateIgnoredVehicleIDs()
        BigWorld.player().autoAim(None)
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying and replayCtrl.isControllingCamera:
            self.__dataUpdateCallback = BigWorld.callback(0.0, self.__updateTrajectoryData)
        else:
            self.__updateTrajectoryData()
        return

    def disable(self):
        super(_TrajectoryControlMode, self).disable()
        self.__trajectoryDrawer.visible = False
        if self.__dataUpdateCallback is not None:
            BigWorld.cancelCallback(self.__dataUpdateCallback)
            self.__dataUpdateCallback = None
        self.__interpolator.disable()
        self._cam.writeUserPreferences()
        self.spgShotsIndicatorState = {}
        return

    def setObservedVehicle(self, vehicleID):
        self.__controllingVehicleID = vehicleID
        self.__updateIgnoredVehicleIDs()

    def handleKeyEvent(self, isDown, key, mods, event=None):
        cmdMap = CommandMapping.g_instance
        if cmdMap.isFired(CommandMapping.CMD_CM_SHOOT, key) and isDown:
            BigWorld.player().shoot()
            return True
        elif cmdMap.isFired(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION, key) and isDown:
            self._aih.switchAutorotation(True)
            return True
        elif cmdMap.isFired(CommandMapping.CMD_CM_ALTERNATE_MODE, key) and isDown:
            self.__interpolator.disable()
            pos = self._cam.aimingSystem.getDesiredShotPoint()
            if pos is None:
                pos = self._gunMarker.getPosition()
            self._aih.onControlModeChanged(CTRL_MODE_NAME.ARCADE, preferredPos=pos, aimingMode=self._aimingMode, closesDist=False)
            return True
        else:
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
                if self.__switchToNextControlMode(switchToPos=self._cam.getCurrentCamDist(), switchToPlace=SwitchToPlaces.TO_NEAR_POS):
                    return True
            return False

    def handleMouseEvent(self, dx, dy, dz):
        GUI.mcursor().position = self._aimOffset
        if not self._aih.isObserverFPV:
            self._cam.update(dx, dy, dz)
        return True

    def onMinimapClicked(self, worldPos):
        self._cam.teleport(worldPos)
        return True

    def resetGunMarkers(self):
        self._gunMarker.reset()

    def setGUIVisible(self, isVisible):
        self.__trajectoryDrawer.visible = isVisible

    def isManualBind(self):
        return True

    def getCamDistRatio(self):
        return self._cam.getDistRatio()

    def getCamDist(self):
        return self._cam.getCurrentCamDist()

    def getScaleParams(self):
        minV, maxV = self.getCamDistRange()
        return (minV, self._cam.getCamTransitionDist(), maxV)

    def getCamDistRange(self):
        return self._cam.getCamDistRange()

    def __onInterpolationStart(self):
        self._cam.isAimOffsetEnabled = False

    def __onInterpolationStop(self):
        self._cam.isAimOffsetEnabled = True

    def __switchToNextControlMode(self, switchToPos=None, switchToPlace=None):
        if GUI_SETTINGS.spgAlternativeAimingCameraEnabled and self._aih.isSPG and not self._aih.isAssaultSPG and self._nextControlMode is not None:
            soundName = self._SWITCH_SOUND.get(self._nextControlMode)
            if soundName:
                SoundGroups.g_instance.playSound2D(soundName)
            pos = self._cam.aimingSystem.planePosition
            if pos is None:
                pos = self._gunMarker.getPosition()
            source = self._cam.camera
            sourceFov = BigWorld.projection().fov
            self._aih.onControlModeChanged(self._nextControlMode, preferredPos=pos, aimingMode=self._aimingMode, saveDist=True, switchToPos=switchToPos, switchToPlace=switchToPlace)
            self.__interpolator.enable(source, self._aih.ctrl.camera.camera, sourceFov, BigWorld.projection().fov)
            AccountSettings.setSettings(LAST_ARTY_CTRL_MODE, self._nextControlMode)
            isStrategicMode = self._nextControlMode == CTRL_MODE_NAME.STRATEGIC
            self.__trajectoryDrawer.setStrategicMode(isStrategicMode)
            return True
        else:
            return False

    def __updateTrajectoryDrawer(self, targetPoint, shotPos, shotVel, target):
        try:
            if isinstance(target, VehicleEntity):
                targetVehicleID = target.id
            else:
                targetVehicleID = None
            if targetVehicleID != self.__targetVehicleID:
                nonCollideVehicles = []
                if self.__controllingVehicleID is not None:
                    nonCollideVehicles.append(self.__controllingVehicleID)
                if targetVehicleID is not None:
                    nonCollideVehicles.append(targetVehicleID)
                self.__trajectoryDrawer.setIgnoredIDs(nonCollideVehicles)
            self.__targetVehicleID = targetVehicleID
            self.__trajectoryDrawer.update(targetPoint, shotPos, shotVel, self.__updateInterval)
        except Exception:
            LOG_CURRENT_EXCEPTION()

        return

    def __onGunShotChanged(self):
        shotDescr = BigWorld.player().getVehicleDescriptor().shot
        self.__trajectoryDrawer.setParams(shotDescr.maxDistance, Math.Vector3(0, -shotDescr.gravity, 0), self._aimOffset)

    def __initTrajectoryDrawer(self):
        player = BigWorld.player()
        player.onGunShotChanged += self.__onGunShotChanged
        self.__trajectoryDrawer.setColors(Math.Vector4(0, 255, 0, 255), Math.Vector4(255, 0, 0, 255), Math.Vector4(128, 128, 128, 255))
        self.__controllingVehicleID = player.playerVehicleID
        attachedVehicle = player.getVehicleAttached()
        if attachedVehicle is not None:
            self.__controllingVehicleID = attachedVehicle.id
        self.__trajectoryDrawer.setIgnoredIDs([self.__controllingVehicleID])
        self.__onGunShotChanged()
        return

    def __delTrajectoryDrawer(self):
        BigWorld.player().onGunShotChanged -= self.__onGunShotChanged
        self.__trajectoryDrawer = None
        self.__controllingVehicleID = None
        self.__targetVehicleID = None
        return

    def __updateTrajectoryData(self):
        self.__dataUpdateCallback = BigWorld.callback(self.__updateInterval, self.__updateTrajectoryData)
        targetPoint = self.camera.aimingSystem.getDesiredShotPoint()
        if targetPoint is None:
            return
        else:
            player = BigWorld.player()
            target = BigWorld.target()
            if player is None or player.getVehicleAttached() is None:
                return
            vehicleDescriptor = player.getVehicleDescriptor()
            shotsIndicatorState = {}
            for i, shotDescr in enumerate(vehicleDescriptor.gun.shots):
                if i == vehicleDescriptor.activeGunShotIndex:
                    shotPos, shotVel, shotGravity = player.gunRotator.getShotParams(targetPoint, ignoreYawLimits=True)
                    self.__updateTrajectoryDrawer(targetPoint, shotPos, shotVel, target)
                    if self.__needSPGIndicatorUpdate(shotDescr):
                        shotsIndicatorState[i] = self._getShotIndicatorState(i, targetPoint, shotPos, shotVel, shotGravity, player, target, shotDescr)
                if self.__needSPGIndicatorUpdate(shotDescr):
                    shotPos, shotVel, shotGravity = player.gunRotator.getShotParams(targetPoint, ignoreYawLimits=True, overrideShotIdx=i)
                    shotsIndicatorState[i] = self._getShotIndicatorState(i, targetPoint, shotPos, shotVel, shotGravity, player, target, shotDescr)

            self.spgShotsIndicatorState = shotsIndicatorState
            return

    def _getShotIndicatorState(self, shotIdx, targetPoint, shotPos, shotVel, shotGravity, player, target, shotDescr):
        shotResult = getSPGShotResult(targetPoint, shotIdx, shotPos, shotVel, shotGravity, player, target)
        flyTime = getSPGShotFlyTime(targetPoint, shotVel, shotPos, shotDescr.maxDistance, shotDescr.speed)
        return (shotResult, flyTime)

    def __needSPGIndicatorUpdate(self, shotDescr):
        ammoCtrl = self.__sessionProvider.shared.ammo
        shellCD = shotDescr.shell.compactDescr
        if ammoCtrl is not None and ammoCtrl.shellInAmmo(shellCD):
            quantity, _ = ammoCtrl.getShells(shellCD)
            if quantity <= 0:
                return False
        else:
            return False
        return self.__settingsCore.getSetting(SPGAim.SHOTS_RESULT_INDICATOR)

    def __updateIgnoredVehicleIDs(self):
        ignoredIDs = [self.__controllingVehicleID] if self.__controllingVehicleID is not None else []
        if self.__targetVehicleID is not None:
            ignoredIDs.append(self.__targetVehicleID)
        self.__trajectoryDrawer.setIgnoredIDs(ignoredIDs)
        return

    def onChangeControlModeByScroll(self, switchToName, switchToPos, switchToPlace):
        if self._nextControlMode is not None and self._nextControlMode == switchToName:
            BigWorld.callback(0.0, partial(self.__switchToNextControlMode, switchToPos=switchToPos, switchToPlace=switchToPlace))
        return


class StrategicControlMode(_TrajectoryControlMode):
    _TRAJECTORY_UPDATE_INTERVAL = 0.1

    def __init__(self, dataSection, avatarInputHandler):
        super(StrategicControlMode, self).__init__(dataSection, avatarInputHandler, CTRL_MODE_NAME.STRATEGIC, StrategicControlMode._TRAJECTORY_UPDATE_INTERVAL)
        self._nextControlMode = CTRL_MODE_NAME.ARTY
        self._cam = StrategicCamera.StrategicCamera(dataSection['camera'])

    def enable(self, **args):
        super(StrategicControlMode, self).enable(**args)
        AccountSettings.setSettings(LAST_ARTY_CTRL_MODE, CTRL_MODE_NAME.STRATEGIC)
        g_repeatKeyHandlers.add(self.__handleRepeatKeyEvent)

    def disable(self):
        super(StrategicControlMode, self).disable()
        g_repeatKeyHandlers.discard(self.__handleRepeatKeyEvent)

    def __handleRepeatKeyEvent(self, event):
        return self.handleKeyEvent(event.isKeyDown(), event.key, 0)


class ArtyControlMode(_TrajectoryControlMode):
    _TRAJECTORY_UPDATE_INTERVAL = 0.05

    def __init__(self, dataSection, avatarInputHandler):
        super(ArtyControlMode, self).__init__(dataSection, avatarInputHandler, CTRL_MODE_NAME.ARTY, ArtyControlMode._TRAJECTORY_UPDATE_INTERVAL)
        self._nextControlMode = CTRL_MODE_NAME.STRATEGIC
        self._cam = ArtyCamera.ArtyCamera(dataSection['camera'])

    def enable(self, **args):
        super(ArtyControlMode, self).enable(**args)
        self.strategicCamera = STRATEGIC_CAMERA.TRAJECTORY
        AccountSettings.setSettings(LAST_ARTY_CTRL_MODE, CTRL_MODE_NAME.ARTY)

    def disable(self):
        super(ArtyControlMode, self).disable()
        self.strategicCamera = STRATEGIC_CAMERA.AERIAL


class OnlyArtyControlMode(_TrajectoryControlMode):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _TRAJECTORY_UPDATE_INTERVAL = 0.05

    def __init__(self, dataSection, avatarInputHandler):
        super(OnlyArtyControlMode, self).__init__(dataSection, avatarInputHandler, CTRL_MODE_NAME.SPG_ONLY_ARTY_MODE, OnlyArtyControlMode._TRAJECTORY_UPDATE_INTERVAL)
        self._nextControlMode = None
        self._cam = OnlyArtyCamera.OnlyArtyCamera(dataSection['camera'])
        return

    def enable(self, **args):
        super(OnlyArtyControlMode, self).enable(**args)
        self.strategicCamera = STRATEGIC_CAMERA.TRAJECTORY
        if self._aih.isFlamethrower:
            self._cam.setMaxDistance(BigWorld.player().getVehicleDescriptor().shot.maxDistance)
        ammoCtrl = self.__sessionProvider.shared.ammo
        if ammoCtrl is not None:
            ammoCtrl.onCurrentShellChanged += self.__onCurrentShellChanged
        return

    def disable(self):
        super(OnlyArtyControlMode, self).disable()
        self.strategicCamera = STRATEGIC_CAMERA.AERIAL
        ammoCtrl = self.__sessionProvider.shared.ammo
        if ammoCtrl is not None:
            ammoCtrl.onCurrentShellChanged -= self.__onCurrentShellChanged
        return

    def __onCurrentShellChanged(self, intCD):
        ctrl = self.__sessionProvider.shared.ammo
        if ctrl is not None:
            shotIdx = ctrl.getGunSettings().getShotIndex(intCD)
            if shotIdx < 0:
                LOG_WARNING('FlamethrowerControlMode __onCurrentShellChanged invalid shellID', intCD)
                return
            shotDesc = BigWorld.player().getVehicleDescriptor().gun.shots[shotIdx]
            self._cam.setMaxDistance(shotDesc.maxDistance)
        return


class AssaultControlMode(_TrajectoryControlMode):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _TRAJECTORY_UPDATE_INTERVAL = 0.05
    _MIN_ACCEPT_TARGET_NORMAL = -0.1

    def __init__(self, dataSection, avatarInputHandler):
        super(AssaultControlMode, self).__init__(dataSection, avatarInputHandler, CTRL_MODE_NAME.ASSAULT_SPG, AssaultControlMode._TRAJECTORY_UPDATE_INTERVAL)
        self._nextControlMode = CTRL_MODE_NAME.ARCADE
        self._cam = AssaultCamera.AssaultCamera(dataSection['camera'])

    def enable(self, **args):
        replayCtrl = BattleReplay.g_replayCtrl
        if not (replayCtrl.isPlaying and replayCtrl.isControllingCamera):
            canEnable = False
            if args['hitNormal'].y > AssaultControlMode._MIN_ACCEPT_TARGET_NORMAL:
                canEnable = self._cam.setup(args['preferredPos'])
            else:
                LOG_DEBUG('AssaultCamera: aiming on the plane from below!')
            if not canEnable:
                self._aih.onControlModeChanged(CTRL_MODE_NAME.ARCADE)
                return
        super(AssaultControlMode, self).enable(**args)
        self.strategicCamera = STRATEGIC_CAMERA.TRAJECTORY
        ammoCtrl = self.__sessionProvider.shared.ammo
        if ammoCtrl is not None:
            ammoCtrl.onCurrentShellChanged += self.__onCurrentShellChanged
        return

    def disable(self):
        super(AssaultControlMode, self).disable()
        self.strategicCamera = STRATEGIC_CAMERA.AERIAL
        ammoCtrl = self.__sessionProvider.shared.ammo
        if ammoCtrl is not None:
            ammoCtrl.onCurrentShellChanged -= self.__onCurrentShellChanged
        return

    def __onCurrentShellChanged(self, intCD):
        ctrl = self.__sessionProvider.shared.ammo
        if ctrl is not None:
            shotIdx = ctrl.getGunSettings().getShotIndex(intCD)
            if shotIdx < 0:
                LOG_WARNING('AssaultControlMode __onCurrentShellChanged invalid shellID', intCD)
                return
        return


class SniperControlMode(_GunControlMode):
    _LENS_EFFECTS_ENABLED = True
    _BINOCULARS_MODE_SUFFIX = ['usual', 'coated']
    BinocularsModeDesc = namedtuple('BinocularsModeDesc', ('background', 'distortion', 'rgbCube', 'greenOffset', 'blueOffset', 'aberrationRadius', 'distortionAmount'))
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    @staticmethod
    def enableLensEffects(enable):
        SniperControlMode._LENS_EFFECTS_ENABLED = enable
        curCtrl = getattr(getattr(BigWorld.player(), 'inputHandler', None), 'ctrl', None)
        if isinstance(curCtrl, SniperControlMode) and curCtrl._binoculars is not None:
            curCtrl._binoculars.setEnableLensEffects(SniperControlMode._LENS_EFFECTS_ENABLED)
        return

    def __init__(self, dataSection, avatarInputHandler, mode=CTRL_MODE_NAME.SNIPER):
        super(SniperControlMode, self).__init__(dataSection, avatarInputHandler, mode)
        self._binoculars = BigWorld.wg_binoculars()
        self._setupCamera(dataSection)
        self.__binocularsModes = {}
        for suffix in SniperControlMode._BINOCULARS_MODE_SUFFIX:
            prefPath = 'binoculars_' + suffix
            modeDesc = SniperControlMode.BinocularsModeDesc(dataSection.readString(prefPath + '/background'), dataSection.readString(prefPath + '/distortion'), dataSection.readString(prefPath + '/rgbCube'), dataSection.readFloat(prefPath + '/greenOffset'), dataSection.readFloat(prefPath + '/blueOffset'), dataSection.readFloat(prefPath + '/aberrationRadius'), dataSection.readFloat(prefPath + '/distortionAmount'))
            self.__binocularsModes[suffix] = modeDesc

    def create(self):
        self._cam.create(self.onChangeControlModeByScroll)
        super(SniperControlMode, self).create()
        optDevicesCtrl = self.__guiSessionProvider.shared.optionalDevices
        if optDevicesCtrl is not None:
            optDevicesCtrl.onDescriptorDevicesChanged += self.__onDescriptorDevicesChanged
        self.__setupBinoculars(vehicle_getter.getOptionalDevices())
        return

    def destroy(self):
        optDevicesCtrl = self.__guiSessionProvider.shared.optionalDevices
        if optDevicesCtrl is not None:
            optDevicesCtrl.onDescriptorDevicesChanged -= self.__onDescriptorDevicesChanged
        self.disable(True)
        self._binoculars.setEnabled(False)
        self._binoculars.resetTextures()
        self._cam.writeUserPreferences()
        super(SniperControlMode, self).destroy()
        return

    def enable(self, **args):
        super(SniperControlMode, self).enable(**args)
        SoundGroups.g_instance.changePlayMode(1)
        desc = BigWorld.player().getVehicleDescriptor()
        isHorizontalStabilizerAllowed = desc.gun.turretYawLimits is None
        self._cam.aimingSystem.enableHorizontalStabilizerRuntime(isHorizontalStabilizerAllowed)
        self._cam.aimingSystem.forceFullStabilization(self.__isFullStabilizationRequired())
        self._cam.aimingSystem.enableAutoRotation(self._aih.getAutorotation())
        self._cam.enable(args['preferredPos'], args['saveZoom'])
        self._binoculars.setEnabled(True)
        self._binoculars.setEnableLensEffects(SniperControlMode._LENS_EFFECTS_ENABLED)
        BigWorld.wg_enableTreeHiding(True)
        BigWorld.wg_setTreeHidingRadius(15.0, 10.0)
        BigWorld.wg_havokSetSniperMode(True)
        if not BattleReplay.g_replayCtrl.isPlaying:
            TriggersManager.g_manager.activateTrigger(TRIGGER_TYPE.SNIPER_MODE)
        if BattleReplay.g_replayCtrl.isRecording:
            BattleReplay.g_replayCtrl.onSniperModeChanged(True)
        if self._aih.siegeModeControl is not None:
            self._aih.siegeModeControl.onSiegeStateChanged += self.__siegeModeStateChanged
        return

    def disable(self, isDestroy=False):
        super(SniperControlMode, self).disable()
        self._binoculars.setEnabled(False)
        BigWorld.wg_havokSetSniperMode(False)
        BigWorld.wg_enableTreeHiding(False)
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
            vehicleData = self.__guiSessionProvider.arenaVisitor.getArenaVehicles().get(vehicleID)
            if vehicleData is not None:
                vehicleDescr = vehicleData.get('vehicleType', vehicleDescr)
            self.__setupBinoculars(vehicleDescr.optionalDevices)
            isHorizontalStabilizerAllowed = vehicleDescr.gun.turretYawLimits is None
            if self._cam.aimingSystem is not None:
                self._cam.aimingSystem.enableHorizontalStabilizerRuntime(isHorizontalStabilizerAllowed)
            return

    def handleKeyEvent(self, isDown, key, mods, event=None):
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
            self._aih.switchAutorotation(True)
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
            return turretHasYawLimits and not self._aih.isHullLockEnabled() or yawHullAimingAvailable or isRotationAroundCenter and not turretHasYawLimits

    def enableSwitchAutorotationMode(self, triggeredByKey=False):
        vehicle = BigWorld.entities.get(BigWorld.player().playerVehicleID)
        if vehicle is None:
            return
        else:
            desc = vehicle.typeDescriptor
            isRotationAroundCenter = desc.chassis.rotationIsAroundCenter
            turretHasYawLimits = desc.gun.turretYawLimits is not None
            yawHullAimingAvailable = desc.isYawHullAimingAvailable
            return turretHasYawLimits and triggeredByKey or yawHullAimingAvailable or isRotationAroundCenter and not turretHasYawLimits

    def onAutorotationChanged(self, value):
        vehicle = BigWorld.entities.get(BigWorld.player().playerVehicleID)
        if vehicle is None or vehicle.typeDescriptor.gun.turretYawLimits is None:
            return
        else:
            self._cam.aimingSystem.enableAutoRotation(self._aih.getAutorotation())
            return

    def onChangeControlModeByScroll(self, switchToClosestDist=True):
        if not _isEnabledChangeModeByScroll(self._cam, self._aih):
            return
        self._aih.onControlModeChanged(CTRL_MODE_NAME.ARCADE, preferredPos=self.camera.aimingSystem.getDesiredShotPoint(), turretYaw=self._cam.aimingSystem.turretYaw, gunPitch=self._cam.aimingSystem.gunPitch, aimingMode=self._aimingMode, closesDist=switchToClosestDist)

    def recreateCamera(self):
        preferredPos = self.camera.aimingSystem.getDesiredShotPoint()
        self._cam.disable()
        self._cam.enable(preferredPos, True)

    def setForcedGuiControlMode(self, enable):
        if enable:
            self._cam.update(0, 0, 0, False)

    def _setupCamera(self, dataSection):
        self._cam = SniperCamera.SniperCamera(dataSection['camera'], defaultOffset=self._defaultOffset, binoculars=self._binoculars)

    def __setupBinoculars(self, optDevices):
        isCoatedOptics = findFirst(lambda d: d is not None and 'coatedOptics' in d.tags, optDevices) is not None
        modeDesc = self.__binocularsModes[SniperControlMode._BINOCULARS_MODE_SUFFIX[1 if isCoatedOptics else 0]]
        self._binoculars.setBackgroundTexture(modeDesc.background)
        self._binoculars.setDistortionTexture(modeDesc.distortion)
        self._binoculars.setColorGradingTexture(modeDesc.rgbCube)
        self._binoculars.setParams(modeDesc.greenOffset, modeDesc.blueOffset, modeDesc.aberrationRadius, modeDesc.distortionAmount)
        return

    def __siegeModeStateChanged(self, newState, timeToNewMode):
        if newState == VEHICLE_SIEGE_STATE.ENABLED or newState == VEHICLE_SIEGE_STATE.DISABLED:
            self._cam.aimingSystem.forceFullStabilization(self.__isFullStabilizationRequired())
            self._cam.aimingSystem.onSiegeStateChanged(newState)

    def __isFullStabilizationRequired(self):
        descriptor = BigWorld.player().vehicleTypeDescriptor
        return descriptor.isPitchHullAimingAvailable or descriptor.isYawHullAimingAvailable

    def __onDescriptorDevicesChanged(self, optDevices):
        self.__setupBinoculars(optDevices)


class DualGunControlMode(SniperControlMode):
    __chargeMarkerState = aih_global_binding.bindRW(aih_global_binding.BINDING_ID.CHARGE_MARKER_STATE)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, dataSection, avatarInputHandler):
        super(DualGunControlMode, self).__init__(dataSection, avatarInputHandler, CTRL_MODE_NAME.DUAL_GUN)

    def enable(self, **args):
        super(DualGunControlMode, self).enable(**args)
        ctrl = self.__sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
        return

    def disable(self, isDestroy=False):
        ctrl = self.__sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
        super(DualGunControlMode, self).disable(isDestroy)
        return

    def handleKeyEvent(self, isDown, key, mods, event=None):
        if self._aih.dualGunControl and self._aih.dualGunControl.handleKeyEvent(isDown, key, mods, event):
            return True
        super(DualGunControlMode, self).handleKeyEvent(isDown, key, mods, event)

    def updateTargetedEnemiesForGuns(self, gunsData):
        leftCollision, rightCollision = gunsData[:2]
        hasLeft = leftCollision is not None
        hasRight = rightCollision is not None
        chargeState = CHARGE_MARKER_STATE.DIMMED
        if hasLeft and hasRight:
            chargeState = CHARGE_MARKER_STATE.VISIBLE
        elif hasLeft:
            chargeState = CHARGE_MARKER_STATE.LEFT_ACTIVE
        elif hasRight:
            chargeState = CHARGE_MARKER_STATE.RIGHT_ACTIVE
        self.__chargeMarkerState = chargeState
        return

    def alwaysReceiveKeyEvents(self, isDown=True):
        return True if not isDown else False

    def setForcedGuiControlMode(self, enable):
        if enable and self._aih.dualGunControl:
            self._aih.dualGunControl.cancelShootKeyEvent()

    def __onActiveGunChanged(self, gunIndex, switchTime):
        self._cam.aimingSystem.onActiveGunChanged(gunIndex, switchTime)

    def _setupCamera(self, dataSection):
        self._cam = DualGunCamera.DualGunCamera(dataSection['camera'], defaultOffset=self._defaultOffset, binoculars=self._binoculars)

    def __onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        if eventID == FEEDBACK_EVENT_ID.VEHICLE_ACTIVE_GUN_CHANGED:
            activeGun, switchDelay = value
            self._cam.aimingSystem.onActiveGunChanged(activeGun, switchDelay)


class PostMortemControlMode(IControlMode):
    _POSTMORTEM_DELAY_ENABLED = True
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    __aimOffset = aih_global_binding.bindRO(aih_global_binding.BINDING_ID.AIM_OFFSET)

    @property
    def aimingMode(self):
        pass

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
        self.__isEnabled = False
        self.__postmortemDelay = None
        self.__isObserverMode = False
        self.__videoControlModeAvailable = dataSection.readBool('videoModeAvailable', constants.HAS_DEV_RESOURCES)
        self._cameraTransitionDurations = _readCameraTransitionSettings(dataSection['camera'])
        self._targetCtrlModeAfterDelay = None
        self.__altTargetMode = None
        return

    def prerequisites(self):
        return []

    def create(self):
        self.__cam.create(None, True)
        return

    def destroy(self):
        self.disable()
        self.__cam.destroy()
        self.__cam = None
        return

    def enable(self, **args):
        SoundGroups.g_instance.changePlayMode(0)
        playerPostmortemViewPointDefined = False
        player = BigWorld.player()
        if player:
            self.__selfVehicleID = player.playerVehicleID
            self.__isObserverMode = 'observer' in player.vehicleTypeDescriptor.type.tags
            self.__curVehicleID = self.__selfVehicleID
            playerVehicle = BigWorld.entities.get(player.playerVehicleID)
            if playerVehicle:
                playerPostmortemViewPointDefined = playerVehicle.isPostmortemViewPointDefined
        camTransitionParams = {'cameraTransitionDuration': args.get('transitionDuration', -1),
         'camMatrix': args.get('camMatrix', None)}
        self.__cam.enable(None, False, args.get('postmortemParams'), None, None, camTransitionParams)
        newVehicle = args.get('newVehicleID', None)
        self.__cam.vehicleMProv = player.consistentMatrices.attachedVehicleMatrix if newVehicle is None else BigWorld.entities.get(newVehicle).matrix
        self.__connectToArena()
        _setCameraFluency(self.__cam.camera, self.__CAM_FLUENCY)
        self.__isEnabled = True
        player.consistentMatrices.onVehicleMatrixBindingChanged += self._onMatrixBound
        if not BattleReplay.g_replayCtrl.isPlaying:
            if self.__isObserverMode:
                vehicleID = args.get('vehicleID')
                if vehicleID is None:
                    self.__switch()
                else:
                    self.__fakeSwitchToVehicle(vehicleID)
                return
            if (self._isPostmortemDelayEnabled() or bool(args.get('respawn', False))) and bool(args.get('bPostmortemDelay')) and not playerPostmortemViewPointDefined:
                self.__startPostmortemDelay(self.__selfVehicleID)
            else:
                self.__switchToVehicle(None)
        arena = BigWorld.player().arena
        if arena is not None:
            arena.onVehicleKilled += self.__onArenaVehicleKilled
        if bool(args.get('respawn', False)):
            respawnCtrl = self.guiSessionProvider.dynamic.respawn
            if respawnCtrl:
                self._targetCtrlModeAfterDelay = CTRL_MODE_NAME.RESPAWN_DEATH
                if respawnCtrl.respawnInfo is None:
                    self._targetCtrlModeAfterDelay = None
                respawnCtrl.onRespawnInfoUpdated += self.__onRespawnInfoUpdated
                if respawnCtrl.respawnInfo is not None:
                    self.__onRespawnInfoUpdated(respawnCtrl.respawnInfo)
        if playerPostmortemViewPointDefined:
            matrix = Math.Matrix(player.consistentMatrices.attachedVehicleMatrix)
            self.__cam.setYawPitch(matrix.yaw, -matrix.pitch)
        return

    def __startPostmortemDelay(self, vehicleID):
        initialDelay = self.__calculatePostMortemInitialDelayForVehicle(vehicleID)
        self.__postmortemDelay = PostmortemDelay(self.__cam, self._onPostmortemDelayStart, self._onPostmortemDelayStop, initialDelay, self._isPostmortemDelayEnabled())
        self.__postmortemDelay.start()

    def __calculatePostMortemInitialDelayForVehicle(self, vehicleID):
        vehicle = BigWorld.entities.get(vehicleID)
        if vehicle is None or not vehicle.isWheeledTech:
            return 0
        else:
            wheeledDeathCountLeft = AccountSettings.getSettings(WHEELED_DEATH_DELAY_COUNT)
            if wheeledDeathCountLeft == 0:
                return 0
            AccountSettings.setSettings(WHEELED_DEATH_DELAY_COUNT, max(wheeledDeathCountLeft - 1, 0))
            return _WHEELED_VEHICLE_POSTMORTEM_DELAY

    def disable(self):
        ctrl = self.guiSessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onRespawnInfoUpdated -= self.__onRespawnInfoUpdated
        self._targetCtrlModeAfterDelay = None
        self.__altTargetMode = None
        arena = BigWorld.player().arena
        if arena is not None:
            arena.onVehicleKilled -= self.__onArenaVehicleKilled
        BigWorld.player().consistentMatrices.onVehicleMatrixBindingChanged -= self._onMatrixBound
        self.__isEnabled = False
        self._destroyPostmortemDelay()
        self.__disconnectFromArena()
        self.__cam.disable()
        self.__curVehicleID = None
        return

    def handleKeyEvent(self, isDown, key, mods, event=None):
        cmdMap = CommandMapping.g_instance
        guiCtrlEnabled = BigWorld.player().isForcedGuiControlMode()
        if BigWorld.isKeyDown(Keys.KEY_CAPSLOCK) and constants.HAS_DEV_RESOURCES and isDown and key == Keys.KEY_F1:
            self.__aih.onControlModeChanged(CTRL_MODE_NAME.DEBUG, prevModeName=CTRL_MODE_NAME.POSTMORTEM, camMatrix=self.__cam.camera.matrix)
            return True
        if BigWorld.isKeyDown(Keys.KEY_CAPSLOCK) and isDown and key == Keys.KEY_F3 and (self.__videoControlModeAvailable or self.guiSessionProvider.getCtx().isPlayerObserver()):
            if not self.__aih.isControlModeChangeAllowed():
                return
            self.__aih.onControlModeChanged(CTRL_MODE_NAME.VIDEO, prevModeName=CTRL_MODE_NAME.POSTMORTEM, camMatrix=self.__cam.camera.matrix, curVehicleID=self.__curVehicleID)
            return True
        if cmdMap.isFired(CommandMapping.CMD_CM_POSTMORTEM_NEXT_VEHICLE, key) and isDown and not guiCtrlEnabled:
            if self.__aih.isAllowToSwitchPositionOrFPV():
                self.__switch()
                return True
        if cmdMap.isFired(CommandMapping.CMD_CM_POSTMORTEM_SELF_VEHICLE, key) and isDown and not guiCtrlEnabled:
            if self.__aih.isAllowToSwitchPositionOrFPV():
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
        GUI.mcursor().position = self.__aimOffset
        if self.__postmortemDelay is not None:
            self.__postmortemDelay.handleMouseEvent(dx, dy, dz)
            return True
        else:
            self.__cam.update(dx, dy, math_utils.clamp(-1, 1, dz))
            return True

    def onRecreateDevice(self):
        pass

    def selectPlayer(self, vehID):
        self.__switchToVehicle(vehID)

    def selectViewPoint(self, pointID):
        self.__switchToViewpoint(pointID)

    def setGUIVisible(self, isVisible):
        pass

    def _switchToCtrlMode(self, targetMode):
        if self.curPostmortemDelay is not None or targetMode is None:
            return
        else:
            self.selectPlayer(None)
            BigWorld.player().inputHandler.onControlModeChanged(targetMode, prevModeName=CTRL_MODE_NAME.POSTMORTEM, camMatrix=Math.Matrix(BigWorld.camera().matrix), curVehicleID=self.__curVehicleID, transitionDuration=self._cameraTransitionDurations[targetMode])
            return

    def _isPostmortemDelayEnabled(self):
        return PostMortemControlMode.getIsPostmortemDelayEnabled()

    def _destroyPostmortemDelay(self):
        if self.__postmortemDelay is not None:
            self.__postmortemDelay.destroy()
            self.__postmortemDelay = None
        return

    def _onPostmortemDelayStart(self, killerVehicleID):
        self.__aih.onPostmortemKillerVisionEnter(killerVehicleID)

    def _onPostmortemDelayStop(self):
        self.__cam.vehicleMProv = BigWorld.player().consistentMatrices.attachedVehicleMatrix
        self.__aih.onPostmortemKillerVisionExit()
        if not self.__isEnabled:
            return
        else:
            self._destroyPostmortemDelay()
            if self._targetCtrlModeAfterDelay is None:
                self._switchToCtrlMode(self.altTargetMode)
            else:
                self._switchToCtrlMode(self._targetCtrlModeAfterDelay)
            return

    def __onArenaVehicleKilled(self, targetID, attackerID, equipmentID, reason, numVehiclesAffected):
        if self.curPostmortemDelay is not None or self.__altTargetMode is None:
            return
        else:
            if targetID == self.__curVehicleID:
                LOG_DEBUG('target vehicle killed, switch to alternative mode')
                self._switchToCtrlMode(self.__altTargetMode)
            return

    def __onRespawnInfoUpdated(self, respawnInfo):
        if respawnInfo is not None:
            self._targetCtrlModeAfterDelay = CTRL_MODE_NAME.RESPAWN_DEATH
        if self.curPostmortemDelay is None:
            self._switchToCtrlMode(self._targetCtrlModeAfterDelay)
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
            self.__doPreBind()
            self.guiSessionProvider.shared.viewPoints.selectViewPoint(toId)
            return

    def __switch(self, isNext=True):
        if self.__postmortemDelay is not None:
            return
        else:
            self.__doPreBind()
            self.guiSessionProvider.shared.viewPoints.switch(isNext)
            return

    def __switchToVehicle(self, toId=None):
        if self.__postmortemDelay is not None:
            return
        else:
            self.__doPreBind()
            self.__changeVehicle(toId)
            self.guiSessionProvider.shared.viewPoints.selectVehicle(toId)
            return

    def __doPreBind(self):
        if self.__curVehicleID is not None:
            vehicle = BigWorld.entity(self.__curVehicleID)
            if vehicle is not None:
                vehicle.removeCameraCollider()
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
            if vehicle.isUpgrading:
                return
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

    def _onMatrixBound(self, isStatic):
        if isStatic:
            return
        else:
            vehicle = BigWorld.player().vehicle
            if vehicle is None or self.__curVehicleID != vehicle.id or not vehicle.inWorld:
                return
            vehicle.addCameraCollider()
            replayCtrl = BattleReplay.g_replayCtrl
            if replayCtrl.isRecording:
                replayCtrl.setPlayerVehicleID(self.__curVehicleID)
            if self.__cam.vehicleMProv is not BigWorld.player().consistentMatrices.attachedVehicleMatrix:
                self.__cam.vehicleMProv = BigWorld.player().consistentMatrices.attachedVehicleMatrix
            self.__aih.onCameraChanged(CTRL_MODE_NAME.POSTMORTEM, self.__curVehicleID)
            return

    def isSelfVehicle(self):
        return self.__curVehicleID == self.__selfVehicleID

    @property
    def curVehicleID(self):
        return self.__curVehicleID

    @property
    def curPostmortemDelay(self):
        return self.__postmortemDelay

    @property
    def camera(self):
        return self.__cam

    @property
    def isEnabled(self):
        return self.__isEnabled

    @property
    def altTargetMode(self):
        return self.__altTargetMode

    @altTargetMode.setter
    def altTargetMode(self, mode):
        self.__altTargetMode = mode


class _ShellingControl(object):
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
        except Exception:
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
            result.materialFX = GUI.Simple.eMaterialFX.BLEND_INVERSE_COLOUR
            result.filterType = GUI.Simple.eFilterType.LINEAR
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
            BigWorld.player().addModel(result)
        elif self.__targetModel is not None:
            self.setTargetModelAutoUpdate(None)
            BigWorld.player().delModel(self.__targetModel)
            self.__targetModel = None
        return result

    def __showTargetPointer_directly(self, value):
        self.__targetPointer.visible = value

    def __showTargetModel_directly(self, value):
        self.__targetModel.visible = value


class _MouseVehicleRotator(object):
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
            self.__rotationState = math_utils.clamp(-1, 1, dx)
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
    direction, start = cameras.getWorldRayAndPoint(0, 0)
    end = start + direction.scale(100000.0)
    point = collideDynamicAndStatic(start, end, (BigWorld.player().playerVehicleID,), 0)
    return point[0] if point is not None else AimingSystems.shootInSkyPoint(start, direction)


def _readCameraTransitionSettings(cameraDataSec):
    targetModeToDurationMap = dict.fromkeys(CTRL_MODES, -1.0)
    if cameraDataSec is None:
        return targetModeToDurationMap
    else:
        transitionSettings = cameraDataSec['transitionSettings']
        if transitionSettings is None:
            return targetModeToDurationMap
        for _, (_, durationSection) in _xml.getItemsWithContext(None, transitionSettings, 'transitionDuration'):
            targetMode = durationSection.readString('controlModeName')
            targetModeToDurationMap[targetMode] = durationSection.readFloat('duration', -1.0)

        return targetModeToDurationMap


def _sign(val):
    if val > 0:
        return 1.0
    return -1.0 if val < 0 else 0.0


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


def _isEnabledChangeModeByScroll(camera, aih):
    sniperModeByShift = camera.getUserConfigValue(GAME.SNIPER_MODE_BY_SHIFT)
    return not sniperModeByShift and not aih.isOnlyArty or aih.isObserverFPV
