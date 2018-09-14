# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/control_modes.py
import math
import weakref
from collections import namedtuple
import BigWorld
import Math
import Keys
import GUI
import ResMgr
from AvatarInputHandler import mathUtils, AimingSystems
import cameras
import aims
import CommandMapping
import constants
import BattleReplay
import TriggersManager
import SoundGroups
from TriggersManager import TRIGGER_TYPE
from gui.battle_control import g_sessionProvider
from post_processing import g_postProcessing
from constants import AIMING_MODE
from gui import DEPTH_OF_GunMarker, GUI_SETTINGS
from gui.Scaleform.Flash import Flash
from debug_utils import *
from ProjectileMover import collideDynamicAndStatic, getCollidableEntities
from PostmortemDelay import PostmortemDelay
import VideoCamera
from DynamicCameras import SniperCamera, StrategicCamera, ArcadeCamera
_ARCADE_CAM_PIVOT_POS = Math.Vector3(0, 4, 3)

class IControlMode(object):

    def prerequisites(self):
        return []

    def create(self):
        pass

    def destroy(self):
        pass

    def dumpState(self):
        pass

    def enable(self, **args):
        pass

    def disable(self):
        pass

    def handleKeyEvent(self, isDown, key, mods, event=None):
        pass

    def handleMouseEvent(self, dx, dy, dz):
        pass

    def showGunMarker(self, flag):
        pass

    def showGunMarker2(self, flag):
        pass

    def updateGunMarker(self, pos, dir, size, relaxTime, collData):
        pass

    def updateGunMarker2(self, pos, dir, size, relaxTime, collData):
        pass

    def resetGunMarkers(self):
        pass

    def setAimingMode(self, enable, mode):
        pass

    def getAimingMode(self, mode):
        pass

    def resetAimingMode(self):
        pass

    def getDesiredShotPoint(self):
        pass

    def updateShootingStatus(self, canShoot):
        pass

    def updateTrajectory(self):
        pass

    def onRecreateDevice(self):
        pass

    def getAim(self):
        return None

    def setGUIVisible(self, isVisible):
        pass

    def selectPlayer(self, index):
        pass

    def onMinimapClicked(self, worldPos):
        pass

    def onSwitchViewpoint(self, vehicleID, cameraPos):
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

    def __init__(self, avatarInputHandler, mode='arcade', isStrategic=False):
        self._aih = weakref.proxy(avatarInputHandler)
        self.__createGunMarker(mode, isStrategic)
        self._isEnabled = False
        self._aim = None
        self._cam = None
        self._aimingMode = 0
        self._canShot = False
        return

    def prerequisites(self):
        out = []
        out += self._gunMarker.prerequisites()
        if self._aim is not None:
            out += self._aim.prerequisites()
        return out

    def create(self):
        self._gunMarker.create()
        if self._aim is not None:
            self._aim.create()
        self.disable()
        return

    def enable(self, **args):
        self._isEnabled = True
        self._aimingMode = args.get('aimingMode', self._aimingMode)
        if self._aim is not None:
            self._aim.enable()
        ctrlState = args.get('ctrlState')
        self._gunMarker.enable(ctrlState.get('gunMarker', None))
        return

    def disable(self):
        self._isEnabled = False
        self._cam.disable()
        self._gunMarker.disable()
        if self._aim is not None:
            self._aim.disable()
        return

    def destroy(self):
        self._aih.onSetReloading -= self._gunMarker.setReloading
        self._aih.onSetReloadingPercents -= self._gunMarker.setReloadingInPercent
        self._gunMarker.destroy()
        self._aih = None
        self._cam.destroy()
        self._cam = None
        if self._aim is not None:
            self._aim.destroy()
        return

    def showGunMarker(self, flag):
        self._gunMarker.show(flag)

    def showGunMarker2(self, flag):
        self._gunMarker.show2(flag)

    def updateGunMarker(self, pos, dir, size, relaxTime, collData):
        assert self._isEnabled
        self._gunMarker.update(pos, dir, size, relaxTime, collData)

    def updateGunMarker2(self, pos, dir, size, relaxTime, collData):
        assert self._isEnabled
        self._gunMarker.update2(pos, dir, size, relaxTime, collData)

    def setAimingMode(self, enable, mode):
        if enable:
            self._aimingMode |= mode
        else:
            self._aimingMode &= -1 - mode

    def resetAimingMode(self):
        self._aimingMode = 0

    def getDesiredShotPoint(self):
        assert self._isEnabled
        return self._cam.aimingSystem.getDesiredShotPoint() if self._aimingMode == 0 and self._cam is not None and self._aim is not None else None

    def getAimingMode(self, mode):
        return self._aimingMode & mode == mode

    def onRecreateDevice(self):
        self._gunMarker.onRecreateDevice()
        self._aim.onRecreateDevice()

    def getAim(self):
        return self._aim

    def dumpState(self):
        return {'gunMarker': self._gunMarker.dumpState()}

    def updateShootingStatus(self, canShot):
        assert self._isEnabled
        self._canShot = canShot

    def __createGunMarker(self, mode, isStrategic):
        if not GUI_SETTINGS.isGuiEnabled():
            from gui.development.no_gui.battle import GunMarker
            self._gunMarker = GunMarker()
            return
        self._gunMarker = _SuperGunMarker(mode, isStrategic)
        self._aih.onSetReloading += self._gunMarker.setReloading
        self._aih.onSetReloadingPercents += self._gunMarker.setReloadingInPercent


class CameraLocationPoint():
    name = property(lambda self: self.__name)
    matrix = property(lambda self: self.__matrix)

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
        super(VideoCameraControlMode, self).__init__(avatarInputHandler)
        self.__prevModeName = None
        cameraDataSection = dataSection['camera'] if dataSection is not None else ResMgr.DataSection('camera')
        self.__showGunMarkerKey = getattr(Keys, cameraDataSection.readString('keyShowGunMarker', ''), None)
        self.__showGunMarker = False
        self._cam = VideoCamera.VideoCamera(cameraDataSection)
        self.__curVehicleID = None
        locationXmlPath = 'spaces/' + BigWorld.player().arena.arenaType.geometryName + '/locations.xml'
        xmlSec = ResMgr.openSection(locationXmlPath)
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
        self._gunMarker.setGUIVisible(self.__showGunMarker)
        return

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
                    self.__showGunMarker = not self.__showGunMarker
                    self._gunMarker.setGUIVisible(self.__showGunMarker)
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

    def dumpState(self):
        return dumpStateEmpty()

    def enable(self, **args):
        self.__prevModeName = args.get('prevModeName')
        camMatrix = args.get('camMatrix')
        self.__cam.enable(camMatrix)
        BigWorld.setWatcher('Client Settings/Strafe Rate', 50)
        BigWorld.setWatcher('Client Settings/Camera Mass', 1)
        assert constants.IS_DEVELOPMENT
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
        if BigWorld.isKeyDown(Keys.KEY_CAPSLOCK) and constants.IS_DEVELOPMENT and isDown and key == Keys.KEY_F1:
            self.__aih.onControlModeChanged(self.__prevModeName)
            return True
        return True if self.__videoControl.handleKeyEvent(isDown, key, mods, event) else self.__cam.handleKey(event)

    def handleMouseEvent(self, dx, dy, dz):
        assert self.__isEnabled
        GUI.mcursor().position = (0, 0)
        return self.__videoControl.handleMouseEvent(dx, dy, dz)

    def getDesiredShotPoint(self):
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
        self.__shellingControl.destroy()
        self.__shellingControl = None
        self.__cam.destroy()
        self.__cam = None
        self.__isCreated = False
        return

    def dumpState(self):
        return dumpStateEmpty()

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
        self.__shellingControl.setEnable(False)
        self.__cam.disable()
        self.__isEnabled = False

    def handleKeyEvent(self, isDown, key, mods, event=None):
        assert self.__isEnabled
        if BigWorld.isKeyDown(Keys.KEY_CAPSLOCK) and constants.IS_DEVELOPMENT and isDown and key == Keys.KEY_F2:
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

    def __init__(self, dataSection, avatarInputHandler):
        super(ArcadeControlMode, self).__init__(avatarInputHandler, mode='arcade')
        self._aim = aims.createAim(dataSection.readString('aim'))
        self._cam = ArcadeCamera.ArcadeCamera(dataSection['camera'], self._aim)
        self.__mouseVehicleRotator = _MouseVehicleRotator()
        self.__isArenaStarted = False
        self.__sightOffset = list(self._aim.offset())
        self.__videoControlModeAvailable = dataSection.readBool('videoModeAvailable', constants.IS_DEVELOPMENT)
        self.__videoControlModeAvailable &= BattleReplay.g_replayCtrl.isPlaying or constants.IS_DEVELOPMENT

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
        arena = BigWorld.player().arena
        if arena is not None:
            arena.onPeriodChange += self.__onArenaStarted
            self.__onArenaStarted(arena.period)
        g_postProcessing.enable('arcade')
        return

    def disable(self):
        super(ArcadeControlMode, self).disable()
        arena = BigWorld.player().arena
        if arena is not None:
            arena.onPeriodChange -= self.__onArenaStarted
        g_postProcessing.disable()
        return

    def handleKeyEvent(self, isDown, key, mods, event=None):
        assert self._isEnabled
        cmdMap = CommandMapping.g_instance
        if self._cam.handleKeyEvent(isDown, key, mods, event):
            return True
        elif BigWorld.isKeyDown(Keys.KEY_CAPSLOCK) and constants.IS_DEVELOPMENT and isDown and key == Keys.KEY_F1:
            self._aih.onControlModeChanged('debug', prevModeName='arcade', camMatrix=self._cam.camera.matrix)
            return True
        elif BigWorld.isKeyDown(Keys.KEY_CAPSLOCK) and constants.IS_DEVELOPMENT and isDown and key == Keys.KEY_F2:
            self._aih.onControlModeChanged('cat', camMatrix=self._cam.camera.matrix)
            return True
        elif BigWorld.isKeyDown(Keys.KEY_CAPSLOCK) and isDown and key == Keys.KEY_F3 and self.__videoControlModeAvailable:
            self._aih.onControlModeChanged('video', prevModeName='arcade', camMatrix=self._cam.camera.matrix)
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
        GUI.mcursor().position = self._aim.offset()
        self._cam.update(dx, dy, mathUtils.clamp(-1, 1, dz))
        self.__mouseVehicleRotator.handleMouse(dx)
        return True

    def onMinimapClicked(self, worldPos):
        if self._aih.isSPG:
            self.__activateAlternateMode(worldPos)

    def onChangeControlModeByScroll(self):
        self.__activateAlternateMode(pos=None, bByScroll=True)
        return

    def __onArenaStarted(self, period, *args):
        self.__isArenaStarted = True if period == constants.ARENA_PERIOD.BATTLE else False

    def setGUIVisible(self, isVisible):
        self._aim.setVisible(isVisible)
        self._gunMarker.setGUIVisible(isVisible, valueUpdate=not self.__isArenaStarted)

    def __activateAlternateMode(self, pos=None, bByScroll=False):
        ownVehicle = BigWorld.entity(BigWorld.player().playerVehicleID)
        if ownVehicle is not None and ownVehicle.isStarted and ownVehicle.appearance.isUnderwater or BigWorld.player().isGunLocked:
            return
        elif self._aih.isSPG and not bByScroll:
            self._cam.update(0, 0, 0, False, False)
            equipmentID = None
            if BattleReplay.isPlaying():
                mode = BattleReplay.g_replayCtrl.getControlMode()
                pos = BattleReplay.g_replayCtrl.getGunMarkerPos()
                equipmentID = BattleReplay.g_replayCtrl.getEquipmentId()
            else:
                mode = 'strategic'
                if pos is None:
                    pos = self.camera.aimingSystem.getDesiredShotPoint()
                    if pos is None:
                        pos = Math.Matrix(self._gunMarker.matrixProvider()).applyToOrigin()
            self._aih.onControlModeChanged(mode, preferredPos=pos, aimingMode=self._aimingMode, saveDist=True, equipmentID=equipmentID)
            return
        elif not self._aih.isSPG:
            self._cam.update(0, 0, 0, False, False)
            if BattleReplay.isPlaying() and BigWorld.player().isGunLocked:
                mode = BattleReplay.g_replayCtrl.getControlMode()
                desiredShotPoint = BattleReplay.g_replayCtrl.getGunMarkerPos()
                equipmentID = BattleReplay.g_replayCtrl.getEquipmentId()
            else:
                mode = 'sniper'
                equipmentID = None
                desiredShotPoint = self.camera.aimingSystem.getDesiredShotPoint()
            self._aih.onControlModeChanged(mode, preferredPos=desiredShotPoint, aimingMode=self._aimingMode, saveZoom=not bByScroll, equipmentID=equipmentID)
            return
        else:
            return


class StrategicControlMode(_GunControlMode):

    def __init__(self, dataSection, avatarInputHandler):
        super(StrategicControlMode, self).__init__(avatarInputHandler, mode='strategic', isStrategic=True)
        self.__trajectoryDrawer = BigWorld.wg_trajectory_drawer()
        self._aim = aims.createAim(dataSection.readString('aim'))
        self._cam = StrategicCamera.StrategicCamera(dataSection['camera'], self._aim)
        self.__trajectoryDrawerClbk = None
        self.__updateInterval = 0.1
        return

    def create(self):
        self._cam.create(None)
        super(StrategicControlMode, self).create()
        self.__initTrajectoryDrawer()
        return

    def destroy(self):
        self.disable()
        self.__delTrajectoryDrawer()
        self._cam.writeUserPreferences()
        super(StrategicControlMode, self).destroy()

    def enable(self, **args):
        super(StrategicControlMode, self).enable(**args)
        SoundGroups.g_instance.changePlayMode(2)
        self._cam.enable(args['preferredPos'], args['saveDist'])
        self.__trajectoryDrawer.visible = BigWorld.player().isGuiVisible
        BigWorld.player().autoAim(None)
        self.__updateTrajectoryDrawer()
        g_postProcessing.enable('strategic')
        BigWorld.setFloraEnabled(False)
        return

    def disable(self):
        super(StrategicControlMode, self).disable()
        self.__trajectoryDrawer.visible = False
        if self.__trajectoryDrawerClbk is not None:
            BigWorld.cancelCallback(self.__trajectoryDrawerClbk)
            self.__trajectoryDrawerClbk = None
        g_postProcessing.disable()
        BigWorld.setFloraEnabled(True)
        return

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
            pos = self._cam.aimingSystem.getDesiredShotPoint()
            if pos is None:
                pos = Math.Matrix(self._gunMarker.matrixProvider()).applyToOrigin()
            self._aih.onControlModeChanged('arcade', preferredPos=pos, aimingMode=self._aimingMode, closesDist=False)
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
        elif cmdMap.isFired(CommandMapping.CMD_CM_CAMERA_RESTORE_DEFAULT, key) and isDown:
            self._cam.update(0, 0, 0, False)
            self._cam.restoreDefaultsState()
            return True
        else:
            return False

    def handleMouseEvent(self, dx, dy, dz):
        assert self._isEnabled
        GUI.mcursor().position = self._aim.offset()
        self._cam.update(dx, dy, dz)
        return True

    def onMinimapClicked(self, worldPos):
        self._cam.teleport(worldPos)

    def resetGunMarkers(self):
        self._gunMarker.reset()

    def setGUIVisible(self, isVisible):
        self._aim.setVisible(isVisible)
        self._gunMarker.setGUIVisible(isVisible)
        self.__trajectoryDrawer.visible = isVisible

    def isManualBind(self):
        return True

    def __updateTrajectoryDrawer(self):
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying:
            self.__trajectoryDrawerClbk = BigWorld.callback(0.0, self.__updateTrajectoryDrawer)
        else:
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
        shotDescr = BigWorld.player().vehicleTypeDescriptor.shot
        self.__trajectoryDrawer.setParams(shotDescr['maxDistance'], Math.Vector3(0, -shotDescr['gravity'], 0), self._aim.offset())

    def __initTrajectoryDrawer(self):
        BigWorld.player().onGunShotChanged += self.__onGunShotChanged
        self.__trajectoryDrawer.setColors(Math.Vector4(0, 255, 0, 255), Math.Vector4(255, 0, 0, 255), Math.Vector4(128, 128, 128, 255))
        self.__trajectoryDrawer.setGetDynamicCollidersCallback(lambda start, end: [ e.collideSegment for e in getCollidableEntities((BigWorld.player().playerVehicleID,), start, end) ])
        self.__onGunShotChanged()

    def __delTrajectoryDrawer(self):
        BigWorld.player().onGunShotChanged -= self.__onGunShotChanged
        self.__trajectoryDrawer = None
        return


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
        super(SniperControlMode, self).__init__(avatarInputHandler, 'sniper')
        self._aim = aims.createAim(dataSection.readString('aim'))
        self.__binoculars = BigWorld.wg_binoculars()
        self._cam = SniperCamera.SniperCamera(dataSection['camera'], self._aim, self.__binoculars)
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
        BigWorld.wg_enableTreeHiding(True)
        BigWorld.wg_setTreeHidingRadius(15.0, 10.0)
        TriggersManager.g_manager.activateTrigger(TRIGGER_TYPE.SNIPER_MODE)
        g_postProcessing.enable('sniper')
        desc = BigWorld.player().vehicleTypeDescriptor
        isHorizontalStabilizerAllowed = desc.gun['turretYawLimits'] is None
        self._cam.aimingSystem.enableHorizontalStabilizerRuntime(isHorizontalStabilizerAllowed)
        return

    def disable(self, isDestroy=False):
        super(SniperControlMode, self).disable()
        self.__binoculars.enabled = False
        BigWorld.wg_enableTreeHiding(False)
        g_postProcessing.disable()
        if TriggersManager.g_manager is not None:
            TriggersManager.g_manager.deactivateTrigger(TRIGGER_TYPE.SNIPER_MODE)
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
            self._aih.onControlModeChanged('arcade', preferredPos=self.camera.aimingSystem.getDesiredShotPoint(), turretYaw=self._cam.aimingSystem.turretYaw, gunPitch=self._cam.aimingSystem.gunPitch, aimingMode=self._aimingMode, closesDist=False)
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
        GUI.mcursor().position = self._aim.offset()
        self._cam.update(dx, dy, dz)
        return True

    def onRecreateDevice(self):
        super(SniperControlMode, self).onRecreateDevice()
        self._cam.onRecreateDevice()

    def setGUIVisible(self, isVisible):
        self._aim.setVisible(isVisible)
        self._gunMarker.setGUIVisible(isVisible)

    def getPreferredAutorotationMode(self):
        vehicle = BigWorld.entities.get(BigWorld.player().playerVehicleID)
        if vehicle is None:
            return
        else:
            desc = vehicle.typeDescriptor
            isRotationAroundCenter = desc.chassis['rotationIsAroundCenter']
            turretHasYawLimits = desc.gun['turretYawLimits'] is not None
            return isRotationAroundCenter and not turretHasYawLimits

    def enableSwitchAutorotationMode(self):
        return self.getPreferredAutorotationMode() is not False

    def onChangeControlModeByScroll(self, switchToClosestDist=True):
        assert self._isEnabled
        self._aih.onControlModeChanged('arcade', preferredPos=self.camera.aimingSystem.getDesiredShotPoint(), turretYaw=self._cam.aimingSystem.turretYaw, gunPitch=self._cam.aimingSystem.gunPitch, aimingMode=self._aimingMode, closesDist=switchToClosestDist)

    def recreateCamera(self):
        preferredPos = self.camera.aimingSystem.getDesiredShotPoint()
        self._cam.disable()
        self._cam.enable(preferredPos, True)

    def __setupBinoculars(self, isCoatedOptics):
        modeDesc = self.__binocularsModes[SniperControlMode._BINOCULARS_MODE_SUFFIX[1 if isCoatedOptics else 0]]
        self.__binoculars.setBackgroundTexture(modeDesc.background)
        self.__binoculars.setDistortionTexture(modeDesc.distortion)
        self.__binoculars.setColorGradingTexture(modeDesc.rgbCube)
        self.__binoculars.setParams(modeDesc.greenOffset, modeDesc.blueOffset, modeDesc.aberrationRadius, modeDesc.distortionAmount)


class PostMortemControlMode(IControlMode):
    _POSTMORTEM_DELAY_ENABLED = True
    camera = property(lambda self: self.__cam)

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
        self.__aim = aims.createAim('postmortem')
        self.__cam = ArcadeCamera.ArcadeCamera(dataSection['camera'], self.__aim)
        self.__curVehicleID = None
        self.__selfVehicleID = None
        self.__isEnabled = False
        self.__postmortemDelay = None
        self.__isObserverMode = False
        self.__videoControlModeAvailable = dataSection.readBool('videoModeAvailable', constants.IS_DEVELOPMENT)
        return

    def prerequisites(self):
        return self.__aim.prerequisites()

    def create(self):
        self.__aim.create()
        self.__cam.create(_ARCADE_CAM_PIVOT_POS, None, True)
        return

    def destroy(self):
        self.disable()
        self.__aim.destroy()
        self.__cam.destroy()
        self.__cam = None
        return

    def dumpState(self):
        return dumpStateEmpty()

    def enable(self, **args):
        SoundGroups.g_instance.changePlayMode(0)
        player = BigWorld.player()
        if player:
            self.__selfVehicleID = player.playerVehicleID
            self.__isObserverMode = 'observer' in player.vehicleTypeDescriptor.type.tags
        self.__cam.enable(None, False, args.get('postmortemParams'))
        self.__cam.vehicleMProv = BigWorld.player().consistentMatrices.attachedVehicleMatrix
        self.__aim.enable()
        self.__connectToArena()
        _setCameraFluency(self.__cam.camera, self.__CAM_FLUENCY)
        self.__isEnabled = True
        BigWorld.player().consistentMatrices.onVehicleMatrixBindingChanged += self.__onMatrixBound
        if not BattleReplay.g_replayCtrl.isPlaying:
            if self.__isObserverMode:
                vehicleID = args.get('vehicleID')
                if vehicleID is None:
                    self.__switchViewpoint(False)
                else:
                    self.__fakeSwitchToVehicle(vehicleID)
                return
            if PostMortemControlMode.getIsPostmortemDelayEnabled() and bool(args.get('bPostmortemDelay')):
                self.__postmortemDelay = PostmortemDelay(self.__cam, self.__onPostmortemDelayStop)
                self.__postmortemDelay.start()
            else:
                self.__switchToVehicle(None)
        g_postProcessing.enable('postmortem')
        return

    def disable(self):
        BigWorld.player().consistentMatrices.onVehicleMatrixBindingChanged -= self.__onMatrixBound
        self.__destroyPostmortemDelay()
        self.__isEnabled = False
        self.__aim.disable()
        self.__disconnectFromArena()
        self.__cam.disable()
        self.__curVehicleID = None
        self.__selfVehicleID = None
        g_postProcessing.disable()
        return

    def handleKeyEvent(self, isDown, key, mods, event=None):
        assert self.__isEnabled
        cmdMap = CommandMapping.g_instance
        if BigWorld.isKeyDown(Keys.KEY_CAPSLOCK) and constants.IS_DEVELOPMENT and isDown and key == Keys.KEY_F1:
            self.__aih.onControlModeChanged('debug', prevModeName='postmortem', camMatrix=self.__cam.camera.matrix)
            return True
        if BigWorld.isKeyDown(Keys.KEY_CAPSLOCK) and isDown and key == Keys.KEY_F3 and (self.__videoControlModeAvailable or g_sessionProvider.getCtx().isPlayerObserver()):
            self.__aih.onControlModeChanged('video', prevModeName='postmortem', camMatrix=self.__cam.camera.matrix, curVehicleID=self.__curVehicleID)
            return True
        if cmdMap.isFired(CommandMapping.CMD_CM_POSTMORTEM_NEXT_VEHICLE, key) and isDown:
            self.__switchViewpoint(True)
            return True
        if cmdMap.isFired(CommandMapping.CMD_CM_POSTMORTEM_SELF_VEHICLE, key) and isDown:
            self.__switchViewpoint(False)
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
        GUI.mcursor().position = self.__aim.offset()
        if self.__postmortemDelay is not None:
            return True
        else:
            self.__cam.update(dx, dy, _clamp(-1, 1, dz))
            return True

    def onRecreateDevice(self):
        self.__aim.onRecreateDevice()

    def selectPlayer(self, vehId):
        self.__switchToVehicle(vehId)

    def getAim(self):
        return self.__aim

    def setGUIVisible(self, isVisible):
        self.__aim.setVisible(isVisible)

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

    def __switchViewpoint(self, toPrevious, vehicleID=None):
        assert isinstance(toPrevious, bool)
        if self.__postmortemDelay is not None:
            return
        else:
            self.__doPreBind()
            if vehicleID is None:
                BigWorld.player().positionControl.switchViewpoint(toPrevious)
            else:
                self.onSwitchViewpoint(vehicleID, Math.Vector3(0.0, 0.0, 0.0))
            return

    def __switchToVehicle(self, toId=None):
        if self.__postmortemDelay is not None:
            return
        else:
            assert not toId or isinstance(toId, int) and toId >= 0
            self.__doPreBind()
            self.__aih.onPostmortemVehicleChanged(toId)
            BigWorld.player().positionControl.bindToVehicle(vehicleID=toId)
            return

    def __doPreBind(self):
        if self.__curVehicleID is not None:
            prevVehicleAppearance = getattr(BigWorld.entity(self.__curVehicleID), 'appearance', None)
            if prevVehicleAppearance is not None:
                self.__cam.removeVehicleToCollideWith(prevVehicleAppearance)
            else:
                LOG_DEBUG('Cannot find current vehicle with id %s, erasing all collision models instead!' % self.__curVehicleID)
                self.__cam.clearVehicleToCollideWith()
        return

    def onSwitchViewpoint(self, vehicleID, cameraPos):
        player = BigWorld.player()
        replayCtrl = BattleReplay.g_replayCtrl
        self.__curVehicleID = vehicleID if vehicleID != -1 else self.__selfVehicleID
        self.__aim.changeVehicle(self.__curVehicleID)
        self.__aih.onPostmortemVehicleChanged(self.__curVehicleID)
        if self.__curVehicleID in BigWorld.entities.keys():
            self.__aih.onCameraChanged('postmortem', self.__curVehicleID)
        if self.__curVehicleID != player.playerVehicleID and self.__curVehicleID is not None and BigWorld.entity(self.__curVehicleID) is None and not replayCtrl.isPlaying and not self.__isObserverMode and player.arena.positions.get(self.__curVehicleID) is None:
            self.__switchViewpoint(False)
        return

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
            if vehicle is None or self.__curVehicleID != vehicle.id:
                return
            self.__cam.addVehicleToCollideWith(vehicle.appearance)
            replayCtrl = BattleReplay.g_replayCtrl
            if replayCtrl.isRecording:
                replayCtrl.setPlayerVehicleID(self.__curVehicleID)
            self.__cam.vehicleMProv = BigWorld.player().consistentMatrices.attachedVehicleMatrix
            self.__aih.onCameraChanged('postmortem', self.__curVehicleID)
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
        gunRotator = BigWorld.player().gunRotator
        shotDesc = BigWorld.player().vehicleTypeDescriptor.shot
        gunMat = AimingSystems.getPlayerGunMat(gunRotator.turretYaw, gunRotator.gunPitch)
        position = gunMat.translation
        velocity = gunMat.applyVector(Math.Vector3(0, 0, shotDesc['speed']))
        return (position, velocity, Math.Vector3(0, -shotDesc['gravity'], 0))

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


class _SuperGunMarker():
    GUN_MARKER_CLIENT = 1
    GUN_MARKER_SERVER = 2

    def __init__(self, mode='arcade', isStrategic=False):
        self.__show2 = useServerAim()
        self.__show1 = constants.IS_DEVELOPMENT or not self.__show2
        self.__isGuiVisible = True
        self.__isStrategic = isStrategic
        replayCtrl = BattleReplay.g_replayCtrl
        replayCtrl.setUseServerAim(self.__show2)
        if isStrategic:
            self.__gm1 = _SPGFlashGunMarker(_PlayerGunInformation.getCurrentShotInfo, _PlayerGunInformation.updateMarkerDispersion, self.GUN_MARKER_CLIENT)
        else:
            self.__gm1 = _FlashGunMarker(self.GUN_MARKER_CLIENT, mode)
        if isStrategic:
            self.__gm2 = _SPGFlashGunMarker(_PlayerGunInformation.getCurrentShotInfo, _PlayerGunInformation.updateServerMarkerDispersion, self.GUN_MARKER_SERVER, True, True)
        else:
            self.__gm2 = _FlashGunMarker(self.GUN_MARKER_SERVER, mode, True)

    def prerequisites(self):
        return self.__gm1.prerequisites() + self.__gm2.prerequisites()

    def create(self):
        self.__gm1.create()
        self.__gm2.create()

    def destroy(self):
        self.__gm1.destroy()
        self.__gm2.destroy()

    def enable(self, state):
        if state is not None:
            self.__show1 = state.get('show1', False)
            self.__show2 = state.get('show2', False)
        self.__gm1.enable(state)
        self.__gm2.enable(state)
        if state:
            self.__gm2.setPosition(state['pos2'])
        self.show(self.__show1)
        self.show2(self.__show2)
        self.onRecreateDevice()
        return

    def disable(self):
        self.__gm1.disable()
        self.__gm2.disable()

    def dumpState(self):
        out = self.__gm1.dumpState()
        out['pos2'] = self.__gm2.getPosition()
        out['show1'] = self.__show1
        out['show2'] = self.__show2
        return out

    def matrixProvider(self):
        return self.__gm1.matrixProvider

    def setReloading(self, duration, startTime=None, baseTime=None):
        self.__gm1.setReloading(duration, startTime)
        self.__gm2.setReloading(duration, startTime)

    def setReloadingInPercent(self, percent):
        self.__gm1.setReloadingInPercent(percent)
        self.__gm2.setReloadingInPercent(percent)

    def show(self, flag):
        self.__show1 = flag
        self.__gm1.show(flag and self.__isGuiVisible)

    def show2(self, flag):
        if BattleReplay.isPlaying():
            return
        show2Prev = self.__show2
        self.__show2 = flag and self.__isGuiVisible
        if self.__show2 and show2Prev != self.__show2:
            self.__gm2.setPosition(self.__gm1.getPosition())
        self.__gm2.show(self.__show2)
        replayCtrl = BattleReplay.g_replayCtrl
        replayCtrl.setUseServerAim(self.__show2)
        if not constants.IS_DEVELOPMENT:
            self.show(not flag)

    def setGUIVisible(self, isVisible, valueUpdate=False):
        self.__isGuiVisible = isVisible
        if not valueUpdate:
            serverAim = useServerAim()
            self.show(constants.IS_DEVELOPMENT or not serverAim)
            self.show2(serverAim)

    def update(self, pos, dir, size, relaxTime, collData):
        self.__gm1.update(pos, dir, size, relaxTime, collData)

    def update2(self, pos, dir, size, relaxTime, collData):
        self.__gm2.update(pos, dir, size, relaxTime, collData)

    def reset(self):
        if self.__isStrategic is True:
            self.__gm1.reset()
            self.__gm2.reset()

    def onRecreateDevice(self):
        self.__gm1.onRecreateDevice()
        self.__gm2.onRecreateDevice()

    def setPosition(self, pos):
        self.__gm1.setPosition(pos)

    def setPosition2(self, pos):
        self.__gm2.setPosition(pos)

    def getPosition(self):
        return self.__gm1.getPosition()

    def getPosition2(self):
        return self.__gm2.getPosition()


class _SPGFlashGunMarker(Flash):
    _FLASH_CLASS = 'WGSPGCrosshairFlash'
    _SWF_FILE_NAME = 'crosshair_strategic.swf'
    _SWF_SIZE = (620, 620)

    def __init__(self, gunInfoFunc, dispersionUpdateFunc, key, isDebug=False, enableSmoothFiltering=False):
        Flash.__init__(self, self._SWF_FILE_NAME, self._FLASH_CLASS)
        self.__curShotInfoFunc = gunInfoFunc
        self.__dispersionUpdateFunc = dispersionUpdateFunc
        self.key = key
        self.component.wg_enableSmoothFiltering = enableSmoothFiltering
        self.component.wg_inputKeyMode = 2
        self.component.position.z = DEPTH_OF_GunMarker
        self.component.focus = False
        self.component.moveFocus = False
        self.component.heightMode = 'PIXEL'
        self.component.widthMode = 'PIXEL'
        self.movie.backgroundAlpha = 0
        self.flashSize = self._SWF_SIZE
        self.__animMat = None
        self.__applyFilter = isDebug
        self.__oldSize = 0.0
        if isDebug:
            self.call('Crosshair.setAsDebug', [isDebug])
        return

    def prerequisites(self):
        return []

    def dumpState(self):
        return {'reload': dict(self.__reload),
         'pos1': self.getPosition(),
         'size': 0.0}

    def create(self):
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        self.component.wg_maxTime = 5.0
        self.component.wg_serverTickLength = 0.1
        self.component.wg_sizeScaleRate = 10.0
        self.component.wg_sizeConstraints = Math.Vector2(50.0, 100.0)
        self.component.wg_usePyCollDetect = False
        self.component.wg_setRelaxTime(0.1)
        self.component.wg_setPointsBaseScale(g_settingsCore.interfaceScale.get())
        g_settingsCore.interfaceScale.onScaleChanged += self.onScaleChanged
        self.active(True)
        self.__reload = {'start_time': 0.0,
         'duration': 0.0,
         'isReloading': False}
        self.onRecreateDevice()
        if self.__applyFilter and constants.IS_DEVELOPMENT and useServerAim():
            self.call('Crosshair.setFilter')

    def destroy(self):
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        self.active(False)
        self.__curShotInfoFunc = None
        g_settingsCore.interfaceScale.onScaleChanged -= self.onScaleChanged
        return

    def enable(self, state):
        if state is not None:
            ammoCtrl = g_sessionProvider.getAmmoCtrl()
            if ammoCtrl.isGunReloadTimeInPercent():
                self.setReloadingInPercent(ammoCtrl.getGunReloadTime())
            else:
                rs = state['reload']
                self.setReloading(rs['duration'], rs['startTime'], rs['isReloading'], correction=rs.get('correction'))
            self.setPosition(state['pos1'])
        return

    def disable(self):
        self.show(False)

    def matrixProvider(self):
        return self.__animMat

    def show(self, flag):
        self.component.visible = flag

    def setReloading(self, duration, startTime=None, isReloading=True, correction=None):
        rs = self.__reload
        rs['isReloading'] = isReloading
        rs['startTime'] = BigWorld.time() if startTime is None else startTime
        rs['duration'] = duration
        rs['correction'] = correction
        startTime = 0.0 if startTime is None else BigWorld.time() - startTime
        self.call('Crosshair.setReloading', [duration, startTime, isReloading])
        return

    def setReloadingInPercent(self, percent):
        self.call('Crosshair.setReloadingAsPercent', [percent])

    def update(self, pos, dir, size, relaxTime, collData):
        if not self.component.visible:
            return
        m = Math.Matrix()
        m.setTranslate(pos)
        self.__setupMatrixAnimation()
        self.__animMat.keyframes = ((0.0, Math.Matrix(self.__animMat)), (relaxTime, m))
        self.__animMat.time = 0.0
        self.__oldSize = size[0]
        self.__spgUpdate(self.__oldSize)

    def reset(self):
        self.component.wg_reset()
        self.__spgUpdate(self.__oldSize)

    def onRecreateDevice(self):
        self.component.size = GUI.screenResolution()

    def onScaleChanged(self, scale):
        self.component.wg_setPointsBaseScale(scale)

    def setPosition(self, pos):
        m = Math.Matrix()
        m.setTranslate(pos)
        self.__setupMatrixAnimation()
        self.__animMat.keyframes = ((0.0, m), (0.0, m))
        self.__animMat.time = 0.0

    def getPosition(self):
        return Math.Vector3(0.0, 0.0, 0.0) if self.__animMat is None else Math.Matrix(self.__animMat).translation

    def __setupMatrixAnimation(self):
        if self.__animMat is not None:
            return
        else:
            self.__animMat = Math.MatrixAnimation()
            return

    def __spgUpdate(self, size):
        try:
            pos3d, vel3d, gravity3d = self.__curShotInfoFunc()
            self.__dispersionUpdateFunc(self.component)
            self.component.wg_update(pos3d, vel3d, gravity3d, size)
        except:
            LOG_CURRENT_EXCEPTION()

    def outsideConstraint(self, idealAngle):
        pass


class SizeFilter(object):

    @property
    def size(self):
        return self.__outSize

    def __init__(self):
        self.__outSize = 0.0
        self.__inSize = 0.0
        self.__k = 0.0
        self.__minLimit = 0.0

    def init(self, startSize, minLimit):
        self.__outSize = self.__inSize = startSize
        self.__minLimit = minLimit

    def update(self, inSize, ideal):
        if inSize >= self.__inSize or self.__minLimit <= ideal:
            self.__outSize = self.__inSize = inSize
            self.__k = 0.0
            return
        if self.__k == 0.0 and inSize != ideal:
            self.__k = (inSize - self.__minLimit) / (inSize - ideal)
        self.__inSize = inSize
        self.__outSize = self.__minLimit + self.__k * (self.__inSize - ideal)


class _FlashGunMarker(Flash):
    _FLASH_CLASS = 'WGCrosshairFlash'
    _SWF_FILE_NAME = 'crosshair_sniper.swf'
    _SWF_SIZE = (620, 620)
    _colorsByPiercing = {'default': {'not_pierced': 'red',
                 'little_pierced': 'orange',
                 'great_pierced': 'green'},
     'color_blind': {'not_pierced': 'purple',
                     'little_pierced': 'yellow',
                     'great_pierced': 'green'}}

    def __init__(self, key, mode, applyFilter=False):
        Flash.__init__(self, self._SWF_FILE_NAME, self._FLASH_CLASS)
        self.component.wg_inputKeyMode = 2
        self.component.position.z = DEPTH_OF_GunMarker
        self.component.focus = False
        self.component.moveFocus = False
        self.component.heightMode = 'PIXEL'
        self.component.widthMode = 'PIXEL'
        self.movie.backgroundAlpha = 0
        self.flashSize = self._SWF_SIZE
        self.mode = mode
        self.key = key
        self.__replSwitchTime = 0.0
        self.__sizeFilter = SizeFilter()
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        self.settingsCore = weakref.proxy(g_settingsCore)
        from account_helpers.settings_core.SettingsCache import g_settingsCache
        self.settingsCache = weakref.proxy(g_settingsCache)
        self.settingsCache.onSyncCompleted += self.onSettingsSynced
        self.__curSize = 0.0
        self.__animMat = None
        self.__applyFilter = applyFilter
        self.__scaleNeedToUpdate = True
        self.__isVisible = False
        self._aim = None
        self.updateAim()
        return

    def prerequisites(self):
        return []

    def dumpState(self):
        return {'reload': dict(self.__reload),
         'pos1': self.getPosition(),
         'size': self.__curSize}

    def create(self):
        type = 'color_blind' if self.settingsCore.getSetting('isColorBlind') else 'default'
        self._curColors = self._colorsByPiercing[type]
        self.settingsCore.onSettingsChanged += self.applySettings
        self.settingsCore.interfaceScale.onScaleChanged += self.onScaleChanged
        self.component.wg_sizeConstraint = (10.0, 300.0)
        self.component.wg_setStartSize(10.0)
        self.__sizeFilter.init(10.0, 10.0)
        self.active(True)
        self.__reload = {'start_time': 0.0,
         'duration': 0.0,
         'isReloading': False}
        self.onRecreateDevice()
        self.onScaleChanged()

    def updateAim(self):
        self._aim = {'arcade': self.settingsCore.getSetting('arcade'),
         'sniper': self.settingsCore.getSetting('sniper')}

    def onSettingsSynced(self):
        self.updateAim()
        self.settingsCache.onSyncCompleted -= self.onSettingsSynced

    def applySettings(self, diff):
        if type(diff) is dict:
            self._aim['arcade'] = diff.get('arcade', self._aim['arcade'])
            self._aim['sniper'] = diff.get('sniper', self._aim['sniper'])
        if self.mode in diff:
            for mode in ('arcade', 'sniper'):
                if mode in diff:
                    settings = self._aim[mode]
                    current = settings['gunTag']
                    currentType = settings['gunTagType']
                    self.__scaleNeedToUpdate = True
                    self.call('Crosshair.setGunTag', [current, currentType, self.settingsCore.interfaceScale.get()])
                    current = settings['mixing']
                    currentType = settings['mixingType']
                    self.call('Crosshair.setMixing', [current, currentType])
                    if self.__applyFilter and constants.IS_DEVELOPMENT and useServerAim():
                        self.call('Crosshair.setFilter')

        if 'isColorBlind' in diff:
            mode = 'color_blind' if diff['isColorBlind'] else 'default'
            self._curColors = self._colorsByPiercing[mode]

    def destroy(self):
        self.settingsCore.onSettingsChanged -= self.applySettings
        self.settingsCore.interfaceScale.onScaleChanged -= self.onScaleChanged
        self.close()
        self.__animMat = None
        return

    def enable(self, state):
        self.applySettings(self.mode)
        if state is not None:
            ammoCtrl = g_sessionProvider.getAmmoCtrl()
            if ammoCtrl.isGunReloadTimeInPercent():
                self.setReloadingInPercent(ammoCtrl.getGunReloadTime(), False)
            else:
                rs = state['reload']
                self.setReloading(rs['duration'], rs['startTime'], rs['isReloading'], correction=rs.get('correction'), switched=True)
            self.setPosition(state['pos1'])
            self.component.wg_updateSize(state['size'], 0.0)
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying and replayCtrl.isClientReady:
            self.__replSwitchTime = 0.2
        return

    def disable(self):
        self.show(False)

    def matrixProvider(self):
        return self.__animMat

    def show(self, flag):
        self.__isVisible = flag
        if not flag:
            self.component.visible = flag

    def setReloading(self, duration, startTime=None, isReloading=True, correction=None, switched=False):
        rs = self.__reload
        _isReloading = rs.get('isReloading', False)
        _startTime = rs.get('startTime', 0.0)
        _duration = rs.get('duration', 0.0)
        isReloading = duration > 0.0
        rs['isReloading'] = isReloading
        rs['correction'] = None
        if not switched and _isReloading and duration > 0 and _duration > 0:
            current = BigWorld.time()
            rs['correction'] = {'timeRemaining': duration,
             'startTime': current,
             'startPosition': (current - _startTime) / _duration}
            self.call('Crosshair.correctReloadingTime', [duration])
        else:
            rs['startTime'] = BigWorld.time() if startTime is None else startTime
            rs['duration'] = duration
            if correction is not None:
                params = self._getCorrectionReloadingParams(correction)
                if params is not None:
                    rs['correction'] = correction
                    self.call('Crosshair.setReloading', params)
            else:
                startTime = 0.0 if startTime is None else BigWorld.time() - startTime
                self.call('Crosshair.setReloading', [duration, startTime, isReloading])
        return

    def setReloadingInPercent(self, percent, isReloading=True):
        self.call('Crosshair.setReloadingAsPercent', [percent, isReloading])

    def update(self, pos, dir, sizeVector, relaxTime, collData):
        if not self.__isVisible:
            return
        else:
            m = Math.Matrix()
            m.setTranslate(pos)
            self.__setupMatrixAnimation()
            self.__animMat.keyframes = ((0.0, Math.Matrix(self.__animMat)), (relaxTime, m))
            self.__animMat.time = 0.0
            size = sizeVector[0]
            idealSize = sizeVector[1]
            replayCtrl = BattleReplay.g_replayCtrl
            if replayCtrl.isPlaying and replayCtrl.isClientReady:
                s = replayCtrl.getArcadeGunMarkerSize()
                if s != -1.0:
                    size = s
            elif replayCtrl.isRecording:
                if replayCtrl.isServerAim and self.key == _SuperGunMarker.GUN_MARKER_SERVER:
                    replayCtrl.setArcadeGunMarkerSize(size)
                elif self.key == _SuperGunMarker.GUN_MARKER_CLIENT:
                    replayCtrl.setArcadeGunMarkerSize(size)
            aspectRatio = GUI.screenResolution()[0] * 0.5
            currentSize = _calcScale(m, size) * aspectRatio
            idealSize = _calcScale(m, idealSize) * aspectRatio
            self.__sizeFilter.update(currentSize, idealSize)
            self.__curSize = self.__sizeFilter.size
            if collData is None or collData[0].health <= 0 or collData[0].publicInfo['team'] == BigWorld.player().team:
                self.call('Crosshair.setMarkerType', ['normal'])
            else:
                self._changeColor(pos, collData[2])
            if self.__replSwitchTime > 0.0:
                self.__replSwitchTime -= relaxTime
                self.component.wg_updateSize(self.__curSize, 0.0)
            else:
                self.component.wg_updateSize(self.__curSize, relaxTime)
            if self.__scaleNeedToUpdate:
                self.call('Crosshair.setScale', [self.settingsCore.interfaceScale.get()])
                self.__scaleNeedToUpdate = False
            if self.__isVisible and not self.component.visible:
                self.component.visible = True
            return

    def onRecreateDevice(self):
        self.component.size = GUI.screenResolution()

    def onScaleChanged(self, scale=None):
        self.__scaleNeedToUpdate = True

    def setPosition(self, pos):
        m = Math.Matrix()
        m.setTranslate(pos)
        self.__setupMatrixAnimation()
        self.__animMat.keyframes = ((0.0, m), (0.0, m))
        self.__animMat.time = 0.0

    def getPosition(self):
        return Math.Vector3(0.0, 0.0, 0.0) if self.__animMat is None else Math.Matrix(self.__animMat).translation

    def __setupMatrixAnimation(self):
        if self.__animMat is not None:
            return
        else:
            self.__animMat = Math.MatrixAnimation()
            self.component.wg_positionMatProv = self.__animMat
            return

    def _changeColor(self, hitPoint, armor):
        vDesc = BigWorld.player().vehicleTypeDescriptor
        ppDesc = vDesc.shot['piercingPower']
        maxDist = vDesc.shot['maxDistance']
        dist = (hitPoint - BigWorld.player().getOwnVehiclePosition()).length
        if dist <= 100.0:
            piercingPower = ppDesc[0]
        elif maxDist > dist:
            p100, p500 = ppDesc
            piercingPower = p100 + (p500 - p100) * (dist - 100.0) / 400.0
            if piercingPower < 0.0:
                piercingPower = 0.0
        else:
            piercingPower = 0.0
        piercingPercent = 1000.0
        if piercingPower > 0.0:
            piercingPercent = 100.0 + (armor - piercingPower) / piercingPower * 100.0
        type = 'great_pierced'
        if piercingPercent >= 150:
            type = 'not_pierced'
        elif 90 < piercingPercent < 150:
            type = 'little_pierced'
        self.call('Crosshair.setMarkerType', [self._curColors[type]])

    def _getCorrectionReloadingParams(self, correction):
        cTimeRemaining = correction.get('timeRemaining', 0)
        cStartTime = correction.get('startTime', 0)
        cStartPosition = correction.get('startPosition', 0)
        if not cTimeRemaining > 0:
            LOG_WARNING('timeRemaining - invalid value ', cTimeRemaining)
            return None
        else:
            delta = BigWorld.time() - cStartTime
            currentPosition = cStartPosition + delta / cTimeRemaining * (1 - cStartPosition)
            return [cTimeRemaining - delta,
             cStartTime,
             True,
             currentPosition * 100.0]


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
            self.__rotationState = _clamp(-1, 1, dx)
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


def useServerAim():
    replayCtrl = BattleReplay.g_replayCtrl
    if replayCtrl.isPlaying:
        return False
    from account_helpers.settings_core.SettingsCore import g_settingsCore
    return g_settingsCore.getSetting('useServerAim')


def dumpStateEmpty():
    return {'gunMarkerPosition': None,
     'gunMarkerPosition2': None,
     'aimState': None}


def _clamp(minVal, maxVal, val):
    tmpVal = val
    tmpVal = max(minVal, val)
    tmpVal = min(maxVal, tmpVal)
    return tmpVal


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


def _calcScale(worldMat, size):
    sr = GUI.screenResolution()
    aspect = sr[0] / sr[1]
    proj = BigWorld.projection()
    wtcMat = Math.Matrix()
    wtcMat.perspectiveProjection(proj.fov, aspect, proj.nearPlane, proj.farPlane)
    wtcMat.preMultiply(BigWorld.camera().matrix)
    wtcMat.preMultiply(worldMat)
    pointMat = Math.Matrix()
    pointMat.set(BigWorld.camera().matrix)
    transl = Math.Matrix()
    transl.setTranslate(Math.Vector3(size, 0, 0))
    pointMat.postMultiply(transl)
    pointMat.postMultiply(BigWorld.camera().invViewMatrix)
    p = pointMat.applyToOrigin()
    pV4 = wtcMat.applyV4Point(Math.Vector4(p[0], p[1], p[2], 1))
    oV4 = wtcMat.applyV4Point(Math.Vector4(0, 0, 0, 1))
    pV3 = Math.Vector3(pV4[0], pV4[1], pV4[2]).scale(1.0 / pV4[3])
    oV3 = Math.Vector3(oV4[0], oV4[1], oV4[2]).scale(1.0 / oV4[3])
    return math.fabs(pV3[0] - oV3[0]) + math.fabs(pV3[1] - oV3[1])
