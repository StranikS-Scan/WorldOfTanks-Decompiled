# Embedded file name: scripts/client/gui/battle_control/consumables/equipment_ctrl.py
from collections import namedtuple
import Event
from constants import VEHICLE_SETTING
from debug_utils import LOG_ERROR
from gui.battle_control import avatar_getter, vehicle_getter
from gui.battle_control.battle_constants import makeExtraName, VEHICLE_COMPLEX_ITEMS
from helpers import i18n
from items import vehicles
_ActivationError = namedtuple('_ActivationError', 'key ctx')

class _EquipmentItem(object):
    __slots__ = ('_tag', '_descriptor', '_quantity', '_timeRemaining')

    def __init__(self, descriptor, quantity, timeRemaining, tag = None):
        super(_EquipmentItem, self).__init__()
        self._tag = tag
        self._descriptor = descriptor
        self.update(quantity, timeRemaining)

    def __repr__(self):
        return '{0:>s}(id={1!r:s}, quantity = {2:n}, timeRemaining = {3:n})'.format(self.__class__.__name__, self._descriptor.id, self._quantity, self._timeRemaining)

    def getTag(self):
        return _getSupportedTag(self._descriptor)

    def isEntityRequired(self):
        return False

    def getEntitiesIterator(self, avatar = None):
        raise ValueError, 'Invokes getEntitiesIterator, than it is not required'

    def getGuiIterator(self, avatar = None):
        raise ValueError, 'Invokes getGuiIterator, than it is not required'

    def canActivate(self, entityName = None, avatar = None):
        if self._quantity <= 0 or self._timeRemaining > 0:
            result = False
        else:
            result = True
        return (result, None)

    def getActivationCode(self, entityName = None, avatar = None):
        return None

    def clear(self):
        self._descriptor = None
        self.update(0, 0)
        return

    def update(self, quantity, timeRemaining):
        self._quantity = quantity
        self._timeRemaining = timeRemaining

    def activate(self):
        pass

    def getDescriptor(self):
        return self._descriptor

    def getQuantity(self):
        return self._quantity

    def getTimeRemaining(self):
        return self._timeRemaining


class _AutoItem(_EquipmentItem):

    def canActivate(self, entityName = None, avatar = None):
        return (False, None)


class _TriggerItem(_EquipmentItem):

    def getActivationCode(self, entityName = None, avatar = None):
        flag = 1 if self._timeRemaining == 0 else 0
        return (flag << 16) + self._descriptor.id[1]


class _ExtinguisherItem(_EquipmentItem):
    __slots__ = ('_isActivated',)

    def __init__(self, descriptor, quantity, timeRemaining, tag = None):
        super(_ExtinguisherItem, self).__init__(descriptor, quantity, timeRemaining, tag)
        self._isActivated = timeRemaining > 0

    def update(self, quantity, timeRemaining):
        super(_ExtinguisherItem, self).update(quantity, timeRemaining)
        if timeRemaining == 0:
            self._isActivated = False

    def activate(self):
        self._isActivated = True

    def canActivate(self, entityName = None, avatar = None):
        result, error = super(_ExtinguisherItem, self).canActivate(entityName, avatar)
        if not result:
            return (result, error)
        elif not avatar_getter.isVehicleInFire(avatar):
            return (False, _ActivationError('extinguisherDoesNotActivated', {'name': self._descriptor.userString}))
        elif self._isActivated != 0:
            return (False, _ActivationError('equipmentAlreadyActivated', {'name': self._descriptor.userString}))
        else:
            return (True, None)

    def getActivationCode(self, entityName = None, avatar = None):
        return 65536 + self._descriptor.id[1]

    def changeSettingValue(self):
        self._isActivated = True


class _ExpandedItem(_EquipmentItem):

    def isEntityRequired(self):
        return not self._descriptor.repairAll

    def canActivate(self, entityName = None, avatar = None):
        result, error = super(_ExpandedItem, self).canActivate(entityName, avatar)
        if not result:
            return (result, error)
        else:
            deviceStates = avatar_getter.getVehicleDeviceStates(avatar)
            if not len(deviceStates):
                return (False, _ActivationError(self._getEntitiesAreSafeKey(), None))
            isRequired = self.isEntityRequired()
            if isRequired:
                if entityName is None:
                    return (False, None)
                if entityName not in deviceStates:
                    return (False, _ActivationError(self._getEntityIsSafeKey(), {'entity': self._getEntityUserString(entityName)}))
            return (True, None)

    def getActivationCode(self, entityName = None, avatar = None):
        if not self.isEntityRequired():
            return 65536 + self._descriptor.id[1]
        else:
            extrasDict = avatar_getter.getVehicleExtrasDict(avatar)
            if entityName is None:
                return
            extraName = makeExtraName(entityName)
            if extraName not in extrasDict:
                return
            return (extrasDict[extraName].index << 16) + self._descriptor.id[1]
            return

    def _getEntitiesAreSafeKey(self):
        return ''

    def _getEntityIsSafeKey(self):
        return ''

    def _getEntityUserString(self, entityName, avatar = None):
        extrasDict = avatar_getter.getVehicleExtrasDict(avatar)
        extraName = makeExtraName(entityName)
        if extraName in extrasDict:
            userString = extrasDict[extraName].deviceUserString
        else:
            userString = entityName
        return userString


class _MedKitItem(_ExpandedItem):

    def getEntitiesIterator(self, avatar = None):
        return vehicle_getter.TankmenStatesIterator(avatar_getter.getVehicleDeviceStates(avatar), avatar_getter.getVehicleTypeDescriptor(avatar))

    def getGuiIterator(self, avatar = None):
        for name, state in self.getEntitiesIterator(avatar):
            yield (name, name, state)

    def _getEntitiesAreSafeKey(self):
        return 'medkitAllTankmenAreSafe'

    def _getEntityIsSafeKey(self):
        return 'medkitTankmanIsSafe'


class _RepairKitItem(_ExpandedItem):

    def getEntitiesIterator(self, avatar = None):
        return vehicle_getter.VehicleDeviceStatesIterator(avatar_getter.getVehicleDeviceStates(avatar), avatar_getter.getVehicleTypeDescriptor(avatar))

    def getGuiIterator(self, avatar = None):
        return vehicle_getter.VehicleGUIItemStatesIterator(avatar_getter.getVehicleDeviceStates(avatar), avatar_getter.getVehicleTypeDescriptor(avatar))

    def _getEntitiesAreSafeKey(self):
        return 'repairkitAllDevicesAreNotDamaged'

    def _getEntityIsSafeKey(self):
        return 'repairkitDeviceIsNotDamaged'

    def _getEntityUserString(self, entityName, avatar = None):
        if entityName in VEHICLE_COMPLEX_ITEMS:
            return i18n.makeString('#ingame_gui:devices/{0}'.format(entityName))
        else:
            return super(_RepairKitItem, self)._getEntityUserString(entityName, avatar)


_EQUIPMENT_TAG_TO_ITEM = {'fuel': _AutoItem,
 'stimulator': _AutoItem,
 'trigger': _TriggerItem,
 'extinguisher': _ExtinguisherItem,
 'medkit': _MedKitItem,
 'repairkit': _RepairKitItem}

def _getSupportedTag(descriptor):
    keys = set(_EQUIPMENT_TAG_TO_ITEM.keys()) & descriptor.tags
    if len(keys) == 1:
        tag = keys.pop()
    else:
        tag = None
    return tag


class EquipmentsController(object):
    __slots__ = ('__eManager', '__equipments', 'onEquipmentAdded', 'onEquipmentUpdated')

    def __init__(self):
        super(EquipmentsController, self).__init__()
        self.__eManager = Event.EventManager()
        self.onEquipmentAdded = Event.Event(self.__eManager)
        self.onEquipmentUpdated = Event.Event(self.__eManager)
        self.__equipments = {}

    def __repr__(self):
        return 'EquipmentsController({0!r:s})'.format(self.__equipments)

    @classmethod
    def createItem(cls, descriptor, quantity, timeRemaining):
        tag = _getSupportedTag(descriptor)
        if tag:
            item = _EQUIPMENT_TAG_TO_ITEM[tag](descriptor, quantity, timeRemaining, tag)
        else:
            item = _EquipmentItem(descriptor, quantity, timeRemaining)
        return item

    def clear(self):
        self.__eManager.clear()
        while len(self.__equipments):
            _, item = self.__equipments.popitem()
            item.clear()

    def getEquipment(self, intCD):
        try:
            item = self.__equipments[intCD]
        except KeyError:
            LOG_ERROR('Equipment is not found.', intCD)
            item = None

        return item

    def setEquipment(self, intCD, quantity, timeRemaining):
        if not intCD:
            self.onEquipmentAdded(intCD, None)
            return
        else:
            if intCD in self.__equipments:
                item = self.__equipments[intCD]
                item.update(quantity, timeRemaining)
                self.onEquipmentUpdated(intCD, quantity, timeRemaining)
            else:
                descriptor = vehicles.getDictDescr(intCD)
                item = self.createItem(descriptor, quantity, timeRemaining)
                self.__equipments[intCD] = item
                self.onEquipmentAdded(intCD, item)
            return

    def getActivationCode(self, intCD, entityName = None, avatar = None):
        code = None
        item = self.getEquipment(intCD)
        if item:
            code = item.getActivationCode(entityName, avatar)
        return code

    def canActivate(self, intCD, entityName = None, avatar = None):
        result, error = False, None
        item = self.getEquipment(intCD)
        if item:
            result, error = item.canActivate(entityName, avatar)
        return (result, error)

    def changeSetting(self, intCD, entityName = None, avatar = None):
        if not avatar_getter.isVehicleAlive(avatar):
            return (False, None)
        else:
            result, error = False, None
            item = self.getEquipment(intCD)
            if item:
                result, error = self.__doChangeSetting(item, entityName, avatar)
            return (result, error)

    def changeSettingByTag(self, tag, entityName = None, avatar = None):
        if not avatar_getter.isVehicleAlive(avatar):
            return (False, None)
        else:
            result, error = True, None
            for intCD, item in self.__equipments.iteritems():
                if item.getTag() == tag:
                    result, error = self.__doChangeSetting(item, entityName, avatar)
                    break

            return (result, error)

    def __doChangeSetting(self, item, entityName = None, avatar = None):
        result, error = item.canActivate(entityName, avatar)
        if result:
            value = item.getActivationCode(entityName, avatar)
            if avatar_getter.isPlayerOnArena(avatar):
                avatar_getter.changeVehicleSetting(VEHICLE_SETTING.ACTIVATE_EQUIPMENT, value, avatar)
                item.activate()
        return (result, error)


class _ReplayItem(_EquipmentItem):

    def getEntitiesIterator(self, avatar = None):
        return []

    def getGuiIterator(self, avatar = None):
        return []

    def canActivate(self, entityName = None, avatar = None):
        return (False, None)


class EquipmentsReplayPlayer(EquipmentsController):

    @classmethod
    def createItem(cls, descriptor, quantity, timeRemaining):
        return _ReplayItem(descriptor, quantity, timeRemaining, _getSupportedTag(descriptor))

    def getActivationCode(self, intCD, entityName = None, avatar = None):
        return None

    def canActivate(self, intCD, entityName = None, avatar = None):
        return (False, None)

    def changeSetting(self, intCD, entityName = None, avatar = None):
        pass

    def changeSettingByTag(self, tag, entityName = None, avatar = None):
        pass


__all__ = ('EquipmentsController', 'EquipmentsReplayPlayer')
