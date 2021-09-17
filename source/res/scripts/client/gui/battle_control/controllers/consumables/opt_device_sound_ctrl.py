# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/consumables/opt_device_sound_ctrl.py
from functools import partial
import BigWorld
import Math
import SoundGroups
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
_INIT_OPT_DEVICE_EVENTS = {'improvedVentilation': ('cons_ventilation_start', 'cons_ventilation_stop'),
 'additionalInvisibilityDevice': ('cons_tracks_start', 'cons_tracks_stop'),
 'grousers': ('cons_grousers_start', 'cons_grousers_stop'),
 'antifragmentationLining': ('cons_spall_liner_start', 'cons_spall_liner_stop')}

class OptDeviceSoundController(object):
    __slots__ = ('__playerOptDevices', '__stopSoundEvents', '__schedulerToolbox', '__vehicleStateUpdatedHandlers', '__radioCommunicationHelper')

    def __init__(self):
        self.__playerOptDevices = set()
        self.__stopSoundEvents = []
        self.__schedulerToolbox = _SchedulerToolboxSoundEvent()
        self.__radioCommunicationHelper = _ImprovedRadioCommunicationEvent()
        self.__vehicleStateUpdatedHandlers = {}

    def initDevices(self, devices):
        self.clear()
        for device in devices:
            if device is None:
                continue
            deviceName = device.groupName
            self.__playerOptDevices.add(deviceName)
            if deviceName in _INIT_OPT_DEVICE_EVENTS:
                startEvent, stopEvent = _INIT_OPT_DEVICE_EVENTS[deviceName]
                SoundGroups.g_instance.playSound2D(startEvent)
                if stopEvent is not None:
                    self.__stopSoundEvents.append(stopEvent)

        self.__vehicleStateUpdatedHandlers = {VEHICLE_VIEW_STATE.DEVICES: self.__updateDeviceState,
         VEHICLE_VIEW_STATE.REPAIRING: self.__updateRepairingDevice}
        return

    def vehicleStateUpdated(self, state, value):
        if state in self.__vehicleStateUpdatedHandlers:
            self.__vehicleStateUpdatedHandlers[state](*value)

    def startVehicleVisual(self, vProxy, isImmediate):
        self.__radioCommunicationHelper.startVehicleVisual(vProxy, isImmediate)

    def clear(self):
        self.__playStopSoundEvents()
        self.__playerOptDevices.clear()
        self.__schedulerToolbox.clear()
        self.__radioCommunicationHelper.clear()
        self.__vehicleStateUpdatedHandlers.clear()

    def playLightbulbEffect(self):
        if 'improvedRadioCommunication' in self.__playerOptDevices:
            SoundGroups.g_instance.playSound2D('cons_radio_interference')

    def needGunRammerEffect(self):
        return 'tankRammer' in self.__playerOptDevices

    def playEnemySightedEffect(self, targetID):
        position = Math.Vector3(BigWorld.entities[targetID].position)
        SoundGroups.g_instance.playCameraOriented('cons_radio_sighted_for_team', position)

    def onVehicleDetected(self, feedback):
        if 'improvedRadioCommunication' not in self.__playerOptDevices:
            return
        self.__radioCommunicationHelper.setSpotted(feedback.getTargetID())

    def __playStopSoundEvents(self):
        for stopEvent in self.__stopSoundEvents:
            SoundGroups.g_instance.playSound2D(stopEvent)

        self.__stopSoundEvents = []

    def __updateDeviceState(self, deviceName, deviceState, _=None):
        if 'improvedConfiguration' in self.__playerOptDevices:
            if deviceState == 'repaired':
                if self.__schedulerToolbox.isPlanned(deviceName):
                    self.__schedulerToolbox.delete(deviceName)
                    SoundGroups.g_instance.playSound2D('cons_toolbox_stop')
            elif deviceState == 'destroyed':
                self.__schedulerToolbox.delete(deviceName)
            elif deviceState == 'normal':
                if self.__schedulerToolbox.isPlanned(deviceName):
                    self.__schedulerToolbox.delete(deviceName)
                    SoundGroups.g_instance.playSound2D('cons_toolbox_stop')

    def __updateRepairingDevice(self, deviceName, progress, secondsLeft, isLimited):
        if 'improvedConfiguration' in self.__playerOptDevices:
            if not self.__schedulerToolbox.isPlanned(deviceName):
                self.__schedulerToolbox.playAfterSecond(deviceName, max(0.0, secondsLeft - 2.0))


class _ImprovedRadioCommunicationEvent(object):
    _TIME_DELTA = 1

    def __init__(self):
        self.__spottedVehicles = {}

    def setSpotted(self, vehicleID):
        vehicle = BigWorld.entities.get(vehicleID, None)
        if vehicle is not None:
            SoundGroups.g_instance.playCameraOriented('cons_radio_sighted_for_team', Math.Vector3(vehicle.position))
        else:
            self.__spottedVehicles[vehicleID] = BigWorld.time()
        return

    def startVehicleVisual(self, vProxy, isImmediate):
        if isImmediate and vProxy.id in self.__spottedVehicles:
            if abs(BigWorld.time() - self.__spottedVehicles[vProxy.id]) < self._TIME_DELTA:
                SoundGroups.g_instance.playCameraOriented('cons_radio_sighted_for_team', Math.Vector3(vProxy.position))
            del self.__spottedVehicles[vProxy.id]

    def clear(self):
        self.__spottedVehicles.clear()


class _SchedulerToolboxSoundEvent(object):
    _PLANNING_DELTA = 0.05

    def __init__(self):
        self.__repairDevices = {}

    def playAfterSecond(self, deviceName, second):
        self.delete(deviceName)
        if second < self._PLANNING_DELTA:
            self.__onPlay()
        else:
            self.__repairDevices[deviceName] = BigWorld.callback(second, partial(self.__onPlay, deviceName=deviceName))

    def clear(self):
        for plannedCallbackID in self.__repairDevices.values():
            if plannedCallbackID is not None:
                BigWorld.cancelCallback(plannedCallbackID)

        self.__repairDevices = {}
        return

    def delete(self, deviceName):
        plannedCallbackID = self.__repairDevices.pop(deviceName, None)
        if plannedCallbackID is not None:
            BigWorld.cancelCallback(plannedCallbackID)
        return

    def isPlanned(self, deviceName):
        return deviceName in self.__repairDevices

    def __onPlay(self, deviceName=None):
        if deviceName is not None:
            self.__repairDevices[deviceName] = None
        SoundGroups.g_instance.playSound2D('cons_toolbox_start')
        return
