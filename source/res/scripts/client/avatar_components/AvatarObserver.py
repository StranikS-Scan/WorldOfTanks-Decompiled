# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/avatar_components/AvatarObserver.py
from collections import defaultdict
import logging
import BigWorld
import Math
from aih_constants import CTRL_MODE_NAME, CTRL_MODES
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as BONUS_CAPS
from AvatarInputHandler.subfilters_constants import AVATAR_SUBFILTERS, FILTER_INTERPOLATION_TYPE
from helpers.CallbackDelayer import CallbackDelayer
from soft_exception import SoftException
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

    def __init__(self):
        CallbackDelayer.__init__(self)
        self.__observedVehicleID = None
        self.__observedVehicleData = defaultdict(ObservedVehicleData)
        self.__isFPVModeSwitching = False
        return

    def switchObserverFPV(self):
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

        def getFilterMethod(methodName):
            method = getattr(self.filter, methodName, None)
            if method is None:
                raise SoftException('AvatarObserver.onEnterWorld(): filter does not have method', methodName)
            return method

        self.__filterSyncVector3 = getFilterMethod('syncVector3')
        self.__filterGetVector3 = getFilterMethod('getVector3')
        self.__filterResetVector3 = getFilterMethod('resetVector3')
        self.__filterSetInterpolationType = getFilterMethod('setInterpolationType')
        if self.isObserver():
            self.__filterSetInterpolationType(AVATAR_SUBFILTERS.CAMERA_SHOT_POINT, FILTER_INTERPOLATION_TYPE.LINEAR)
            self.__filterResetVector3(AVATAR_SUBFILTERS.CAMERA_SHOT_POINT)

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
                self.inputHandler.setObservedVehicle(self.__observedVehicleID)
                if self.gunRotator is not None:
                    self.gunRotator.start()
                self.updateObservedVehicleData()
                self.vehicle.set_dotEffect()
                if not self.guiSessionProvider.shared.vehicleState.isInPostmortem:
                    if hasattr(self.vehicle.filter, 'enableStabilisedMatrix'):
                        self.vehicle.filter.enableStabilisedMatrix(True)
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
        return None if vehicle is None or not vehicle.inWorld or not vehicle.isStarted or vehicle.isDestroyed else vehicle

    def clearObservedVehicleID(self):
        self.__observedVehicleID = None
        return

    def getVehicleDescriptor(self):
        descr = self.vehicleTypeDescriptor
        if self.isObserver() and self.getVehicleAttached() is not None:
            descr = self.getVehicleAttached().typeDescriptor
        return descr

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

    def set_observerFPVControlMode(self, prev):
        if self.isObserver() is not None:
            eMode = CTRL_MODES[self.observerFPVControlMode]
            if self.isObserverFPV:
                if eMode == CTRL_MODE_NAME.MAP_CASE_ARCADE:
                    return
                if eMode not in _OBSERVABLE_VIEWS:
                    _logger.debug("AvatarObserver.set_observerFPVControlMode() requested control mode '%r' is not supported, switching out of FPV", eMode)
                    self.cell.switchObserverFPV(False)
                else:
                    self.__switchToObservedControlMode()
        return

    def __switchToObservedControlMode(self):
        eMode = CTRL_MODES[self.observerFPVControlMode]
        _logger.debug('AvatarObserver.__switchToObservedControlMode(): %r, %r', self.observerFPVControlMode, eMode)
        if self.observerSeesAll() and self.inputHandler.ctrlModeName == eMode:
            return
        else:
            filteredValue = None
            time = BigWorld.serverTime()
            if eMode in _OBSERVABLE_VIEWS:
                filteredValue = self.__filterGetVector3(AVATAR_SUBFILTERS.CAMERA_SHOT_POINT, time)
            if filteredValue is None or filteredValue == Math.Vector3(0, 0, 0):
                _logger.debug('AvatarObserver.__switchToObservedControlMode(): no filtered value yet.Rescheduling switch... %r', filteredValue)
                self.delayCallback(0.0, self.__switchToObservedControlMode)
                return
            self.inputHandler.onVehicleControlModeChanged(eMode)
            return

    def set_remoteCamera(self, prev):
        if self.inWorld:
            self.__filterSyncVector3(AVATAR_SUBFILTERS.CAMERA_SHOT_POINT, self.remoteCamera.shotPoint, self.remoteCamera.time)

    def observerSeesAll(self):
        return self.guiSessionProvider.getCtx().isObserver(self.playerVehicleID) and BONUS_CAPS.checkAny(self.arenaBonusType, BONUS_CAPS.OBSERVER_SEES_ALL)

    def isFollowWinner(self):
        return BONUS_CAPS.checkAny(self.arenaBonusType, BONUS_CAPS.FOLLOW_WINNER)

    def __resetFPVModeSwitching(self):
        self.__isFPVModeSwitching = False
