# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarObserver.py
import BigWorld
import Vehicle
import Math
from collections import defaultdict
from AvatarInputHandler.aih_constants import CTRL_MODE_NAME, CTRL_MODES
from constants import AVATAR_SUBFILTERS, FILTER_INTERPOLATION_TYPE, VEHICLE_SETTING
from debug_utils import LOG_DEBUG_DEV, LOG_ERROR
from helpers.CallbackDelayer import CallbackDelayer
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

    def setEquipment(self, intCD, quantity, stage, timeRemaining):
        if not intCD:
            if len(self.__equipmentOrder) < 3:
                self.__equipmentOrder.append(0)
                self.__equipment[0] = (0, 0, 0)
            return
        if intCD not in self.__equipment:
            self.__equipmentOrder.append(intCD)
        self.__equipment[intCD] = (quantity, stage, timeRemaining)

    def setOptionalDevice(self, deviceID, isOn):
        if deviceID not in self.__optionalDevices:
            self.__optionalDevicesOrder.append(deviceID)
        self.__optionalDevices[deviceID] = isOn


class AvatarObserver(CallbackDelayer):
    observedVehicleID = property(lambda self: self.__observedVehicleID)
    observedVehicleData = property(lambda self: self.__observedVehicleData)

    def __init__(self):
        LOG_DEBUG_DEV('client AvatarObserver.init')
        CallbackDelayer.__init__(self)
        self.__observedVehicleID = None
        self.__observedVehicleData = defaultdict(ObservedVehicleData)
        return

    def onBecomePlayer(self):
        LOG_DEBUG_DEV('AvatarObserver.onBecomePlayer')
        self.cell.switchObserverFPV(False)

    def onBecomeNonPlayer(self):
        CallbackDelayer.destroy(self)

    def onEnterWorld(self):
        LOG_DEBUG_DEV('AvatarObserver.onEnterWorld')

        def getFilterMethod(methodName):
            method = getattr(self.filter, methodName, None)
            if not method:
                LOG_ERROR('Avatar.onEnterWorld: filter doesnt have method %s' % methodName)
                return lambda : None
            else:
                return method

        self.__filterSyncVector3 = getFilterMethod('syncVector3')
        self.__filterGetVector3 = getFilterMethod('getVector3')
        self.__filterResetVector3 = getFilterMethod('resetVector3')
        self.__filterSetInterpolationType = getFilterMethod('setInterpolationType')
        self.__setInterpolationTypes()
        self.__resetArcadeCameraData()
        self.__resetSniperCameraData()
        self.__resetStrategicCameraData()

    def onVehicleChanged(self):
        LOG_DEBUG_DEV('Avatar vehicle has changed to %s' % self.vehicle)
        if self.vehicle is not None:
            typeofveh = 'observed' if self.__observedVehicleID == self.vehicle.id else 'players'
            LOG_DEBUG_DEV('Vehicle ID is ' + str(self.vehicle.id) + ' and is ' + typeofveh)
            for v in BigWorld.entities.values():
                if isinstance(v, Vehicle.Vehicle):
                    if self.vehicle is v:
                        v.subscribeToCameraChanged()
                    else:
                        v.unsubscribeFromCameraChanged()

        if self.isObserver() and self.vehicle is not None and self.__observedVehicleID != self.vehicle.id:
            self.__observedVehicleID = self.vehicle.id
            self.guiSessionProvider.getArenaDP().switchCurrentTeam(self.vehicle.publicInfo['team'])
            extraData = self.observedVehicleData[self.__observedVehicleID]
            extraData.gunSettings = self.vehicle.typeDescriptor.gun
            self.inputHandler.setObservedVehicle(self.__observedVehicleID)
            if self.gunRotator is not None:
                self.gunRotator.start()
            self.updateObservedVehicleData()
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
                LOG_DEBUG_DEV('AvatarObserver.vehicle_onEnterWorld', vehicle.id)
                extraData = self.observedVehicleData[self.__observedVehicleID]
                extraData.gunSettings = vehicle.typeDescriptor.gun

    def updateVehicleGunReloadTime(self, vehicleID, timeLeft, baseTime):
        if self.isObserver():
            self.observedVehicleData[vehicleID].setReload(timeLeft, baseTime)

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
                else:
                    return vehicle.matrix
        return

    def getObservedVehicleStabilisedMatrix(self):
        player = BigWorld.player()
        if player.isObserver():
            vehicle = player.getVehicleAttached()
            if vehicle is not None:
                if isinstance(vehicle.filter, BigWorld.WGVehicleFilter):
                    return vehicle.filter.stabilisedMatrix
                else:
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

    def processObservedVehicleEquipments(self, vehicleID, compactDescr, quantity, stage, timeRemaining):
        if self.isObserver():
            self.observedVehicleData[vehicleID].setEquipment(compactDescr, quantity, stage, timeRemaining)

    def set_isObserverFPV(self, prev):
        LOG_DEBUG_DEV('Avatar::set_isObserverFPV', self.isObserverFPV)
        self.__applyObserverModeChange()

    def __applyObserverModeChange(self):
        if self.vehicle is None and self.inputHandler.ctrlModeName not in _STRATEGIC_VIEW:
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
            LOG_DEBUG_DEV('Avatar::set_observerFPVControlMode', eMode)
            if eMode == CTRL_MODE_NAME.ARCADE:
                self.__resetArcadeCameraData()
            elif eMode == CTRL_MODE_NAME.SNIPER:
                self.__resetSniperCameraData()
            elif eMode == CTRL_MODE_NAME.STRATEGIC:
                self.__resetStrategicCameraData()
            elif eMode == CTRL_MODE_NAME.ARTY:
                self.__resetArtyCameraData()
            if self.isObserverFPV:
                if eMode not in (CTRL_MODE_NAME.ARCADE, CTRL_MODE_NAME.SNIPER) + _STRATEGIC_VIEW:
                    LOG_DEBUG_DEV("Avatar::set_observerFPVControlMode requested control mode '{0}' is not supported, switching out of FPV".format(eMode))
                    self.cell.switchObserverFPV(False)
                else:
                    self.__switchToObservedControlMode()
        return

    def __switchToObservedControlMode(self):
        eMode = CTRL_MODES[self.observerFPVControlMode]
        LOG_DEBUG_DEV('Avatar::__switchToObservedControlMode: ', self.observerFPVControlMode, eMode)
        filteredValue = None
        time = BigWorld.serverTime()
        if eMode == CTRL_MODE_NAME.ARCADE:
            filteredValue = self.__filterGetVector3(AVATAR_SUBFILTERS.CAMERA_ARCADE_REL_TRANSLATION, time)
        elif eMode == CTRL_MODE_NAME.SNIPER:
            filteredValue = self.__filterGetVector3(AVATAR_SUBFILTERS.CAMERA_SNIPER_ROTATION, time)
        elif eMode == CTRL_MODE_NAME.STRATEGIC:
            filteredValue = self.__filterGetVector3(AVATAR_SUBFILTERS.CAMERA_STRATEGIC_SHOT_POINT, time)
        elif eMode == CTRL_MODE_NAME.ARTY:
            filteredValue = self.__filterGetVector3(AVATAR_SUBFILTERS.CAMERA_ARTY_SHOT_POINT, time)
        if filteredValue is None or filteredValue == Math.Vector3(0, 0, 0):
            LOG_DEBUG_DEV('Avatar.__switchToObservedControlMode: no filtered value yet, rescheduling switch')
            BigWorld.callback(0.0, self.__switchToObservedControlMode)
            return
        else:
            self.inputHandler.onVehicleControlModeChanged(eMode)
            return

    def __setInterpolationTypes(self):
        if self.isObserver():
            self.__filterSetInterpolationType(AVATAR_SUBFILTERS.CAMERA_ARCADE_REL_TRANSLATION, FILTER_INTERPOLATION_TYPE.SLERP_OF_CARTESIAN)
            self.__filterSetInterpolationType(AVATAR_SUBFILTERS.CAMERA_ARCADE_SHOT_POINT, FILTER_INTERPOLATION_TYPE.SLERP_OF_CARTESIAN)
            self.__filterSetInterpolationType(AVATAR_SUBFILTERS.CAMERA_SNIPER_ROTATION, FILTER_INTERPOLATION_TYPE.ANGLE_RADIANS)
            self.__filterSetInterpolationType(AVATAR_SUBFILTERS.CAMERA_STRATEGIC_SHOT_POINT, FILTER_INTERPOLATION_TYPE.LINEAR)
            self.__filterSetInterpolationType(AVATAR_SUBFILTERS.CAMERA_ARTY_SHOT_POINT, FILTER_INTERPOLATION_TYPE.LINEAR)
            self.__filterSetInterpolationType(AVATAR_SUBFILTERS.CAMERA_ARTY_TRANSLATION, FILTER_INTERPOLATION_TYPE.SLERP_OF_CARTESIAN)
            self.__filterSetInterpolationType(AVATAR_SUBFILTERS.CAMERA_ARTY_ROTATION, FILTER_INTERPOLATION_TYPE.ANGLE_RADIANS)

    def __resetArcadeCameraData(self):
        if self.isObserver():
            self.__filterResetVector3(AVATAR_SUBFILTERS.CAMERA_ARCADE_REL_TRANSLATION)
            self.__filterResetVector3(AVATAR_SUBFILTERS.CAMERA_ARCADE_SHOT_POINT)

    def __resetSniperCameraData(self):
        if self.isObserver():
            self.__filterResetVector3(AVATAR_SUBFILTERS.CAMERA_SNIPER_ROTATION)

    def __resetStrategicCameraData(self):
        if self.isObserver():
            self.__filterResetVector3(AVATAR_SUBFILTERS.CAMERA_STRATEGIC_SHOT_POINT)

    def __resetArtyCameraData(self):
        if self.isObserver():
            self.__filterResetVector3(AVATAR_SUBFILTERS.CAMERA_ARTY_SHOT_POINT)
            self.__filterResetVector3(AVATAR_SUBFILTERS.CAMERA_ARTY_TRANSLATION)
            self.__filterResetVector3(AVATAR_SUBFILTERS.CAMERA_ARTY_ROTATION)

    def set_remoteCameraArcade(self, prev):
        if self.inWorld:
            self.__filterSyncVector3(AVATAR_SUBFILTERS.CAMERA_ARCADE_REL_TRANSLATION, self.remoteCameraArcade.relTranslation, self.remoteCameraArcade.time)
            self.__filterSyncVector3(AVATAR_SUBFILTERS.CAMERA_ARCADE_SHOT_POINT, self.remoteCameraArcade.shotPoint, self.remoteCameraArcade.time)

    def set_remoteCameraSniper(self, prev):
        if self.inWorld:
            self.__filterSyncVector3(AVATAR_SUBFILTERS.CAMERA_SNIPER_ROTATION, self.remoteCameraSniper.camMatrixRotation, self.remoteCameraSniper.time)

    def set_remoteCameraStrategic(self, prev):
        if self.inWorld:
            self.__filterSyncVector3(AVATAR_SUBFILTERS.CAMERA_STRATEGIC_SHOT_POINT, self.remoteCameraStrategic.shotPoint, self.remoteCameraStrategic.time)

    def set_remoteCameraArty(self, prev):
        if self.inWorld:
            self.__filterSyncVector3(AVATAR_SUBFILTERS.CAMERA_ARTY_SHOT_POINT, self.remoteCameraArty.shotPoint, self.remoteCameraArty.time)
            self.__filterSyncVector3(AVATAR_SUBFILTERS.CAMERA_ARTY_TRANSLATION, self.remoteCameraArty.translation, self.remoteCameraArty.time)
            self.__filterSyncVector3(AVATAR_SUBFILTERS.CAMERA_ARTY_ROTATION, self.remoteCameraArty.rotation, self.remoteCameraArty.time)
