# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/consumables/opt_devices_ctrl.py
import Event
import SoundGroups
import nations
from PlayerEvents import g_playerEvents
from constants import ARENA_PERIOD
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.controllers.interfaces import IBattleController
from items import vehicles
__all__ = ('OptionalDevicesController',)

def _makeIntCD(deviceID):
    return vehicles.makeIntCompactDescrByID('optionalDevice', nations.NONE_INDEX, deviceID)


class DevicesSound(object):
    _eventsMap = {6: ('camo_net_start', 'camo_net_stop'),
     4: ('stereo_trumpet_start', 'stereo_trumpet_stop')}
    _enabled = False

    @staticmethod
    def playSound(deviceID, isOn):
        if DevicesSound._enabled:
            events = DevicesSound._eventsMap.get(deviceID, None)
            if events is not None:
                SoundGroups.g_instance.playSound2D(events[0 if isOn else 1])
        return


class OptionalDevicesController(IBattleController):
    __slots__ = ('__eManager', '__optionalDevices', '__order', 'onOptionalDeviceAdded', 'onOptionalDeviceUpdated')

    def __init__(self):
        super(OptionalDevicesController, self).__init__()
        self.__eManager = Event.EventManager()
        self.onOptionalDeviceAdded = Event.Event(self.__eManager)
        self.onOptionalDeviceUpdated = Event.Event(self.__eManager)
        self.__optionalDevices = {}
        self.__order = []
        g_playerEvents.onArenaPeriodChange += self.__pe_onArenaPeriodChange

    def __repr__(self):
        return 'OptionalDevicesController({0!r:s})'.format(self.__optionalDevices)

    def getControllerID(self):
        return BATTLE_CTRL_ID.OPTIONAL_DEVICES

    def startControl(self, *args):
        pass

    def stopControl(self):
        self.clear(leave=True)

    def clear(self, leave=True):
        if leave:
            self.__eManager.clear()
            g_playerEvents.onArenaPeriodChange -= self.__pe_onArenaPeriodChange
        self.__optionalDevices.clear()
        self.__order = []

    def isOptionalDeviceOn(self, deviceID):
        isOn = False
        if deviceID in self.__optionalDevices:
            isOn = self.__optionalDevices[deviceID]
        return isOn

    def isOptionalDeviceOnByCD(self, intCD):
        itemID = vehicles.parseIntCompactDescr(intCD)[-1]
        return self.isOptionalDeviceOn(itemID)

    def getDescriptor(self, deviceID):
        return vehicles.g_cache.optionalDevices()[deviceID]

    def getOrderedOptionalDevicesLayout(self):

        def getItem(deviceID):
            isOn = self.__optionalDevices[deviceID]
            return (_makeIntCD(deviceID), self.getDescriptor(deviceID), isOn)

        return map(getItem, self.__order)

    def setOptionalDevice(self, deviceID, isOn):
        intCD = _makeIntCD(deviceID)
        deviceIsOn = False
        if deviceID in self.__optionalDevices:
            deviceIsOn = self.__optionalDevices[deviceID]
            self.__optionalDevices[deviceID] = isOn
            self.onOptionalDeviceUpdated(intCD, isOn)
        else:
            self.__optionalDevices[deviceID] = isOn
            self.__order.append(deviceID)
            self.onOptionalDeviceAdded(intCD, self.getDescriptor(deviceID), isOn)
        if deviceIsOn != isOn:
            DevicesSound.playSound(deviceID, isOn)

    def __pe_onArenaPeriodChange(self, period, *args):
        if period == ARENA_PERIOD.AFTERBATTLE:
            self.clear()
        DevicesSound._enabled = period == ARENA_PERIOD.BATTLE
