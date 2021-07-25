# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/consumables/opt_devices_ctrl.py
import Event
from PlayerEvents import g_playerEvents
from constants import ARENA_PERIOD
from gui.battle_control import vehicle_getter
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.controllers.consumables.opt_device_in_battle import createOptDeviceInBattle, DevicesSound
from gui.battle_control.controllers.consumables.opt_device_sound_ctrl import OptDeviceSoundController
from gui.battle_control.controllers.interfaces import IBattleController
from items import vehicles
__all__ = ('OptionalDevicesController',)

class OptionalDevicesController(IBattleController):
    __slots__ = ('__eManager', '__optionalDevices', '__order', '__soundManager', '__sessionProvider', '__optionalDevicesInDescriptor', 'onOptionalDeviceAdded', 'onOptionalDeviceUpdated', 'onOptionalDevicesCleared', 'onDescriptorDevicesChanged')

    def __init__(self, setup):
        super(OptionalDevicesController, self).__init__()
        self.__eManager = Event.EventManager()
        self.onOptionalDeviceAdded = Event.Event(self.__eManager)
        self.onOptionalDeviceUpdated = Event.Event(self.__eManager)
        self.onOptionalDevicesCleared = Event.Event(self.__eManager)
        self.onDescriptorDevicesChanged = Event.Event(self.__eManager)
        self.__optionalDevices = {}
        self.__soundManager = OptDeviceSoundController()
        self.__sessionProvider = setup.sessionProvider
        self.__order = []
        self.__optionalDevicesInDescriptor = []

    def __repr__(self):
        return 'OptionalDevicesController({0!r:s})'.format(self.__optionalDevices)

    def getControllerID(self):
        return BATTLE_CTRL_ID.OPTIONAL_DEVICES

    def startControl(self, *args):
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange
        self.__sessionProvider.onBattleSessionStart += self.__onBattleSessionStart
        self.__sessionProvider.onBattleSessionStop += self.__onBattleSessionStop

    def stopControl(self):
        self.clear(leave=True)

    @property
    def soundManager(self):
        return self.__soundManager

    def clear(self, leave=True):
        if leave:
            if self.__sessionProvider is not None:
                self.__sessionProvider.onBattleSessionStart -= self.__onBattleSessionStart
                self.__sessionProvider.onBattleSessionStop -= self.__onBattleSessionStop
            self.__sessionProvider = None
            self.__eManager.clear()
            g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        self.__soundManager.clear()
        self.__optionalDevices.clear()
        self.__order = []
        self.__optionalDevicesInDescriptor = []
        if not leave:
            self.onOptionalDevicesCleared()
        return

    def reset(self):
        self.__optionalDevices.clear()
        self.__order = []
        self.onOptionalDevicesCleared()

    def getOptDeviceInBattle(self, deviceID):
        return self.__optionalDevices.get(deviceID)

    def isOptionalDeviceOn(self, deviceID):
        optDeviceInBattle = self.__optionalDevices.get(deviceID, None)
        return bool(optDeviceInBattle.getStatus()) if optDeviceInBattle is not None else False

    def isOptionalDeviceOnByCD(self, intCD):
        itemID = vehicles.parseIntCompactDescr(intCD)[-1]
        return self.isOptionalDeviceOn(itemID)

    def getOrderedOptionalDevicesLayout(self):

        def getItem(deviceID):
            return self.__optionalDevices[deviceID]

        return map(getItem, self.__order)

    def setOptionalDevice(self, deviceID, isOn):
        optDeviceInBattle = self.__optionalDevices.get(deviceID, None)
        if optDeviceInBattle is not None:
            optDeviceInBattle.updateStatus(isOn)
            self.onOptionalDeviceUpdated(optDeviceInBattle)
        else:
            optDeviceInBattle = createOptDeviceInBattle(deviceID, isOn)
            self.__optionalDevices[deviceID] = optDeviceInBattle
            self.__order.append(deviceID)
            self.onOptionalDeviceAdded(optDeviceInBattle)
        optDeviceInBattle.apply()
        return

    def startVehicleVisual(self, vProxy, isImmediate):
        self.soundManager.startVehicleVisual(vProxy, isImmediate)

    def __onArenaPeriodChange(self, period, *_):
        if period == ARENA_PERIOD.AFTERBATTLE:
            self.clear()
        DevicesSound.arenaPeriodChange(period)

    def __onBattleSessionStart(self):
        if self.__sessionProvider is None:
            return
        else:
            arena = self.__sessionProvider.arenaVisitor.getArenaSubscription()
            if arena is not None:
                arena.onVehicleUpdated += self.__onVehicleInfoUpdated
            self.__sessionProvider.shared.vehicleState.onVehicleStateUpdated += self.__onVehicleStateUpdated
            self.__sessionProvider.shared.vehicleState.onVehicleControlling += self.__onVehicleChanged
            self.__sessionProvider.shared.feedback.onVehicleDetected += self.soundManager.onVehicleDetected
            return

    def __onBattleSessionStop(self):
        if self.__sessionProvider is None:
            return
        else:
            arena = self.__sessionProvider.arenaVisitor.getArenaSubscription()
            if arena is not None:
                arena.onVehicleUpdated -= self.__onVehicleInfoUpdated
            self.__sessionProvider.shared.vehicleState.onVehicleStateUpdated -= self.__onVehicleStateUpdated
            self.__sessionProvider.shared.vehicleState.onVehicleControlling -= self.__onVehicleChanged
            self.__sessionProvider.shared.feedback.onVehicleDetected -= self.soundManager.onVehicleDetected
            return

    def __onVehicleChanged(self, vehicle):
        if vehicle.isPlayerVehicle and vehicle.isAlive():
            self.__optionalDevicesInDescriptor = None
            self.__invalidateOptionalDevices(vehicle.id)
        return

    def __onVehicleStateUpdated(self, state, value):
        self.__soundManager.vehicleStateUpdated(state, value)

    def __onVehicleInfoUpdated(self, vehicleID):
        vehicle = self.__sessionProvider.shared.vehicleState.getControllingVehicle()
        if vehicle is not None and vehicleID == vehicle.id and vehicle.isPlayerVehicle and vehicle.isAlive():
            self.__invalidateOptionalDevices(vehicleID)
        return

    def __invalidateOptionalDevices(self, vehicleID):
        optionalDevices = vehicle_getter.getOptionalDevicesByVehID(vehicleID)
        optionalDevicesInDescriptor = [ (d.id[1] if d is not None else None) for d in optionalDevices ]
        if optionalDevicesInDescriptor != self.__optionalDevicesInDescriptor:
            self.__soundManager.initDevices(optionalDevices)
            self.__optionalDevicesInDescriptor = optionalDevicesInDescriptor
            self.onDescriptorDevicesChanged(optionalDevices)
        return
