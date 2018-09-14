# Embedded file name: scripts/client/AvatarInputHandler/__init__.py
import functools
import math
from AvatarInputHandler.CallbackDelayer import CallbackDelayer
import BigWorld
import Math
import ResMgr
import Keys
import FMOD
from AvatarInputHandler.AimingSystems.SniperAimingSystem import SniperAimingSystem
import GUI
from Event import Event
from debug_utils import *
from gui import g_guiResetters
from gui.Scaleform.CursorDelegator import g_cursorDelegator
from gui.battle_control import g_sessionProvider
from gui.battle_control.consumables.ammo_ctrl import SHELL_SET_RESULT
from post_processing.post_effect_controllers import g_postProcessingEvents
import control_modes
import constants
import cameras
import DynamicCameras.ArcadeCamera
import DynamicCameras.SniperCamera
import DynamicCameras.StrategicCamera
import BattleReplay
from constants import ARENA_PERIOD, AIMING_MODE
_INPUT_HANDLER_CFG = 'gui/avatar_input_handler.xml'
_CTRLS_FIRST = 'arcade'

class _CTRL_TYPE():
    USUAL = 0
    OPTIONAL = 1
    DEVELOPMENT = 2


_CTRLS_DESC_MAP = {'arcade': ('ArcadeControlMode', 'arcadeMode', _CTRL_TYPE.USUAL),
 'strategic': ('StrategicControlMode', 'strategicMode', _CTRL_TYPE.USUAL),
 'sniper': ('SniperControlMode', 'sniperMode', _CTRL_TYPE.USUAL),
 'postmortem': ('PostMortemControlMode', 'postMortemMode', _CTRL_TYPE.USUAL),
 'debug': ('DebugControlMode', None, _CTRL_TYPE.DEVELOPMENT),
 'cat': ('CatControlMode', None, _CTRL_TYPE.DEVELOPMENT),
 'video': ('VideoCameraControlMode', 'videoMode', _CTRL_TYPE.OPTIONAL)}
_DYNAMIC_CAMERAS = (DynamicCameras.ArcadeCamera.ArcadeCamera, DynamicCameras.SniperCamera.SniperCamera, DynamicCameras.StrategicCamera.StrategicCamera)

class ShakeReason():
    OWN_SHOT = 0
    OWN_SHOT_DELAYED = 1
    HIT = 2
    HIT_NO_DAMAGE = 3
    SPLASH = 4


class DynamicCameraSettings(object):
    settings = property(lambda self: self.__dynamic)

    def __init__(self, dataSec):
        self.__dynamic = {'caliberImpulses': [],
         'massSensitivity': []}
        caliberSettings = dataSec['caliberImpulses']
        if caliberSettings is not None:
            self.__dynamic['caliberImpulses'] = self.__readRange(caliberSettings)
        else:
            LOG_ERROR('<caliberImpulses> dataSection is not found!')
        sensitivitySettings = dataSec['massSensitivity']
        if sensitivitySettings is not None:
            self.__dynamic['massSensitivity'] = self.__readRange(sensitivitySettings)
        else:
            LOG_ERROR('<massSensitivity> dataSection is not found!')
        self.__dynamic['collisionSpeedToImpulseRatio'] = cameras.readFloat(dataSec, 'collisionSpeedToImpulseRatio', 0, 1000, 1.0)
        self.__dynamic['minCollisionSpeed'] = cameras.readFloat(dataSec, 'minCollisionSpeed', 0, 1000, 1.0)
        self.__dynamic['zeroDamageHitSensitivity'] = cameras.readFloat(dataSec, 'zeroDamageHitSensitivity', 0, 1000, 1.0)
        self.__dynamic['ownShotImpulseDelay'] = cameras.readFloat(dataSec, 'ownShotImpulseDelay', 0.0, 1000, 0.0)
        return

    def getGunImpulse(self, caliber):
        impulseMagnitude = 0.0
        for minCaliber, magnitude in self.__dynamic['caliberImpulses']:
            if caliber < minCaliber:
                break
            impulseMagnitude = magnitude

        return impulseMagnitude

    def getSensitivityToImpulse(self, vehicleMass):
        sensitivity = 0.0
        for mass, sense in self.__dynamic['massSensitivity']:
            if vehicleMass < mass:
                break
            sensitivity = sense

        return sensitivity

    def __readRange(self, dataSec):
        ranges = []
        for rangeSec in dataSec.values():
            val = rangeSec.asVector2
            ranges.append((val.x, val.y))

        ranges.sort(key=lambda val: val[0])
        return ranges


class AvatarInputHandler(CallbackDelayer):
    aim = property(lambda self: self.__curCtrl.getAim())
    ctrl = property(lambda self: self.__curCtrl)
    ctrls = property(lambda self: self.__ctrls)
    isSPG = property(lambda self: self.__isSPG)
    isATSPG = property(lambda self: self.__isATSPG)
    isFlashBangAllowed = property(lambda self: self.__ctrls['video'] != self.__curCtrl)
    _DYNAMIC_CAMERAS_ENABLED_KEY = 'global/dynamicCameraEnabled'

    @staticmethod
    def enableDynamicCamera(enable, useHorizontalStabilizer = True):
        for dynamicCameraClass in _DYNAMIC_CAMERAS:
            dynamicCameraClass.enableDynamicCamera(enable)

        SniperAimingSystem.setStabilizerSettings(useHorizontalStabilizer and enable, enable)

    @staticmethod
    def isCameraDynamic():
        for dynamicCameraClass in _DYNAMIC_CAMERAS:
            if not dynamicCameraClass.isCameraDynamic():
                return False

        return True

    @staticmethod
    def isSniperStabilized():
        return SniperAimingSystem.getStabilizerSettings()

    def __init__(self):
        CallbackDelayer.__init__(self)
        self.__alwaysShowAim = False
        self.__alwaysShowAimKey = None
        self.__showMarkersKey = None
        sec = self._readCfg()
        self.onCameraChanged = Event()
        self.onPostmortemVehicleChanged = Event()
        self.__isArenaStarted = False
        self.__isStarted = False
        self.__targeting = _Targeting()
        self.__vertScreenshotCamera = _VertScreenshotCamera()
        self.__ctrls = dict()
        self.__killerVehicleID = None
        self.__isAutorotation = True
        self.__prevModeAutorotation = None
        self.__isSPG = False
        self.__isATSPG = False
        self.__setupCtrls(sec)
        self.__curCtrl = self.__ctrls[_CTRLS_FIRST]
        self.__detachCount = 0
        return

    def prerequisites(self):
        out = []
        for ctrl in self.__ctrls.itervalues():
            out += ctrl.prerequisites()

        return out

    def handleKeyEvent(self, event):
        cursorDetached = self.__detachCount < 0
        import game
        isDown, key, mods, isRepeat = game.convertKeyEvent(event)
        if isRepeat:
            return False
        elif self.__isStarted and cursorDetached:
            return BigWorld.player().handleKey(isDown, key, mods)
        elif not self.__isStarted or cursorDetached:
            return False
        if isDown and BigWorld.isKeyDown(Keys.KEY_CAPSLOCK):
            if self.__alwaysShowAimKey is not None and key == self.__alwaysShowAimKey:
                self.__alwaysShowAim = not self.__alwaysShowAim
                getAim = getattr(self.__curCtrl, 'getAim')
                if getAim is not None:
                    aim = getAim()
                    if aim is not None:
                        aim.setVisible(self.__alwaysShowAim or BigWorld.player().isGuiVisible)
                return True
            if self.__showMarkersKey is not None and key == self.__showMarkersKey and not BigWorld.player().isGuiVisible:
                from gui.WindowsManager import g_windowsManager
                markersManager = g_windowsManager.battleWindow.vMarkersManager
                markersManager.active(not markersManager.isActive)
                return True
            if key == Keys.KEY_F5 and constants.IS_DEVELOPMENT:
                self.__vertScreenshotCamera.enable(not self.__vertScreenshotCamera.isEnabled)
                return True
        if self.__curCtrl.handleKeyEvent(isDown, key, mods, event):
            return True
        else:
            return BigWorld.player().handleKey(isDown, key, mods)

    def handleMouseEvent(self, dx, dy, dz):
        if not self.__isStarted or self.__detachCount < 0:
            return False
        return self.__curCtrl.handleMouseEvent(dx, dy, dz)

    def detachCursor(self, isDetached, enableAiming):
        if not self.__isStarted:
            return
        self.__detachCount += -1 if isDetached else 1
        if not self.__detachCount <= 0:
            raise AssertionError
            if self.__detachCount == -1 and isDetached:
                self.__targeting.enable(False)
                g_cursorDelegator.activateCursor()
                enableAiming and self.setAimingMode(False, AIMING_MODE.USER_DISABLED)
        elif not self.__detachCount:
            self.__targeting.enable(True)
            g_cursorDelegator.detachCursor()

    def updateShootingStatus(self, canShoot):
        if self.__detachCount < 0:
            return
        return self.__curCtrl.updateShootingStatus(canShoot)

    def getDesiredShotPoint(self):
        if self.__detachCount < 0:
            return None
        else:
            g_postProcessingEvents.onFocalPlaneChanged()
            return self.__curCtrl.getDesiredShotPoint()

    def showGunMarker(self, flag):
        self.__curCtrl.showGunMarker(flag)

    def showGunMarker2(self, flag):
        self.__curCtrl.showGunMarker2(flag)

    def updateGunMarker(self, pos, dir, size, relaxTime, collData):
        aim = self.__curCtrl.getAim()
        if aim is not None:
            aim.updateMarkerPos(pos, relaxTime)
        self.__curCtrl.updateGunMarker(pos, dir, size, relaxTime, collData)
        return

    def updateGunMarker2(self, pos, dir, size, relaxTime, collData):
        self.__curCtrl.updateGunMarker2(pos, dir, size, relaxTime, collData)

    def setAimingMode(self, enable, mode):
        self.__curCtrl.setAimingMode(enable, mode)

    def getAimingMode(self, mode):
        return self.__curCtrl.getAimingMode(mode)

    def setAutorotation(self, bValue):
        if not self.__curCtrl.enableSwitchAutorotationMode():
            return
        elif not BigWorld.player().isOnArena:
            return
        else:
            if self.__isAutorotation != bValue:
                self.__isAutorotation = bValue
                BigWorld.player().enableOwnVehicleAutorotation(self.__isAutorotation)
            self.__prevModeAutorotation = None
            return

    def getAutorotation(self):
        return self.__isAutorotation

    def switchAutorotation(self):
        self.setAutorotation(not self.__isAutorotation)

    def activatePostmortem(self):
        try:
            params = self.__curCtrl.postmortemCamParams
        except:
            params = None

        onPostmortemActivation = getattr(self.__curCtrl, 'onPostmortemActivation', None)
        if onPostmortemActivation is not None:
            onPostmortemActivation()
        else:
            self.onControlModeChanged('postmortem', postmortemParams=params, bPostmortemDelay=True)
        return

    def setKillerVehicleID(self, killerVehicleID):
        self.__killerVehicleID = killerVehicleID

    def getKillerVehicleID(self):
        return self.__killerVehicleID

    def start(self):
        g_guiResetters.add(self.__onRecreateDevice)
        import aims
        aims.clearState()
        ownVehicle = BigWorld.entity(BigWorld.player().playerVehicleID)
        vehTypeDesc = ownVehicle.typeDescriptor.type
        self.__isSPG = 'SPG' in vehTypeDesc.tags
        self.__isATSPG = 'AT-SPG' in vehTypeDesc.tags
        for control in self.__ctrls.itervalues():
            control.create()

        self.__addBattleCtrlListeners()
        g_cursorDelegator.detachCursor()
        if not self.__curCtrl.isManualBind():
            BigWorld.player().positionControl.bindToVehicle(True)
        self.__curCtrl.enable(ctrlState=control_modes.dumpStateEmpty())
        self.onCameraChanged('arcade')
        tmp = self.__curCtrl.getPreferredAutorotationMode()
        if tmp is not None:
            self.__isAutorotation = tmp
            self.__prevModeAutorotation = True
        else:
            self.__isAutorotation = True
            self.__prevModeAutorotation = None
        BigWorld.player().enableOwnVehicleAutorotation(self.__isAutorotation)
        self.__targeting.enable(True)
        self.__isStarted = True
        self.__isGUIVisible = True
        self.__killerVehicleID = None
        arena = BigWorld.player().arena
        arena.onPeriodChange += self.__onArenaStarted
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        g_settingsCore.onSettingsChanged += self.__onSettingsChanged
        self.__onArenaStarted(arena.period)
        return

    def stop(self):
        self.__isStarted = False
        FMOD.setEventsParam('viewPlayMode', 0)
        self.__removeBattleCtrlListeners()
        for control in self.__ctrls.itervalues():
            control.destroy()

        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isRecording:
            replayCtrl.setPlayerVehicleID(0)
        self.onCameraChanged = None
        self.__targeting.enable(False)
        self.__killerVehicleID = None
        g_guiResetters.remove(self.__onRecreateDevice)
        BigWorld.player().arena.onPeriodChange -= self.__onArenaStarted
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        g_settingsCore.onSettingsChanged -= self.__onSettingsChanged
        CallbackDelayer.destroy(self)
        return

    def onControlModeChanged(self, eMode, **args):
        if not self.__isArenaStarted and eMode != 'postmortem':
            return
        else:
            player = BigWorld.player()
            ctrl = BattleReplay.g_replayCtrl
            if ctrl.isRecording:
                ctrl.setControlMode(eMode)
            ctrlState = self.__curCtrl.dumpState()
            self.__curCtrl.disable()
            prevCtrl = self.__curCtrl
            self.__curCtrl = self.__ctrls[eMode]
            if player is not None:
                if not prevCtrl.isManualBind() and self.__curCtrl.isManualBind():
                    player.positionControl.bindToVehicle(False)
                if prevCtrl.isManualBind() and not self.__curCtrl.isManualBind():
                    player.positionControl.bindToVehicle(True)
            if player is not None:
                newAutoRotationMode = self.__curCtrl.getPreferredAutorotationMode()
                if newAutoRotationMode is not None:
                    if prevCtrl.getPreferredAutorotationMode() is None:
                        self.__prevModeAutorotation = self.__isAutorotation
                    if self.__isAutorotation != newAutoRotationMode:
                        self.__isAutorotation = newAutoRotationMode
                        BigWorld.player().enableOwnVehicleAutorotation(self.__isAutorotation)
                elif prevCtrl.getPreferredAutorotationMode() is not None:
                    if self.__prevModeAutorotation is None:
                        self.__prevModeAutorotation = True
                    if self.__isAutorotation != self.__prevModeAutorotation:
                        self.__isAutorotation = self.__prevModeAutorotation
                        BigWorld.player().enableOwnVehicleAutorotation(self.__isAutorotation)
                    self.__prevModeAutorotation = None
            self.__targeting.onRecreateDevice()
            aim = self.aim
            GUI.mcursor().position = aim.offset() if aim is not None else (0, 0)
            self.__curCtrl.setGUIVisible(self.__isGUIVisible)
            self.__curCtrl.enable(ctrlState=ctrlState, **args)
            self.onCameraChanged(eMode)
            if self.__alwaysShowAim:
                getAim = getattr(self.__curCtrl, 'getAim')
                if getAim is not None:
                    aim = getAim()
                    if aim is not None:
                        aim.setVisible(self.__alwaysShowAim or BigWorld.player().isGuiVisible)
            return

    def getTargeting(self):
        return self.__targeting

    def setGUIVisible(self, isVisible):
        self.__isGUIVisible = isVisible
        self.__curCtrl.setGUIVisible(isVisible)
        self.__alwaysShowAim = False

    def selectPlayer(self, vehId):
        self.__curCtrl.selectPlayer(vehId)

    def onMinimapClicked(self, worldPos):
        self.__curCtrl.onMinimapClicked(worldPos)

    def setReloading(self, duration, startTime = None, baseTime = None):
        self.__curCtrl.setReloading(duration, startTime)
        if self.aim is not None:
            self.aim.setReloading(duration, startTime, baseTime)
        return

    def setReloadingInPercent(self, percent):
        self.__curCtrl.setReloadingInPercent(percent)
        if self.aim is not None:
            self.aim.setReloadingInPercent(percent)
        return

    def onVehicleShaken(self, vehicle, impulsePosition, impulseDir, caliber, shakeReason):
        if shakeReason == ShakeReason.OWN_SHOT_DELAYED:
            shakeFuncBound = functools.partial(self.onVehicleShaken, vehicle, impulsePosition, impulseDir, caliber, ShakeReason.OWN_SHOT)
            delayTime = self.__dynamicCameraSettings.settings['ownShotImpulseDelay']
            self.delayCallback(delayTime, shakeFuncBound)
            return
        else:
            camera = getattr(self.ctrl, 'camera', None)
            if camera is None:
                return
            impulseValue = self.__dynamicCameraSettings.getGunImpulse(caliber)
            vehicleSensitivity = 0.0
            avatarVehicle = BigWorld.player().getVehicleAttached()
            if avatarVehicle is None or not avatarVehicle.isAlive():
                return
            avatarVehicleTypeDesc = getattr(avatarVehicle, 'typeDescriptor', None)
            if avatarVehicleTypeDesc is not None:
                avatarVehWeightTons = avatarVehicleTypeDesc.physics['weight'] / 1000.0
                vehicleSensitivity = self.__dynamicCameraSettings.getSensitivityToImpulse(avatarVehWeightTons)
                vehicleSensitivity *= avatarVehicleTypeDesc.hull['swinging']['sensitivityToImpulse']
            impulseReason = None
            isDistant = False
            if shakeReason == ShakeReason.OWN_SHOT:
                if vehicle is avatarVehicle:
                    impulseReason = cameras.ImpulseReason.MY_SHOT
                    isDistant = False
                else:
                    impulseReason = cameras.ImpulseReason.OTHER_SHOT
                    isDistant = True
            elif vehicle is avatarVehicle:
                if shakeReason == ShakeReason.HIT or shakeReason == ShakeReason.HIT_NO_DAMAGE:
                    impulseValue *= 1.0 if shakeReason == ShakeReason.HIT else self.__dynamicCameraSettings.settings['zeroDamageHitSensitivity']
                    impulseReason = cameras.ImpulseReason.ME_HIT
                    isDistant = False
                else:
                    impulseReason = cameras.ImpulseReason.SPLASH
                    isDistant = True
            impulseDir, impulseValue = self.__adjustImpulse(impulseDir, impulseValue, camera, impulsePosition, vehicleSensitivity, impulseReason)
            if isDistant:
                camera.applyDistantImpulse(impulsePosition, impulseValue, impulseReason)
            else:
                camera.applyImpulse(impulsePosition, impulseDir * impulseValue, impulseReason)
            return

    def onVehicleCollision(self, vehicle, impactVelocity):
        if impactVelocity < self.__dynamicCameraSettings.settings['minCollisionSpeed']:
            return
        else:
            camera = getattr(self.ctrl, 'camera', None)
            if camera is None:
                return
            avatarVehicle = BigWorld.player().getVehicleAttached()
            if avatarVehicle is None or not avatarVehicle.isAlive():
                return
            if vehicle is avatarVehicle:
                impulse = Math.Vector3(0, impactVelocity * self.__dynamicCameraSettings.settings['collisionSpeedToImpulseRatio'], 0)
                camera.applyImpulse(vehicle.position, impulse, cameras.ImpulseReason.COLLISION)
            return

    def onVehicleDeath(self, vehicle, exploded):
        if not exploded:
            return
        else:
            camera = getattr(self.ctrl, 'camera', None)
            if camera is None:
                return
            avatarVehicle = BigWorld.player().getVehicleAttached()
            if avatarVehicle is None or avatarVehicle is vehicle:
                return
            caliber = vehicle.typeDescriptor.shot['shell']['caliber']
            impulseValue = self.__dynamicCameraSettings.getGunImpulse(caliber)
            avatarVehicleWeightInTons = avatarVehicle.typeDescriptor.physics['weight'] / 1000.0
            vehicleSensitivity = self.__dynamicCameraSettings.getSensitivityToImpulse(avatarVehicleWeightInTons)
            vehicleSensitivity *= avatarVehicle.typeDescriptor.hull['swinging']['sensitivityToImpulse']
            _, impulseValue = self.__adjustImpulse(Math.Vector3(0, 0, 0), impulseValue, camera, vehicle.position, vehicleSensitivity, cameras.ImpulseReason.VEHICLE_EXPLOSION)
            camera.applyDistantImpulse(vehicle.position, impulseValue, cameras.ImpulseReason.VEHICLE_EXPLOSION)
            return

    def onProjectileHit(self, position, caliber, isOwnShot):
        if not isOwnShot:
            return
        else:
            camera = getattr(self.ctrl, 'camera', None)
            if camera is None:
                return
            impulseValue = self.__dynamicCameraSettings.getGunImpulse(caliber)
            vehicleSensitivity = 1.0
            avatarVehicle = BigWorld.player().getVehicleAttached()
            if avatarVehicle is not None:
                avatarVehicleWeightInTons = avatarVehicle.typeDescriptor.physics['weight'] / 1000.0
                vehicleSensitivity = self.__dynamicCameraSettings.getSensitivityToImpulse(avatarVehicleWeightInTons)
                vehicleSensitivity *= avatarVehicle.typeDescriptor.hull['swinging']['sensitivityToImpulse']
            _, impulseValue = self.__adjustImpulse(Math.Vector3(0, 0, 0), impulseValue, camera, position, vehicleSensitivity, cameras.ImpulseReason.VEHICLE_EXPLOSION)
            camera.applyDistantImpulse(position, impulseValue, cameras.ImpulseReason.PROJECTILE_HIT)
            return

    def __adjustImpulse(self, impulseDir, impulseValue, camera, impulsePosition, vehicleSensitivity, impulseReason):
        if impulseReason in camera.getReasonsAffectCameraDirectly():
            dirToCamera = camera.camera.position - impulsePosition
            dirToCamera.normalise()
            impulseDir = dirToCamera
        else:
            impulseValue *= vehicleSensitivity
        return (impulseDir, impulseValue)

    def reloadDynamicSettings(self):
        if not constants.IS_DEVELOPMENT:
            return
        sec = ResMgr.openSection(_INPUT_HANDLER_CFG)
        self.__dynamicCameraSettings = DynamicCameraSettings(sec['dynamicCameraCommon'])

    def _readCfg(self):
        sec = ResMgr.openSection(_INPUT_HANDLER_CFG)
        if sec is None:
            LOG_ERROR('can not open <%s>.' % _INPUT_HANDLER_CFG)
            return
        else:
            self.__checkSections(sec)
            keySec = sec['keys']
            if keySec is not None:
                self.__showMarkersKey = getattr(Keys, keySec.readString('showMarkersKey', ''), None)
                self.__alwaysShowAimKey = getattr(Keys, keySec.readString('alwaysShowAimKey', ''), None)
            self.__dynamicCameraSettings = DynamicCameraSettings(sec['dynamicCameraCommon'])
            return sec

    def __setupCtrls(self, section):
        for name, desc in _CTRLS_DESC_MAP.items():
            if desc[2] != _CTRL_TYPE.DEVELOPMENT or desc[2] == _CTRL_TYPE.DEVELOPMENT and constants.IS_DEVELOPMENT:
                if name not in self.__ctrls:
                    self.__ctrls[name] = getattr(control_modes, desc[0])(section[desc[1]] if desc[1] else None, self)

        return

    def __checkSections(self, section):
        for name, desc in _CTRLS_DESC_MAP.items():
            if desc[1] is None or desc[2] == _CTRL_TYPE.OPTIONAL or desc[2] == _CTRL_TYPE.DEVELOPMENT and not constants.IS_DEVELOPMENT:
                continue
            if not section.has_key(desc[1]):
                LOG_ERROR('Invalid section <%s> in <%s>.' % (desc[1], _INPUT_HANDLER_CFG))

        return

    def __onArenaStarted(self, period, *args):
        self.__isArenaStarted = True if period == ARENA_PERIOD.BATTLE else False
        show = self.__isGUIVisible and self.__isArenaStarted
        self.__curCtrl.showGunMarker2(show and control_modes.useServerAim())
        if constants.IS_DEVELOPMENT:
            showArcadeAim = show
        else:
            showArcadeAim = show and not control_modes.useServerAim()
        self.__curCtrl.showGunMarker(showArcadeAim)

    def __onRecreateDevice(self):
        self.__curCtrl.onRecreateDevice()
        self.__targeting.onRecreateDevice()

    def __onSettingsChanged(self, diff):
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        if 'dynamicCamera' in diff or 'horStabilizationSnp' in diff:
            dynamicCamera = g_settingsCore.getSetting('dynamicCamera')
            horStabilizationSnp = g_settingsCore.getSetting('horStabilizationSnp')
            self.enableDynamicCamera(dynamicCamera, horStabilizationSnp)

    def __addBattleCtrlListeners(self):
        ammoCtrl = g_sessionProvider.getAmmoCtrl()
        self.__onGunSettingsSet(ammoCtrl.getGunSettings())
        ammoCtrl.onGunSettingsSet += self.__onGunSettingsSet
        ammoCtrl.onGunReloadTimeSet += self.__onGunReloadTimeSet
        ammoCtrl.onGunReloadTimeSetInPercent += self.__onGunReloadTimeSetInPercent
        ammoCtrl.onCurrentShellChanged += self.__onCurrentShellChanged
        ammoCtrl.onShellsUpdated += self.__onShellsUpdated

    def __removeBattleCtrlListeners(self):
        ammoCtrl = g_sessionProvider.getAmmoCtrl()
        ammoCtrl.onGunSettingsSet -= self.__onGunSettingsSet
        ammoCtrl.onGunReloadTimeSet -= self.__onGunReloadTimeSet
        ammoCtrl.onGunReloadTimeSetInPercent -= self.__onGunReloadTimeSetInPercent
        ammoCtrl.onCurrentShellChanged -= self.__onCurrentShellChanged
        ammoCtrl.onShellsUpdated -= self.__onShellsUpdated

    def __onGunSettingsSet(self, gunSettings):
        aim = self.__curCtrl.getAim()
        if aim:
            self.__curCtrl.getAim().setClipParams(gunSettings.clip.size, gunSettings.burst.size)

    def __onGunReloadTimeSet(self, _, timeLeft, baseTime):
        self.setReloading(timeLeft, None, baseTime)
        return

    def __onGunReloadTimeSetInPercent(self, _, percent):
        self.setReloadingInPercent(percent)

    def __onCurrentShellChanged(self, _):
        aim = self.__curCtrl.getAim()
        if aim:
            aim.setAmmoStock(*g_sessionProvider.getAmmoCtrl().getCurrentShells())

    def __onShellsUpdated(self, _, quantity, quantityInClip, result):
        if not result & SHELL_SET_RESULT.CURRENT:
            return
        aim = self.__curCtrl.getAim()
        if aim:
            aim.setAmmoStock(quantity, quantityInClip, result & SHELL_SET_RESULT.CASSETTE_RELOAD > 0)


class _Targeting():

    def __init__(self):
        target = BigWorld.target
        target.selectionFovDegrees = 1.0
        target.deselectionFovDegrees = 80.0
        target.maxDistance = 710.0
        target.skeletonCheckEnabled = True
        BigWorld.target.isEnabled = False
        self.__mouseMatProv = BigWorld.MouseTargettingMatrix()

    def isEnabled(self):
        return BigWorld.target.isEnabled

    def getTargetEntity(self):
        return BigWorld.target.entity

    def enable(self, flag):
        if flag and not BigWorld.target.isEnabled:
            BigWorld.target.isEnabled = True
            BigWorld.target.source = self.__mouseMatProv
        elif not flag:
            BigWorld.target.isEnabled = False
            BigWorld.target.clear()
            BigWorld.target.source = None
        return

    def onRecreateDevice(self):
        if BigWorld.target.isEnabled:
            BigWorld.target.clear()


class _VertScreenshotCamera(object):
    isEnabled = property(lambda self: self.__isEnabled)

    def __init__(self):
        self.__isEnabled = False
        self.__watcherNames = ('Render/Fov', 'Render/Near Plane', 'Render/Far Plane', 'Render/Objects Far Plane/Enabled', 'Render/Shadows/dynamicEnabled', 'Render/Shadows/dynamicViewDistanceTo', 'Visibility/Draw tanks', 'Visibility/Control Points', 'Visibility/GUI', 'Visibility/particles', 'Client Settings/std fog/enabled', 'Client Settings/Script tick')

    def destroy(self):
        self.enable(False)

    def enable(self, doEnable):
        if self.__isEnabled == doEnable:
            return
        if not doEnable:
            self.__isEnabled = False
            BigWorld.camera(self.__savedCamera)
            BigWorld.wg_enableSuperShot(False, False)
            for k, v in self.__savedWatchers.iteritems():
                BigWorld.setWatcher(k, v)

            LOG_DEBUG('Vertical screenshot camera is disabled')
            return
        self.__isEnabled = True
        self.__savedCamera = BigWorld.camera()
        arenaBB = BigWorld.wg_getSpaceBounds()
        centerXZ = Math.Vector2(0.5 * (arenaBB[0] + arenaBB[2]), 0.5 * (arenaBB[1] + arenaBB[3]))
        halfSizesXZ = Math.Vector2(0.5 * (arenaBB[2] - arenaBB[0]), 0.5 * (arenaBB[3] - arenaBB[1]))
        camFov = math.radians(15.0)
        camPos = Math.Vector3(centerXZ.x, 0, centerXZ.z)
        aspectRatio = 1.0
        if not BigWorld.isVideoWindowed():
            aspectRatio = BigWorld.getFullScreenAspectRatio()
        else:
            aspectRatio = BigWorld.screenWidth() / BigWorld.screenHeight()
        camPos.y = max(halfSizesXZ.x / math.sin(0.5 * camFov * aspectRatio), halfSizesXZ.y / math.sin(0.5 * camFov))
        camMatr = Math.Matrix()
        camMatr.setRotateYPR(Math.Vector3(0.0, math.pi * 0.5, 0.0))
        camMatr.translation = camPos
        camMatr.invert()
        self.__cam = BigWorld.FreeCamera()
        self.__cam.set(camMatr)
        BigWorld.camera(self.__cam)
        BigWorld.wg_enableSuperShot(True, False)
        self.__savedWatchers = {}
        for name in self.__watcherNames:
            self.__savedWatchers[name] = BigWorld.getWatcher(name)
            if name.startswith('Visibility'):
                BigWorld.setWatcher(name, False)

        BigWorld.setWatcher('Client Settings/std fog/enabled', False)
        BigWorld.setWatcher('Render/Fov', camFov)
        BigWorld.setWatcher('Render/Near Plane', max(0.1, camPos.y - 1000.0))
        BigWorld.setWatcher('Render/Far Plane', camPos.y + 1000.0)
        BigWorld.setWatcher('Render/Objects Far Plane/Enabled', False)
        BigWorld.setWatcher('Render/Shadows/dynamicEnabled', False)
        BigWorld.setWatcher('Render/Shadows/dynamicViewDistanceTo', 1000000)
        BigWorld.setWatcher('Client Settings/Script tick', False)
        LOG_DEBUG('Vertical screenshot camera is enabled')
