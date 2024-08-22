# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/control_modes.py
import logging
import time
import weakref
from collections import namedtuple
from functools import partial
from enum import Enum
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
import math_utils
import constants
from AvatarInputHandler.DynamicCameras.free_camera import FreeVideoCamera
from constants import POSTMORTEM_MODIFIERS
from AimingSystems import getShotTargetInfo
from AimingSystems.magnetic_aim import magneticAimProcessor, MagneticAimSettings
from AvatarInputHandler import AimingSystems, aih_global_binding, gun_marker_ctrl
from AvatarInputHandler.DynamicCameras.camera_switcher import SwitchToPlaces
from AvatarInputHandler.StrategicCamerasInterpolator import StrategicCamerasInterpolator
from AvatarInputHandler.spg_marker_helpers.spg_marker_helpers import getSPGShotResult, getSPGShotFlyTime
from DynamicCameras import SniperCamera, StrategicCamera, ArcadeCamera, ArtyCamera, DualGunCamera
from PostmortemDelay import PostmortemDelay
from ProjectileMover import collideDynamicAndStatic
from TriggersManager import TRIGGER_TYPE
from Vehicle import Vehicle as VehicleEntity
from account_helpers.AccountSettings import AccountSettings, LAST_ARTY_CTRL_MODE, FREE_CAM_USES_COUNT
from account_helpers.settings_core.settings_constants import SPGAim, SPGAimEntranceModeOptions
from aih_constants import CTRL_MODE_NAME, GUN_MARKER_FLAG, STRATEGIC_CAMERA, CTRL_MODES, CHARGE_MARKER_STATE
from constants import AIMING_MODE
from constants import VEHICLE_SIEGE_STATE
from debug_utils import LOG_DEBUG, LOG_CURRENT_EXCEPTION
from gui import GUI_SETTINGS, g_repeatKeyHandlers
from gui.battle_control import avatar_getter, vehicle_getter
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID, ENTITY_IN_FOCUS_TYPE
from gui.battle_control.controllers.spectator_ctrl import SPECTATOR_MODE
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from helpers import dependency, uniprof
from helpers.CallbackDelayer import CallbackDelayer
from items import _xml
from shared_utils import findFirst
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

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
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
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
        if not self._isEnabled:
            return
        else:
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

    def _handleShootCmd(self):
        player = BigWorld.player()
        if player is None:
            return
        else:
            vehicle = player.getVehicleAttached()
            if vehicle is None or vehicle.typeDescriptor is None:
                return
            autoShootCtrl = self.__sessionProvider.shared.autoShootCtrl
            if autoShootCtrl is not None and vehicle.typeDescriptor.isAutoShootGunVehicle:
                self.__sessionProvider.shared.autoShootCtrl.processShootCmd()
                return
            player.shoot()
            return


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
    camera = property(lambda self: self.__cam)

    def __init__(self, dataSection, avatarInputHandler):
        self.__aih = weakref.proxy(avatarInputHandler)
        self.__cam = cameras.FreeCamera()
        self.__isCreated = False
        self.__isEnabled = False
        self.__sens = (3.0, 3.0, 3.0)

    def create(self):
        self.__isCreated = True

    def destroy(self):
        self.disable()
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
        self.__isEnabled = True

    def setForcedGuiControlMode(self, enable):
        if enable:
            self.__cam.resetMovement()

    def isSelfVehicle(self):
        return False

    def disable(self):
        if self.__cam is not None:
            self.__cam.disable()
        self.__isEnabled = False
        return

    def handleKeyEvent(self, isDown, key, mods, event=None):
        if BigWorld.isKeyDown(Keys.KEY_CAPSLOCK) and constants.HAS_DEV_RESOURCES and isDown and key == Keys.KEY_F2:
            self.__aih.onControlModeChanged('arcade')
        return self.__cam.handleKey(event)

    def handleMouseEvent(self, dx, dy, dz):
        GUI.mcursor().position = (0, 0)
        return self.__cam.handleMouse(int(self.__sens[0] * dx), int(self.__sens[1] * dy), int(self.__sens[2] * dz))

    def getEnabled(self):
        return bool(self.__isEnabled)

    def setCameraPosition(self, x, y, z):
        mat = Math.Matrix()
        mat.lookAt(Math.Vector3(x, y, z), (0, 0, 1), (0, 1, 0))
        self.__cam.camera.set(mat)

    def getCameraPosition(self):
        return tuple(self.__cam.camera.position)

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
        elif BigWorld.isKeyDown(Keys.KEY_CAPSLOCK) and constants.HAS_DEV_RESOURCES and isDown and key == Keys.KEY_F2:
            self._aih.onControlModeChanged(CTRL_MODE_NAME.DEBUG, camMatrix=self._cam.camera.matrix)
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
                self._handleShootCmd()
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

    def __activateAlternateMode(self, pos=None, bByScroll=False):
        ownVehicle = BigWorld.entity(BigWorld.player().playerVehicleID)
        if ownVehicle is not None and ownVehicle.isStarted and avatar_getter.isVehicleBarrelUnderWater() or BigWorld.player().isGunLocked or BigWorld.player().isObserver():
            return
        elif self._aih.isSPG and not bByScroll:
            self._cam.update(0, 0, 0, False, False)
            equipmentID = None
            if BattleReplay.isPlaying():
                mode = BattleReplay.g_replayCtrl.getControlMode()
                pos = BattleReplay.g_replayCtrl.getGunMarkerPos()
                equipmentID = BattleReplay.g_replayCtrl.getEquipmentId()
            else:
                mode = self.__getSpgAlternativeMode()
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
                mode = CTRL_MODE_NAME.SNIPER if not self._aih.isDualGun else CTRL_MODE_NAME.DUAL_GUN
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
            self._handleShootCmd()
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
            if TriggersManager.g_manager:
                TriggersManager.g_manager.fireTriggerInstantly(TRIGGER_TYPE.PLAYER_LEAVE_SPG_MODE)
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
        if GUI_SETTINGS.spgAlternativeAimingCameraEnabled:
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
                        shotsIndicatorState[i] = self.__getShotIndicatorState(i, targetPoint, shotPos, shotVel, shotGravity, player, target, shotDescr)
                if self.__needSPGIndicatorUpdate(shotDescr):
                    shotPos, shotVel, shotGravity = player.gunRotator.getShotParams(targetPoint, ignoreYawLimits=True, overrideShotIdx=i)
                    shotsIndicatorState[i] = self.__getShotIndicatorState(i, targetPoint, shotPos, shotVel, shotGravity, player, target, shotDescr)

            self.spgShotsIndicatorState = shotsIndicatorState
            return

    def __getShotIndicatorState(self, shotIdx, targetPoint, shotPos, shotVel, shotGravity, player, target, shotDescr):
        shotResult = getSPGShotResult(targetPoint, shotIdx, shotPos, shotVel, shotGravity, player, target)
        vehAttrs = self.__sessionProvider.shared.feedback.getVehicleAttrs()
        flyTime = getSPGShotFlyTime(targetPoint, shotVel, shotPos, shotDescr.maxDistance, shotDescr.speed, vehAttrs)
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
        if self._nextControlMode == switchToName:
            BigWorld.callback(0.0, partial(self.__switchToNextControlMode, switchToPos=switchToPos, switchToPlace=switchToPlace))


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
        if not BattleReplay.g_replayCtrl.isPlaying:
            TriggersManager.g_manager.fireTriggerInstantly(TRIGGER_TYPE.PLAYER_ENTER_SPG_STRATEGIC_MODE)

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
        if not BattleReplay.g_replayCtrl.isPlaying:
            TriggersManager.g_manager.fireTriggerInstantly(TRIGGER_TYPE.PLAYER_ENTER_SPG_SNIPER_MODE)

    def disable(self):
        super(ArtyControlMode, self).disable()
        self.strategicCamera = STRATEGIC_CAMERA.AERIAL


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
            self._handleShootCmd()
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


class _PostmortemSwitchType(Enum):
    NONE = 0
    DIRECT_TARGETING = 1
    CYCLE_VEHICLES = 2
    PLAYERS_PANEL = 3
    CONTROL_MODE_CHANGE = 4
    VIEWPOINT = 4


class PostMortemControlMode(IControlMode, CallbackDelayer):
    _IS_POSTMORTEM_DELAY_ENABLED = True
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    __aimOffset = aih_global_binding.bindRO(aih_global_binding.BINDING_ID.AIM_OFFSET)

    @property
    def aimingMode(self):
        pass

    @staticmethod
    def getIsPostmortemDelayEnabled():
        return PostMortemControlMode._IS_POSTMORTEM_DELAY_ENABLED

    @staticmethod
    def setIsPostmortemDelayEnabled(value):
        PostMortemControlMode._IS_POSTMORTEM_DELAY_ENABLED = value

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
        CallbackDelayer.__init__(self)
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
        self.__selectedTargetID = None
        self.__endOfRound = False
        self.__transitionDuration = dataSection['camera'].readFloat('linearTransitionDuration')
        self.__transitionCamera = BigWorld.TransitionCamera()
        self.__targetCamera = BigWorld.HomingCamera(None)
        self.__targetCamera.cameraPositionProvider = Math.Vector4Basic()
        self.__targetCamera.aimPointProvider = Math.Vector4Basic()
        self.__vehicleSwitchType = _PostmortemSwitchType.NONE
        self.__nextVehicleIdIndex = 0
        self.__previousPostmortemVehicleID = None
        return

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

    def isSelfVehicle(self):
        return self.__curVehicleID == BigWorld.player().playerVehicleID

    def prerequisites(self):
        return []

    def create(self):
        self.__cam.create(onChangeControlMode=None, postmortemMode=True, smartPointCalculator=False)
        return

    def destroy(self):
        CallbackDelayer.destroy(self)
        self.disable()
        self.__cam.destroy()
        self.__cam = None
        return

    def enable(self, **args):
        SoundGroups.g_instance.changePlayMode(0)
        playerPostmortemViewPointDefined = False
        player = BigWorld.player()
        if player is None:
            return
        else:
            playerVehicle = BigWorld.entities.get(player.playerVehicleID)
            if playerVehicle:
                playerPostmortemViewPointDefined = playerVehicle.isPostmortemViewPointDefined
            self.__isObserverMode = 'observer' in player.vehicleTypeDescriptor.type.tags
            newVehicleID = args.get('newVehicleID', None)
            specCtrl = self.guiSessionProvider.shared.spectator
            if specCtrl is not None:
                specCtrl.spectatorViewModeChanged(SPECTATOR_MODE.FOLLOW)
            self.__curVehicleID = self.__getInitialVehicleID(newVehicleID)
            shouldSwitchToAlly = bool(args.get('immediateSwitchToAllyVehicle', False))
            camDuration = args.get('transitionDuration', -1)
            camMatrix = args.get('camMatrix', None)
            hasDuration = self.__hasCameraTransitionDuration()
            keepRotation = args.get('prevModeName', '') == CTRL_MODE_NAME.DEATH_FREE_CAM
            camTransitionParams = {'cameraTransitionDuration': camDuration if hasDuration and not shouldSwitchToAlly else 0,
             'camMatrix': camMatrix,
             'keepRotation': keepRotation or args.get('keepCameraSettings', False),
             'newVehicleID': newVehicleID,
             'pivotSettings': args.get('pivotSettings', None),
             'distanceFromFocus': args.get('distanceFromFocus', None)}
            if self.__isObserverMode and player.vehicle is None and not player.isObserverFPV:
                player.consistentMatrices.notifyPreBind(player)
            self.__cam.enable(None, False, args.get('postmortemParams'), None, None, camTransitionParams)
            foundEntity = BigWorld.entities.get(newVehicleID) if newVehicleID is not None else None
            if foundEntity:
                self.__cam.vehicleMProv = foundEntity.matrix
            else:
                self.__cam.vehicleMProv = player.consistentMatrices.attachedVehicleMatrix
            self.__connectToArena()
            _setCameraFluency(self.__cam.camera, self.__CAM_FLUENCY)
            self.__isEnabled = True
            player.consistentMatrices.onVehicleMatrixBindingChanged += self._onMatrixBound
            self.guiSessionProvider.shared.feedback.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
            if self.__isObserverMode:
                vehicleID = args.get('vehicleID')
                self.__cam.vehicleMProv = BigWorld.player().consistentMatrices.attachedVehicleMatrix
                if vehicleID is None:
                    self.__switch()
                else:
                    self.__fakeSwitchToVehicle(vehicleID)
                return
            isRespawnEnabled = self.guiSessionProvider.dynamic.respawn is not None
            isDelayRequired = bool(args.get('bPostmortemDelay'))
            isDelayOrRespawnEnabled = isRespawnEnabled or self._isPostmortemDelayEnabled()
            if isDelayRequired and isDelayOrRespawnEnabled and not playerPostmortemViewPointDefined:
                self.__startPostmortemDelay()
            if isRespawnEnabled and self.__processRespawn():
                return
            if playerPostmortemViewPointDefined:
                matrix = Math.Matrix(player.consistentMatrices.attachedVehicleMatrix)
                self.__cam.setYawPitch(matrix.yaw, -matrix.pitch)
            if self.__postmortemDelay is not None:
                return
            vehData = BigWorld.entities.get(self.__curVehicleID, None)
            if vehData is not None:
                self.__cam.vehicleMProv = vehData.matrix
            if shouldSwitchToAlly:
                self.guiSessionProvider.shared.viewPoints.updateAttachedVehicle(self.__curVehicleID)
                self.__switch()
                return
            isAttachedOnVehicle = DeathFreeCamMode.isAttachedOnVehicle(self.__curVehicleID)
            self.__vehicleSwitchType = _PostmortemSwitchType.CONTROL_MODE_CHANGE
            self.selectPlayer(self.__curVehicleID)
            if isAttachedOnVehicle:
                self.onSwitchViewpoint(self.__curVehicleID, Math.Vector3(0.0, 0.0, 0.0))
                self._onMatrixBound(False)
            return

    def disable(self):
        self.clearCallbacks()
        specCtrl = self.guiSessionProvider.shared.spectator
        if specCtrl is not None:
            specCtrl.spectatorViewModeChanged(SPECTATOR_MODE.NONE)
        ctrl = self.guiSessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onRespawnInfoUpdated -= self.__onRespawnInfoUpdated
        self._targetCtrlModeAfterDelay = None
        self.__altTargetMode = None
        self.__isEnabled = False
        self.__resetSwitchType()
        self._destroyPostmortemDelay()
        self.__disconnectFromArena()
        BigWorld.player().consistentMatrices.onVehicleMatrixBindingChanged -= self._onMatrixBound
        self.guiSessionProvider.shared.feedback.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
        if self.__transitionCamera.isInTransition():
            self.__transitionCamera.finish()
        self.__cam.disable()
        self.__curVehicleID = None
        return

    def handleKeyEvent(self, isDown, key, mods, event=None):
        if self.__transitionCamera.isInTransition():
            return
        cmdMap = CommandMapping.g_instance
        guiCtrlEnabled = BigWorld.player().isForcedGuiControlMode()
        if BigWorld.isKeyDown(Keys.KEY_CAPSLOCK) and isDown and key == Keys.KEY_F3 and (self.__videoControlModeAvailable or self.guiSessionProvider.getCtx().isPlayerObserver()):
            if not self.__aih.isControlModeChangeAllowed():
                return
            self.__aih.onControlModeChanged(CTRL_MODE_NAME.VIDEO, prevModeName=CTRL_MODE_NAME.POSTMORTEM, camMatrix=self.__cam.camera.matrix, curVehicleID=self.__curVehicleID)
            return True
        if not guiCtrlEnabled and isDown:
            if cmdMap.isFired(CommandMapping.CMD_CM_POSTMORTEM_SELF_VEHICLE, key) and BigWorld.player().isPostmortemFeatureEnabled(CTRL_MODE_NAME.DEATH_FREE_CAM):
                if self.__canSwitchVehicle(checkArcadeCamTransition=True):
                    self._switchToCtrlMode(CTRL_MODE_NAME.DEATH_FREE_CAM)
                    return True
            if not (BigWorld.player().isPostmortemModificationActive(CTRL_MODE_NAME.POSTMORTEM, POSTMORTEM_MODIFIERS.DISABLE_TANK_TARGET_FOLLOW) and self.__canSwitchVehicle(checkArcadeCamTransition=True)):
                if cmdMap.isFired(CommandMapping.CMD_CM_POSTMORTEM_TARGET_VEHICLE, key):
                    hasValidTarget, targetID = DeathFreeCamMode.getVehicleFollowTarget()
                    if hasValidTarget:
                        self.__switchToVehicle(targetID)
                        return True
            if not BigWorld.player().isPostmortemModificationActive(CTRL_MODE_NAME.POSTMORTEM, POSTMORTEM_MODIFIERS.DISABLE_TANK_CYCLE):
                if cmdMap.isFired(CommandMapping.CMD_CM_POSTMORTEM_NEXT_VEHICLE, key):
                    self.__switch()
                    return True
                if cmdMap.isFired(CommandMapping.CMD_CM_POSTMORTEM_PREV_VEHICLE, key):
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
        if self.__transitionCamera.isInTransition():
            return
        else:
            GUI.mcursor().position = self.__aimOffset
            if self.__postmortemDelay is not None:
                self.__postmortemDelay.handleMouseEvent(dx, dy, dz)
                return True
            self.__cam.update(dx, dy, math_utils.clamp(-1, 1, dz))
            return True

    def onRecreateDevice(self):
        pass

    def selectPlayer(self, vehID):
        self.__switchToVehicle(vehID)

    def selectViewPoint(self, pointID):
        self.__switchToViewpoint(pointID)

    def onSwitchViewpoint(self, vehicleID, cameraPos):
        self.__setCurrentVehicleID(vehicleID)
        self.__handleVehicleChange()
        if self.__vehicleSwitchType == _PostmortemSwitchType.NONE:
            self.__vehicleSwitchType = _PostmortemSwitchType.PLAYERS_PANEL
        allowSmoothTransition = not self.__endOfRound and self.__vehicleSwitchType in (_PostmortemSwitchType.PLAYERS_PANEL, _PostmortemSwitchType.DIRECT_TARGETING)
        if self.__isVehicleSwitchFailed():
            self.__resetSwitchType()
            self.__switch()
            return
        if allowSmoothTransition:
            self.__transitionToCurrentVehicle()
        self.__resetSwitchType()

    def setGUIVisible(self, isVisible):
        pass

    def __onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        if eventID == FEEDBACK_EVENT_ID.ENTITY_IN_FOCUS:
            isInFocus, entityType = value
            if entityType == ENTITY_IN_FOCUS_TYPE.VEHICLE:
                player = BigWorld.player()
                if DeathFreeCamMode.canObserveVehicle(player, vehicleID):
                    self.guiSessionProvider.shared.spectator.toggleFollowHint(isInFocus)

    def _switchToCtrlMode(self, targetMode):
        if self.curPostmortemDelay is not None or targetMode is None:
            return
        else:
            self.__previousPostmortemVehicleID = self.__curVehicleID
            self.__switchToVehicle(None, unbind=targetMode == CTRL_MODE_NAME.DEATH_FREE_CAM)
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
            if not self.__isObserverMode:
                self.guiSessionProvider.shared.feedback.showVehicleMarker(self.__previousPostmortemVehicleID)
                self.guiSessionProvider.shared.feedback.hideVehicleMarker(self.curVehicleID)
            return

    def __getCameraTransitionDuration(self, sourceVehicleID, targetVehicleID):
        currVehicleMatrix = self.__getVehicleMatrix(sourceVehicleID)
        targetVehicleMatrix = self.__getVehicleMatrix(targetVehicleID)
        if not currVehicleMatrix or not targetVehicleMatrix:
            return 0
        else:
            currVehiclePos = Math.Matrix(currVehicleMatrix).translation
            targetVehiclePos = Math.Matrix(targetVehicleMatrix).translation
            collision = BigWorld.wg_collideDynamicStatic(BigWorld.player().spaceID, currVehiclePos, targetVehiclePos, 0, sourceVehicleID)
            duration = 0 if collision is not None and not collision[1] else self.__transitionDuration
            return duration

    def __getVehicleMatrix(self, vehicleID):
        vehicle = BigWorld.entities.get(vehicleID)
        if not vehicle:
            return
        else:
            vehicleMatrix = None
            if vehicle.appearance.compoundModel is not None:
                vehicleMatrix = vehicle.appearance.compoundModel.node('HP_gunJoint')
            if not vehicleMatrix:
                vehicleMatrix = BigWorld.entities.get(vehicleID).matrix
            return vehicleMatrix

    def __transitionToCurrentVehicle(self):
        if self.__transitionCamera.isInTransition():
            return
        elif self.__curVehicleID == self.__previousPostmortemVehicleID:
            return
        else:
            prevVehicle = BigWorld.entities.get(self.__previousPostmortemVehicleID)
            targetVehicle = BigWorld.entities.get(self.__curVehicleID)
            if prevVehicle is None or targetVehicle is None or prevVehicle.appearance is None or targetVehicle.appearance is None:
                return
            duration = self.__getCameraTransitionDuration(self.__previousPostmortemVehicleID, self.__curVehicleID)
            if duration == 0:
                return
            prevVehiclePos = prevVehicle.position
            targetVehiclePos = targetVehicle.position
            cameraFinalPosition = targetVehiclePos + (self.camera.camera.position - prevVehiclePos)
            targetCameraPosProvider = self.__targetCamera.cameraPositionProvider
            targetCameraPosProvider.value = Math.Vector4(cameraFinalPosition.x, cameraFinalPosition.y, cameraFinalPosition.z, 1.0)
            self.__cam.vehicleMProv = targetVehicle.matrix
            aimPoint = Math.Vector4(self.__cam.camera.aimPointProvider.value.x, self.__cam.camera.aimPointProvider.value.y, self.__cam.camera.aimPointProvider.value.z, 1.0)
            camAimProvider = self.__targetCamera.aimPointProvider
            camAimProvider.value = aimPoint
            self.__transitionCamera.start(BigWorld.camera().matrix, self.__targetCamera, duration)
            BigWorld.camera(self.__transitionCamera)
            self.delayCallback(duration, self.__finishCameraTransition)
            return

    def __hasCameraTransitionDuration(self):
        targetVehicle = BigWorld.entities.get(self.__curVehicleID)
        if targetVehicle is None:
            return False
        else:
            collision = BigWorld.wg_collideDynamicStatic(BigWorld.player().spaceID, BigWorld.camera().position, targetVehicle.position)
            return False if collision and not collision[1] else True

    def __processRespawn(self):
        respawnCtrl = self.guiSessionProvider.dynamic.respawn
        hasRespawnInfo = respawnCtrl.respawnInfo is not None
        self._targetCtrlModeAfterDelay = CTRL_MODE_NAME.RESPAWN_DEATH if hasRespawnInfo else None
        respawnCtrl.onRespawnInfoUpdated += self.__onRespawnInfoUpdated
        if not hasRespawnInfo:
            return False
        else:
            self.__onRespawnInfoUpdated(respawnCtrl.respawnInfo)
            return True

    def __startPostmortemDelay(self):
        if BattleReplay.g_replayCtrl.isPlaying:
            return
        self.__postmortemDelay = PostmortemDelay(self.__cam, self._onPostmortemDelayStart, self._onPostmortemDelayStop, self._isPostmortemDelayEnabled())
        self.__postmortemDelay.start()

    def __finishCameraTransition(self):
        if self.__transitionCamera.isInTransition():
            return 0.1
        BigWorld.camera(self.__cam.camera)
        self.__aih.notifyCameraChanged()

    def __getValidVehicleID(self, vehicleID):
        return BigWorld.player().playerVehicleID if vehicleID is None or vehicleID == -1 else vehicleID

    def __getInitialVehicleID(self, requestedID=None):
        if requestedID is not None:
            return requestedID
        else:
            replayCtrl = BattleReplay.g_replayCtrl
            if replayCtrl.isPlaying and replayCtrl.playerVehicleID:
                return replayCtrl.playerVehicleID
            return self.__previousPostmortemVehicleID if self.__previousPostmortemVehicleID is not None else BigWorld.player().playerVehicleID

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
            self.__vehicleSwitchType = _PostmortemSwitchType.CYCLE_VEHICLES
            self.__doPreBind()
            self.onSwitchViewpoint(vehicleID, Math.Vector3(0.0, 0.0, 0.0))
            return

    def __switchToViewpoint(self, toId):
        if not self.__canSwitchVehicle():
            return
        self.__vehicleSwitchType = _PostmortemSwitchType.VIEWPOINT
        self.__doPreBind()
        self.guiSessionProvider.shared.viewPoints.selectViewPoint(toId)

    def __switch(self, isNext=True):
        if not self.__canSwitchVehicle():
            return
        self.__vehicleSwitchType = _PostmortemSwitchType.CYCLE_VEHICLES
        self.__doPreBind()
        self.guiSessionProvider.shared.viewPoints.switch(isNext)
        self.delayCallback(0.5, self.__resetSwitchType)

    def __resetSwitchType(self):
        self.__vehicleSwitchType = _PostmortemSwitchType.NONE

    def __switchToVehicle(self, targetID=None, unbind=False):
        if not self.__canSwitchVehicle():
            return
        isAttachedOnVehicle = DeathFreeCamMode.isAttachedOnVehicle(targetID)
        self.__vehicleSwitchType = _PostmortemSwitchType.DIRECT_TARGETING
        self.__doPreBind()
        if targetID or not unbind:
            self.guiSessionProvider.shared.viewPoints.selectVehicle(targetID)
        elif unbind:
            self.guiSessionProvider.shared.viewPoints.unselectVehicle()
        if isAttachedOnVehicle:
            self.onSwitchViewpoint(targetID, Math.Vector3(0.0, 0.0, 0.0))

    def __doPreBind(self):
        if self.__curVehicleID is None:
            return
        else:
            vehicle = BigWorld.entity(self.__curVehicleID)
            if vehicle is not None:
                vehicle.removeCameraCollider()
            return

    def __isVehicleSwitchFailed(self):
        player = BigWorld.player()
        replayCtrl = BattleReplay.g_replayCtrl
        return self.__curVehicleID != player.playerVehicleID and self.__curVehicleID is not None and BigWorld.entity(self.__curVehicleID) is None and not replayCtrl.isPlaying and not self.__isObserverMode and player.arena.positions.get(self.__curVehicleID) is None

    def __setCurrentVehicleID(self, newVehicleID):
        self.__previousPostmortemVehicleID = self.__getValidVehicleID(self.__curVehicleID)
        self.__curVehicleID = self.__getValidVehicleID(newVehicleID)

    def __handleVehicleChange(self):
        vehicleID = self.__curVehicleID
        self.guiSessionProvider.switchVehicle(vehicleID)
        if vehicleID in BigWorld.entities.keys():
            self.__aih.onCameraChanged(CTRL_MODE_NAME.POSTMORTEM, vehicleID)

    def __canSwitchVehicle(self, checkArcadeCamTransition=False):
        if self.__postmortemDelay is not None:
            return False
        elif self.__transitionCamera.isInTransition():
            return False
        elif checkArcadeCamTransition and self.__cam.isCamInTransition:
            return False
        else:
            return False if not self.__aih.isAllowToSwitchPositionOrFPV() else self.__vehicleSwitchType in [_PostmortemSwitchType.NONE, _PostmortemSwitchType.CONTROL_MODE_CHANGE]

    def __onPeriodChange(self, period, *args):
        if period != constants.ARENA_PERIOD.AFTERBATTLE:
            return
        elif self.__isObserverMode:
            return
        else:
            self.__endOfRound = True
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
        player.arena.onVehicleKilled += self.__onArenaVehicleKilled
        player.onVehicleLeaveWorld += self.__onVehicleLeaveWorld

    def __disconnectFromArena(self):
        player = BigWorld.player()
        player.arena.onPeriodChange -= self.__onPeriodChange
        player.arena.onVehicleKilled -= self.__onArenaVehicleKilled
        player.onVehicleLeaveWorld -= self.__onVehicleLeaveWorld


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
    return not camera.getUserConfigValue('sniperModeByShift') or aih.isObserverFPV


_DEFAULT_SPEED_LEVEL_LIMITS = (7, 13, 19)

class DeathFreeCamMode(VideoCameraControlMode, CallbackDelayer):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    markersManager = None

    def __init__(self, dataSection, avatarInputHandler):
        super(DeathFreeCamMode, self).__init__(dataSection, avatarInputHandler)
        CallbackDelayer.__init__(self)
        self.__forcedGuiControlEnabled = False
        self.__curVehicleID = None
        self.__disableHints = int(dataSection.readFloat('disableHints'))
        g_eventBus.addListener(events.MarkersManagerEvent.MARKERS_CREATED, self.__onMarkersManagerMarkersCreated, EVENT_BUS_SCOPE.BATTLE)
        return

    def destroy(self):
        CallbackDelayer.destroy(self)
        g_eventBus.removeListener(events.MarkersManagerEvent.MARKERS_CREATED, self.__onMarkersManagerMarkersCreated, EVENT_BUS_SCOPE.BATTLE)
        self.disable()
        super(DeathFreeCamMode, self).destroy()

    def __onMarkersManagerMarkersCreated(self, event):
        g_eventBus.removeListener(events.MarkersManagerEvent.MARKERS_CREATED, self.__onMarkersManagerMarkersCreated, EVENT_BUS_SCOPE.BATTLE)
        DeathFreeCamMode.markersManager = event.getMarkersManager()

    @staticmethod
    def getVehicleFollowTarget():
        player = BigWorld.player()
        target = BigWorld.target()
        if target is not None:
            targetID = target.id
        else:
            targetID = None
            if DeathFreeCamMode.markersManager is not None:
                tID, _, _ = DeathFreeCamMode.markersManager.getCurrentlyAimedAtMarkerIDAndType()
                target = BigWorld.entities.get(tID)
                if target is not None and isinstance(target, VehicleEntity) and target.isAlive():
                    targetID = tID
            if targetID is None and player.target is not None:
                targetID = player.target.id
            if targetID is None:
                return (False, -1)
        if DeathFreeCamMode.isAttachedOnVehicle(targetID):
            return (False, -1)
        elif player.vehicle is not None and player.vehicle.id == targetID:
            return (True, targetID)
        else:
            return (True, targetID) if DeathFreeCamMode.canObserveVehicle(player, targetID) else (False, -1)

    @staticmethod
    def isAttachedOnVehicle(vehicleID):
        vehicle = BigWorld.player().getVehicleAttached()
        return True if vehicle is not None and vehicle.id == vehicleID else False

    @staticmethod
    def canObserveVehicle(player, vehicleID):
        vehicleData = player.arena.vehicles.get(vehicleID)
        if vehicleData is None:
            return False
        else:
            isVehicleAlive = vehicleData.get('isAlive', False)
            vehicleTeam = vehicleData.get('team', 0)
            vehicleDescription = vehicleData.get('vehicleType', None)
            vehicleType = vehicleDescription.type if vehicleDescription is not None else None
            isUnobservable = 'unobservable' in vehicleType.tags if vehicleType is not None else False
            return True if isVehicleAlive and vehicleTeam == player.team and not isUnobservable else False

    def enable(self, **args):
        VideoCameraControlMode.enable(self, **args)
        specCtrl = self.guiSessionProvider.shared.spectator
        if specCtrl is not None:
            specCtrl.spectatorViewModeChanged(SPECTATOR_MODE.FREECAM)
        ctrl = self.guiSessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onRespawnInfoUpdated += self.__onRespawnInfoUpdated
            if ctrl.respawnInfo is not None:
                self.__onRespawnInfoUpdated(ctrl.respawnInfo)
        curVehicleID = args.get('curVehicleID', None)
        if curVehicleID != -1:
            self.__curVehicleID = curVehicleID
            self.delayCallback(args.get('transitionDuration', 0), self.guiSessionProvider.shared.feedback.showVehicleMarker, curVehicleID)
        self.__forcedGuiControlEnabled = BigWorld.player().isForcedGuiControlMode()
        self.guiSessionProvider.shared.feedback.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
        self.guiSessionProvider.switchVehicle(None)
        self.guiSessionProvider.shared.viewPoints.updateAttachedVehicle(None)
        AccountSettings.setSettings(FREE_CAM_USES_COUNT, AccountSettings.getSettings(FREE_CAM_USES_COUNT) + 1)
        return

    def disable(self):
        self.clearCallbacks()
        VideoCameraControlMode.disable(self)
        self.guiSessionProvider.shared.feedback.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
        ctrl = self.guiSessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onRespawnInfoUpdated -= self.__onRespawnInfoUpdated
        return

    def handleKeyEvent(self, isDown, key, mods, event=None):
        self._cam.handleKeyEvent(key, isDown)
        if self.__forcedGuiControlEnabled:
            return False
        else:
            cmdMap = CommandMapping.g_instance
            if self._aih.isControlModeChangeAllowed():
                if cmdMap.isFired(CommandMapping.CMD_CM_POSTMORTEM_TARGET_VEHICLE, key) and isDown:
                    hasValidTarget, targetID = DeathFreeCamMode.getVehicleFollowTarget()
                    if hasValidTarget:
                        collision = self._raycastToTarget(targetID)
                        transitionDuration = -1 if collision and collision[1] else 0
                        self.__changeVehicle(targetID, transitionDuration)
                        return True
                if cmdMap.isFired(CommandMapping.CMD_CM_FREE_CAMERA_PREV_VEHICLE, key) and isDown:
                    aliveAllies = self.__getAliveAllies()
                    playerVehicleID = self.guiSessionProvider.getArenaDP().getPlayerVehicleID()
                    if self.__curVehicleID is not None and self.__curVehicleID in aliveAllies or self.__curVehicleID == playerVehicleID:
                        nextVehicle = self.__curVehicleID
                    elif aliveAllies:
                        nextVehicle = aliveAllies[0]
                    else:
                        nextVehicle = playerVehicleID
                    self.__changeVehicle(nextVehicle, 1)
                    return True
            return False

    def selectPlayer(self, vehID):
        self.__changeVehicle(vehID)

    def alwaysReceiveKeyEvents(self, isDown=True):
        return True

    def setForcedGuiControlMode(self, enable):
        self.__forcedGuiControlEnabled = enable

    def overridePose(self, pos, rot):
        transform = Math.Matrix()
        transform.setRotateYPR(rot)
        transform.translation = self._cam._checkSpaceBounds(BigWorld.camera().position, pos)
        self._cam.setViewMatrix(transform)

    def isSelfVehicle(self):
        return False

    def onSwitchViewpoint(self, vehicleID, cameraPos):
        collision = self._raycastToTarget(vehicleID)
        transitionDuration = -1 if collision and collision[1] else 0
        self.__changeVehicle(vehicleID, transitionDuration)
        self.guiSessionProvider.switchVehicle(vehicleID)

    def showFreeCamHints(self):
        return AccountSettings.getSettings(FREE_CAM_USES_COUNT) <= self.__disableHints

    def _raycastToTarget(self, targetID):
        targetVehicle = BigWorld.entities.get(targetID)
        if targetVehicle is None:
            return
        else:
            targetVehiclePos = BigWorld.entities.get(targetID).position
            return BigWorld.wg_collideDynamicStatic(BigWorld.player().spaceID, self._cam.position, targetVehiclePos, 0, 0, -1)

    def _createCamera(self, cameraDataSection):
        self._cam = FreeVideoCamera(cameraDataSection)

    def __onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        if eventID == FEEDBACK_EVENT_ID.ENTITY_IN_FOCUS:
            isInFocus, entityType = value
            if entityType == ENTITY_IN_FOCUS_TYPE.VEHICLE:
                player = BigWorld.player()
                if DeathFreeCamMode.canObserveVehicle(player, vehicleID):
                    self.guiSessionProvider.shared.spectator.toggleFollowHint(isInFocus)

    def __getAliveAllies(self):
        from gui.Scaleform.daapi.view.battle.shared.stats_exchange.vehicle import TeamsSortedIDsComposer
        sortedIdComposer = TeamsSortedIDsComposer()
        sortedIdComposer.addSortIDs(False, self.guiSessionProvider.getArenaDP())
        sortedIds = {'leftItemsIDs': [],
         'rightItemsIDs': []}
        sortedIds = sortedIdComposer.compose(sortedIds)
        aliveAllies = [ vID for vID in sortedIds['leftItemsIDs'] if BigWorld.player().arena.vehicles.get(vID)['isAlive'] ]
        return aliveAllies

    def __changeVehicle(self, vehicleID, transitionTime=-1):
        durations = self._cameraTransitionDurations
        if transitionTime >= 0:
            durations = {CTRL_MODE_NAME.POSTMORTEM: transitionTime}
        targetMode = BigWorld.player().getNextControlMode()
        if targetMode == CTRL_MODE_NAME.POSTMORTEM:
            self.guiSessionProvider.shared.feedback.showVehicleMarker(self.__curVehicleID)
            BigWorld.player().inputHandler.onControlModeChanged(targetMode, prevModeName=CTRL_MODE_NAME.DEATH_FREE_CAM, camMatrix=Math.Matrix(BigWorld.camera().matrix), newVehicleID=vehicleID, bPostmortemDelay=False, transitionDuration=durations[targetMode])
            specCtrl = self.guiSessionProvider.shared.spectator
            if specCtrl is not None:
                specCtrl.spectatorViewModeChanged(SPECTATOR_MODE.FOLLOW)
        else:
            _logger.debug('Unsupported Ctrl mode switch attempt %s', targetMode)
        return

    def __onRespawnInfoUpdated(self, respawnInfo):
        if respawnInfo is not None:
            self.selectPlayer(None)
            BigWorld.player().inputHandler.onControlModeChanged(CTRL_MODE_NAME.RESPAWN_DEATH, prevModeName=CTRL_MODE_NAME.POSTMORTEM, camMatrix=Math.Matrix(BigWorld.camera().matrix), curVehicleID=self.curVehicleID, transitionDuration=self._cameraTransitionDurations[CTRL_MODE_NAME.RESPAWN_DEATH])
        return
