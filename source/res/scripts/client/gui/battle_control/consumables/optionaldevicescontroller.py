# Embedded file name: scripts/client/gui/battle_control/consumables/OptionalDevicesController.py
import Event
from PlayerEvents import g_playerEvents
from constants import ARENA_PERIOD
from items import vehicles
import nations

class OptionalDevicesController(object):
    __slots__ = ('__eManager', '__optionalDevices', 'onOptionalDeviceAdded', 'onOptionalDeviceUpdated')

    def __init__(self):
        super(OptionalDevicesController, self).__init__()
        self.__eManager = Event.EventManager()
        self.onOptionalDeviceAdded = Event.Event(self.__eManager)
        self.onOptionalDeviceUpdated = Event.Event(self.__eManager)
        self.__optionalDevices = {}
        g_playerEvents.onArenaPeriodChange += self.__pe_onArenaPeriodChange

    def __repr__(self):
        return 'OptionalDevicesController({0!r:s})'.format(self.__optionalDevices)

    def clear(self, leave = True):
        if leave:
            self.__eManager.clear()
            g_playerEvents.onArenaPeriodChange -= self.__pe_onArenaPeriodChange
        self.__optionalDevices.clear()

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

    def setOptionalDevice(self, deviceID, isOn):
        intCD = vehicles.makeIntCompactDescrByID('optionalDevice', nations.NONE_INDEX, deviceID)
        if deviceID in self.__optionalDevices:
            self.__optionalDevices[deviceID] = isOn
            self.onOptionalDeviceUpdated(intCD, isOn)
        else:
            self.__optionalDevices[deviceID] = isOn
            self.onOptionalDeviceAdded(intCD, self.getDescriptor(deviceID), isOn)

    def __pe_onArenaPeriodChange(self, period, *args):
        if period == ARENA_PERIOD.AFTERBATTLE:
            self.clear()


__all__ = ('OptionalDevicesController',)
