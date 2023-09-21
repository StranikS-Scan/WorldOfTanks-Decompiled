# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/avatar_components/AvatarObserver.py
from collections import defaultdict
import logging
import BigWorld
import Math
import BattleReplay
from PlayerEvents import g_playerEvents
from aih_constants import CTRL_MODE_NAME, CTRL_MODES
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as BONUS_CAPS
from helpers.CallbackDelayer import CallbackDelayer
_logger = logging.getLogger(__name__)
_OBSERVABLE_VIEWS = (CTRL_MODE_NAME.ARCADE,
 CTRL_MODE_NAME.SNIPER,
 CTRL_MODE_NAME.DUAL_GUN,
 CTRL_MODE_NAME.STRATEGIC,
 CTRL_MODE_NAME.ARTY)
_STRATEGIC_VIEW = (CTRL_MODE_NAME.STRATEGIC, CTRL_MODE_NAME.ARTY)

class ObservedVehicleData(object):
    __slots__ = ('dispAngle',)

    def __init__(self):
        super(ObservedVehicleData, self).__init__()
        self.dispAngle = 0


class AvatarObserver(CallbackDelayer):
    observedVehicleID = property(lambda self: self.__observedVehicleID)
    observedVehicleData = property(lambda self: self.__observedVehicleData)
    isFPVModeSwitching = property(lambda self: self.__isFPVModeSwitching)
    observerFPVControlMode = property(lambda self: self.__observerFPVControlMode)

    def __init__(self):
        super(AvatarObserver, self).__init__()
        self.__observedVehicleID = None
        self.__observedVehicleData = defaultdict(ObservedVehicleData)
        self.__previousObservedVehicleID = None
        self.__isFPVModeSwitching = False
        self.__observerFPVControlMode = CTRL_MODES.index(CTRL_MODE_NAME.ARCADE)
        return

    def switchObserverFPV(self):
        if BattleReplay.isServerSideReplay():
            self.isObserverFPV = not self.isObserverFPV
            self.set_isObserverFPV(self.isObserverFPV)
            return
        if self.__isFPVModeSwitching:
            self.stopCallback(self.__resetFPVModeSwitching)
            _logger.warning('switchObserverFPV happened during switching cooldown! isFPVModeSwitching check missed!')
        self.__isFPVModeSwitching = True
        self.delayCallback(0.5, self.__resetFPVModeSwitching)
        self.cell.switchObserverFPV(not BigWorld.player().isObserverFPV)

    def onBecomePlayer(self):
        self.cell.switchObserverFPV(False)

    def onBecomeNonPlayer(self):
        CallbackDelayer.destroy(self)

    def handleKey(self, isDown, key, mods):
        return False

    def onEnterWorld(self):
        if self.isObserver():
            self.filter.setInterpolationType(BigWorld.AvatarSubfilters.CAMERA_SHOT_POINT, BigWorld.FilterInterpolationType.LINEAR)
            self.filter.resetVector3(BigWorld.AvatarSubfilters.CAMERA_SHOT_POINT)

    def getObservedVehicleID(self):
        return self.__observedVehicleID if self.isObserver() else self.playerVehicleID

    def onVehicleChanged(self):
        _logger.debug('Avatar vehicle has changed to %r', self.vehicle)
        if not self.vehicle and self.observerSeesAll():
            self.__observedVehicleID = 0
            return
        else:
            if self.vehicle is not None:
                typeofveh = 'observed' if self.__observedVehicleID == self.vehicle.id else 'players'
                _logger.debug('Vehicle ID is %r and is %r', self.vehicle.id, typeofveh)
            isObserving = self.isObserver()
            if isObserving and self.vehicle is not None:
                self.__observedVehicleID = self.vehicle.id
                self.onObserverVehicleChanged()
                self.guiSessionProvider.getArenaDP().switchCurrentTeam(self.vehicle.publicInfo['team'])
                g_playerEvents.onAvatarObserverVehicleChanged(self.vehicle.id)
                self.inputHandler.setObservedVehicle(self.__observedVehicleID)
                if self.gunRotator is not None:
                    self.gunRotator.start()
                self.updateObservedVehicleData()
                if self.__previousObservedVehicleID and self.vehicle.id != self.__previousObservedVehicleID:
                    self.guiSessionProvider.updateVehicleEffects(BigWorld.entity(self.__previousObservedVehicleID))
                self.vehicle.set_dotEffect()
                self.vehicle.refreshBuffEffects()
                self.__previousObservedVehicleID = self.__observedVehicleID
                if hasattr(self.vehicle.filter, 'enableStabilisedMatrix'):
                    self.vehicle.filter.enableStabilisedMatrix(True)
                if not self.guiSessionProvider.shared.vehicleState.isInPostmortem:
                    BigWorld.target.exclude = self.vehicle
                    for v in BigWorld.player().vehicles:
                        if v.appearance is not None:
                            v.appearance.highlighter.setVehicleOwnership()
                            self.guiSessionProvider.stopVehicleVisual(v.id, False)
                            self.guiSessionProvider.startVehicleVisual(v, True)

            return

    def updateObservedVehicleData(self):
        vehicle = self.getVehicleAttached()
        if vehicle is not None and hasattr(vehicle, 'ownVehicle'):
            self.stopCallback(self.updateObservedVehicleData)
            extraData = self.observedVehicleData[self.__observedVehicleID]
            if self.gunRotator is not None:
                turretYaw, gunPitch = vehicle.getAimParams()
                self.gunRotator.forceGunParams(turretYaw, gunPitch, extraData.dispAngle)
            self.guiSessionProvider.updateObservedVehicleData(vehicle)
        elif self.vehicle:
            return self.delayCallback(0.0, self.updateObservedVehicleData)
        return

    def vehicle_onAppearanceReady(self, vehicle):
        pass

    def getObservedVehicleMatrix(self):
        player = BigWorld.player()
        if player.isObserver():
            vehicle = player.getVehicleAttached()
            if vehicle is not None:
                if isinstance(vehicle.filter, BigWorld.WGVehicleFilter):
                    return vehicle.filter.bodyMatrix
                return vehicle.matrix
        return

    def getObservedVehicleStabilisedMatrix(self):
        player = BigWorld.player()
        if player.isObserver():
            vehicle = player.getVehicleAttached()
            if vehicle is not None:
                if isinstance(vehicle.filter, BigWorld.WGVehicleFilter):
                    return vehicle.filter.stabilisedMatrix
                return vehicle.matrix
        return

    def getObservedVehicleTurretMatrix(self):
        player = BigWorld.player()
        if player.isObserver():
            vehicle = player.getVehicleAttached()
            if vehicle is not None:
                if isinstance(vehicle.filter, BigWorld.WGVehicleFilter):
                    return vehicle.filter.bodyMatrix
                return vehicle.appearance.turretMatrix
        return

    def getVehicleAttached(self):
        vehicle = self.vehicle
        if vehicle is None:
            vehicle = BigWorld.entity(self.__observedVehicleID if self.__observedVehicleID else self.playerVehicleID)
        if vehicle is not None and vehicle.isHidden:
            return vehicle
        else:
            return None if vehicle is None or not vehicle.inWorld or not vehicle.isStarted or vehicle.isDestroyed else vehicle

    def clearObservedVehicleID(self):
        self.__observedVehicleID = None
        return

    def getVehicleDescriptor(self):
        descr = self.vehicleTypeDescriptor
        if self.isObserver() and self.getVehicleAttached() is not None:
            descr = self.getVehicleAttached().typeDescriptor
        return descr

    def setRemoteCamera(self, remoteCamera):
        self.remoteCamera = remoteCamera
        if self.__observerFPVControlMode != remoteCamera.mode:
            self.__setObserverFPVControlMode(remoteCamera.mode)
        if self.inWorld:
            self.filter.syncVector3(BigWorld.AvatarSubfilters.CAMERA_SHOT_POINT, remoteCamera.shotPoint, remoteCamera.time + (0.5 if BattleReplay.isServerSideReplay() else 0.0))

    def set_isObserverFPV(self, prev):
        _logger.debug('AvatarObserver.set_isObserverFPV() %r', self.isObserverFPV)
        self.__applyObserverModeChange()

    def __applyObserverModeChange(self):
        if not self.inputHandler.isStarted:
            self.delayCallback(0.0, self.__applyObserverModeChange)
            return
        else:
            vehicle = self.getVehicleAttached()
            if vehicle is None and self.inputHandler.ctrlModeName not in _STRATEGIC_VIEW:
                self.delayCallback(0.0, self.__applyObserverModeChange)
                return
            self.stopCallback(self.__applyObserverModeChange)
            self.inputHandler.onVehicleControlModeChanged(None)
            if vehicle is not None:
                if self.isObserverFPV:
                    self.guiSessionProvider.stopVehicleVisual(vehicle.id, False)
                else:
                    self.guiSessionProvider.startVehicleVisual(vehicle, True)
            if self.observerSeesAll():
                self.guiSessionProvider.shared.equipments.updateMapCase()
            else:
                self.updateObservedVehicleData()
            return

    def __setObserverFPVControlMode(self, observerFPVControlMode):
        self.__observerFPVControlMode = observerFPVControlMode
        if self.isObserver():
            eMode = CTRL_MODES[observerFPVControlMode]
            if self.isObserverFPV:
                if eMode == CTRL_MODE_NAME.MAP_CASE_ARCADE:
                    return
                if eMode not in _OBSERVABLE_VIEWS:
                    _logger.warning("AvatarObserver.set_observerFPVControlMode() requested control mode '%r' is not supported, switching out of FPV", eMode)
                    self.cell.switchObserverFPV(False)
                else:
                    self.__switchToObservedControlMode()

    def __switchToObservedControlMode(self):
        eMode = CTRL_MODES[self.__observerFPVControlMode]
        _logger.info('AvatarObserver.__switchToObservedControlMode(): %r, %r', self.__observerFPVControlMode, eMode)
        if self.observerSeesAll() and self.inputHandler.ctrlModeName == eMode:
            return
        else:
            filteredValue = None
            if eMode in _OBSERVABLE_VIEWS:
                filteredValue = self.filter.getVector3(BigWorld.AvatarSubfilters.CAMERA_SHOT_POINT, BigWorld.serverTime())
            if filteredValue is None or filteredValue == Math.Vector3(0, 0, 0):
                _logger.info('AvatarObserver.__switchToObservedControlMode(): no filtered value yet.Rescheduling switch... %r', filteredValue)
                self.delayCallback(0.0, self.__switchToObservedControlMode)
                return
            self.inputHandler.onVehicleControlModeChanged(eMode)
            return

    def set_remoteCamera(self, _):
        self.setRemoteCamera(self.remoteCamera)

    def observerSeesAll(self):
        return self.guiSessionProvider.getCtx().isObserver(self.playerVehicleID) and BONUS_CAPS.checkAny(self.arenaBonusType, BONUS_CAPS.OBSERVER_SEES_ALL)

    def isBecomeObserverAfterDeath(self):
        return BONUS_CAPS.checkAny(self.arenaBonusType, BONUS_CAPS.BECOME_AN_OBSERVER_AFTER_DEATH)

    def isFollowWinner(self):
        return BONUS_CAPS.checkAny(self.arenaBonusType, BONUS_CAPS.FOLLOW_WINNER)

    def __resetFPVModeSwitching(self):
        self.__isFPVModeSwitching = False
