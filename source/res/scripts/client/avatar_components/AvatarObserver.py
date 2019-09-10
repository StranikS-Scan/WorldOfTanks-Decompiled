# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/avatar_components/AvatarObserver.py
from collections import defaultdict
import BigWorld
import Vehicle
import Math
from constants import VEHICLE_SETTING
from aih_constants import CTRL_MODE_NAME, CTRL_MODES
from AvatarInputHandler.subfilters_constants import AVATAR_SUBFILTERS, FILTER_INTERPOLATION_TYPE
from debug_utils import LOG_DEBUG_DEV
from helpers.CallbackDelayer import CallbackDelayer
from soft_exception import SoftException
_STRATEGIC_VIEW = (CTRL_MODE_NAME.STRATEGIC, CTRL_MODE_NAME.ARTY)

class ObservedVehicleData(CallbackDelayer):
    RELOAD_UPDATE_FREQUENCY = 1.0
    reloadTimeLeft = property(lambda self: self.__reloadTimeLeft)
    reloadBaseTime = property(lambda self: self.__reloadBaseTime)
    orderedAmmo = property(lambda self: [ (x,) + self.__ammo[x] for x in self.__ammoOrder ])
    orderedEquipment = property(lambda self: [ (x,) + self.__equipment[x] for x in self.__equipmentOrder ])
    orderedOptionalDevices = property(lambda self: [ (x, self.__optionalDevices[x]) for x in self.__optionalDevicesOrder ])

    def __init__(self):
        CallbackDelayer.__init__(self)
        self.dispAngle = 0
        self.gunSettings = {}
        self.currentShellCD = None
        self.nextShellCD = None
        self.__reloadTimeLeft = 0
        self.__reloadBaseTime = 0
        self.__ammo = {}
        self.__ammoOrder = []
        self.__equipment = {}
        self.__equipmentOrder = []
        self.__optionalDevices = {}
        self.__optionalDevicesOrder = []
        return

    def setReload(self, timeLeft, baseTime):
        self.__reloadTimeLeft = timeLeft
        self.__reloadBaseTime = baseTime
        if self.__reloadTimeLeft > 0:
            self.delayCallback(self.RELOAD_UPDATE_FREQUENCY, self.updateReloadTime)

    def updateReloadTime(self):
        self.__reloadTimeLeft = max(0, self.__reloadTimeLeft - self.RELOAD_UPDATE_FREQUENCY)
        return self.RELOAD_UPDATE_FREQUENCY if self.__reloadTimeLeft > 0 else -1

    def setAmmo(self, intCD, quantity, quantityInClip):
        if intCD not in self.__ammo:
            self.__ammoOrder.append(intCD)
        self.__ammo[intCD] = (quantity, quantityInClip)

    def setEquipment(self, intCD, quantity, stage, timeRemaining, totalTime):
        if not intCD:
            if len(self.__equipmentOrder) < 3:
                self.__equipmentOrder.append(0)
                self.__equipment[0] = (0, 0, 0, 0)
            return
        if intCD not in self.__equipment:
            self.__equipmentOrder.append(intCD)
        self.__equipment[intCD] = (quantity,
         stage,
         timeRemaining,
         totalTime)

    def setOptionalDevice(self, deviceID, isOn):
        if deviceID not in self.__optionalDevices:
            self.__optionalDevicesOrder.append(deviceID)
        self.__optionalDevices[deviceID] = isOn


class AvatarObserver(CallbackDelayer):
    observedVehicleID = property(lambda self: self.__observedVehicleID)
    observedVehicleData = property(lambda self: self.__observedVehicleData)

    def __init__(self):
        CallbackDelayer.__init__(self)
        self.__observedVehicleID = None
        self.__observedVehicleData = defaultdict(ObservedVehicleData)
        return

    def onBecomePlayer(self):
        self.cell.switchObserverFPV(False)

    def onBecomeNonPlayer(self):
        CallbackDelayer.destroy(self)

    def handleKey(self, isDown, key, mods):
        pass

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

    def onVehicleChanged(self):
        LOG_DEBUG_DEV('Avatar vehicle has changed to %s' % self.vehicle)
        if self.vehicle is not None:
            typeofveh = 'observed' if self.__observedVehicleID == self.vehicle.id else 'players'
            LOG_DEBUG_DEV('Vehicle ID is ' + str(self.vehicle.id) + ' and is ' + typeofveh)
        if self.isObserver() and self.vehicle is not None and self.__observedVehicleID != self.vehicle.id:
            self.__observedVehicleID = self.vehicle.id
            self.guiSessionProvider.getArenaDP().switchCurrentTeam(self.vehicle.publicInfo['team'])
            extraData = self.observedVehicleData[self.__observedVehicleID]
            extraData.gunSettings = self.vehicle.typeDescriptor.gun
            self.inputHandler.setObservedVehicle(self.__observedVehicleID)
            if self.gunRotator is not None:
                self.gunRotator.start()
            self.updateObservedVehicleData()
            if hasattr(self.vehicle.filter, 'enableStabilisedMatrix'):
                self.vehicle.filter.enableStabilisedMatrix(True)
            BigWorld.target.exclude = self.vehicle
            for v in BigWorld.entities.values():
                if isinstance(v, Vehicle.Vehicle) and v.appearance is not None:
                    v.appearance.highlighter.setVehicleOwnership()
                    self.guiSessionProvider.stopVehicleVisual(v.id, False)
                    self.guiSessionProvider.startVehicleVisual(v, True)

        return

    def updateObservedVehicleData(self):
        if self.vehicle is not None:
            extraData = self.observedVehicleData[self.__observedVehicleID]
            if self.gunRotator is not None:
                turretYaw, gunPitch = self.vehicle.getAimParams()
                self.gunRotator.forceGunParams(turretYaw, gunPitch, extraData.dispAngle)
            self.guiSessionProvider.updateObservedVehicleData(self.__observedVehicleID, extraData)
            ammoCtrl = self.guiSessionProvider.shared.ammo
            shotIdx = ammoCtrl.getGunSettings().getShotIndex(extraData.currentShellCD)
            if shotIdx > -1:
                self.vehicle.typeDescriptor.activeGunShotIndex = shotIdx
        return

    def vehicle_onEnterWorld(self, vehicle):
        if vehicle.id != self.playerVehicleID:
            if self.isObserver() and vehicle.id == self.__observedVehicleID:
                extraData = self.observedVehicleData[self.__observedVehicleID]
                extraData.gunSettings = vehicle.typeDescriptor.gun

    def updateVehicleGunReloadTime(self, vehicleID, timeLeft, baseTime):
        if self.isObserver():
            self.observedVehicleData[vehicleID].setReload(timeLeft, baseTime)

    def updateVehicleClipReloadTime(self, vehicleID, timeLeft, baseTime, stunned):
        pass

    def updateVehicleOptionalDeviceStatus(self, vehicleID, deviceID, isOn):
        self.observedVehicleData[vehicleID].setOptionalDevice(deviceID, isOn)

    def updateVehicleSetting(self, vehicleID, code, value):
        if code == VEHICLE_SETTING.CURRENT_SHELLS:
            self.__observedVehicleData[vehicleID].currentShellCD = value
            return
        if code == VEHICLE_SETTING.NEXT_SHELLS:
            self.__observedVehicleData[vehicleID].nextShellCD = value
            return

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

    def getVehicleAttached(self):
        vehicle = self.vehicle
        if vehicle is None:
            vehicle = BigWorld.entity(self.__observedVehicleID if self.__observedVehicleID else self.playerVehicleID)
        return None if vehicle is None or not vehicle.inWorld or not vehicle.isStarted or vehicle.isDestroyed else vehicle

    def getVehicleDescriptor(self):
        descr = self.vehicleTypeDescriptor
        if self.isObserver() and self.getVehicleAttached() is not None:
            descr = self.getVehicleAttached().typeDescriptor
        return descr

    def processObservedVehicleAmmo(self, vehicleID, compactDescr, quantity, quantityInClip):
        if self.isObserver():
            self.observedVehicleData[vehicleID].setAmmo(compactDescr, quantity, quantityInClip)

    def processObservedVehicleEquipments(self, vehicleID, compactDescr, quantity, stage, timeRemaining, totalTime):
        if self.isObserver():
            self.observedVehicleData[vehicleID].setEquipment(compactDescr, quantity, stage, timeRemaining, totalTime)

    def set_isObserverFPV(self, prev):
        LOG_DEBUG_DEV('AvatarObserver.set_isObserverFPV()', self.isObserverFPV)
        self.__applyObserverModeChange()

    def __applyObserverModeChange(self):
        if not self.inputHandler.isStarted:
            self.delayCallback(0.0, self.__applyObserverModeChange)
            return
        elif self.vehicle is None and self.inputHandler.ctrlModeName not in _STRATEGIC_VIEW:
            self.delayCallback(0.0, self.__applyObserverModeChange)
            return
        else:
            self.stopCallback(self.__applyObserverModeChange)
            self.inputHandler.onVehicleControlModeChanged(None)
            vehicle = self.getVehicleAttached()
            if vehicle is not None:
                if self.isObserverFPV:
                    self.guiSessionProvider.stopVehicleVisual(vehicle.id, False)
                    self.updateObservedVehicleData()
                else:
                    self.guiSessionProvider.startVehicleVisual(vehicle, True)
            return

    def set_observerFPVControlMode(self, prev):
        if self.isObserver() is not None:
            eMode = CTRL_MODES[self.observerFPVControlMode]
            if self.isObserverFPV:
                if eMode not in (CTRL_MODE_NAME.ARCADE, CTRL_MODE_NAME.SNIPER) + _STRATEGIC_VIEW:
                    LOG_DEBUG_DEV("AvatarObserver.set_observerFPVControlMode() requested control mode '{0}' is not supported, switching out of FPV".format(eMode))
                    self.cell.switchObserverFPV(False)
                else:
                    self.__switchToObservedControlMode()
        return

    def __switchToObservedControlMode(self):
        eMode = CTRL_MODES[self.observerFPVControlMode]
        LOG_DEBUG_DEV('AvatarObserver.__switchToObservedControlMode():', self.observerFPVControlMode, eMode)
        filteredValue = None
        time = BigWorld.serverTime()
        if eMode in (CTRL_MODE_NAME.ARCADE, CTRL_MODE_NAME.SNIPER) + _STRATEGIC_VIEW:
            filteredValue = self.__filterGetVector3(AVATAR_SUBFILTERS.CAMERA_SHOT_POINT, time)
        if filteredValue is None or filteredValue == Math.Vector3(0, 0, 0):
            LOG_DEBUG_DEV('AvatarObserver.__switchToObservedControlMode(): no filtered value yet.Rescheduling switch...', filteredValue)
            self.delayCallback(0.0, self.__switchToObservedControlMode)
            return
        else:
            self.inputHandler.onVehicleControlModeChanged(eMode)
            return

    def set_remoteCamera(self, prev):
        if self.inWorld:
            self.__filterSyncVector3(AVATAR_SUBFILTERS.CAMERA_SHOT_POINT, self.remoteCamera.shotPoint, self.remoteCamera.time)
