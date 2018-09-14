# Embedded file name: scripts/client/gui/battle_control/consumables/equipment_ctrl.py
from collections import namedtuple
from functools import partial
import Event
from constants import VEHICLE_SETTING, EQUIPMENT_STAGES
from debug_utils import LOG_ERROR
from gui.battle_control import avatar_getter, vehicle_getter
from gui.battle_control.battle_constants import makeExtraName, VEHICLE_COMPLEX_ITEMS
from gui.shared.utils import findFirst, forEach
from helpers import i18n
from items import vehicles
_ActivationError = namedtuple('_ActivationError', 'key ctx')

class _EquipmentItem(object):
    __slots__ = ('_tag', '_descriptor', '_quantity', '_stage', '_timeRemaining')

    def __init__(self, descriptor, quantity, stage, timeRemaining, tag = None):
        super(_EquipmentItem, self).__init__()
        self._tag = tag
        self._descriptor = descriptor
        self._quantity = 0
        self._stage = 0
        self._timeRemaining = 0
        self.update(quantity, stage, timeRemaining)

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
        if self._timeRemaining > 0 and self._stage and self._stage not in (EQUIPMENT_STAGES.DEPLOYING, EQUIPMENT_STAGES.COOLDOWN):
            result = False
            error = _ActivationError('equipmentAlreadyActivated', {'name': self._descriptor.userString})
        elif self._stage and self._stage not in (EQUIPMENT_STAGES.READY, EQUIPMENT_STAGES.PREPARING):
            result = False
            error = None
            if self._stage == EQUIPMENT_STAGES.ACTIVE:
                error = _ActivationError('equipmentAlreadyActivated', {'name': self._descriptor.userString})
        elif self._quantity <= 0:
            result = False
            error = None
        else:
            result = True
            error = None
        return (result, error)

    def getActivationCode(self, entityName = None, avatar = None):
        return None

    def clear(self):
        self._descriptor = None
        self._quantity = 0
        self._stage = 0
        self._timeRemaining = 0
        return

    def update(self, quantity, stage, timeRemaining):
        self._quantity = quantity
        self._stage = stage
        self._timeRemaining = timeRemaining

    def activate(self, entityName = None, avatar = None):
        avatar_getter.changeVehicleSetting(VEHICLE_SETTING.ACTIVATE_EQUIPMENT, self.getActivationCode(entityName, avatar), avatar=avatar)

    def deactivate(self):
        avatar_getter.changeVehicleSetting(VEHICLE_SETTING.ACTIVATE_EQUIPMENT, self.getEquipmentID())

    def getDescriptor(self):
        return self._descriptor

    def getQuantity(self):
        return self._quantity

    def isQuantityUsed(self):
        return False

    def getStage(self):
        return self._stage

    def getTimeRemaining(self):
        return self._timeRemaining

    def getMarker(self):
        return self._descriptor.name.split('_')[0]

    def getEquipmentID(self):
        nationID, innationID = self._descriptor.id
        return innationID


class _AutoItem(_EquipmentItem):

    def canActivate(self, entityName = None, avatar = None):
        return (False, None)


class _TriggerItem(_EquipmentItem):

    def getActivationCode(self, entityName = None, avatar = None):
        flag = 1 if self._timeRemaining == 0 else 0
        return (flag << 16) + self._descriptor.id[1]


class _ExtinguisherItem(_EquipmentItem):

    def canActivate(self, entityName = None, avatar = None):
        result, error = super(_ExtinguisherItem, self).canActivate(entityName, avatar)
        if not result:
            return (result, error)
        elif not avatar_getter.isVehicleInFire(avatar):
            return (False, _ActivationError('extinguisherDoesNotActivated', {'name': self._descriptor.userString}))
        else:
            return (True, None)

    def getActivationCode(self, entityName = None, avatar = None):
        return 65536 + self._descriptor.id[1]


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
                    for item in self.getEntitiesIterator():
                        if item[0] in deviceStates:
                            return (False, None)

                    return (False, _ActivationError(self._getEntitiesAreSafeKey(), None))
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


class _OrderItem(_TriggerItem):

    def update(self, quantity, stage, timeRemaining):
        from AvatarInputHandler import MapCaseMode
        if stage == EQUIPMENT_STAGES.PREPARING and self._stage != stage:
            MapCaseMode.activateMapCase(self.getEquipmentID(), partial(self.deactivate))
        elif self._stage == EQUIPMENT_STAGES.PREPARING and self._stage != stage:
            MapCaseMode.turnOffMapCase(self.getEquipmentID())
        super(_OrderItem, self).update(quantity, stage, timeRemaining)


class _ArtilleryItem(_OrderItem):

    def getMarker(self):
        return 'artillery'


class _BomberItem(_OrderItem):

    def getMarker(self):
        return 'bomber'


def _tiggerItemFactory(descriptor, quantity, stage, timeRemaining, tag = None):
    if descriptor.name.startswith('artillery'):
        return _ArtilleryItem(descriptor, quantity, stage, timeRemaining, tag)
    if descriptor.name.startswith('bomber'):
        return _BomberItem(descriptor, quantity, stage, timeRemaining, tag)
    return _TriggerItem(descriptor, quantity, stage, timeRemaining, tag)


_EQUIPMENT_TAG_TO_ITEM = {'fuel': _AutoItem,
 'stimulator': _AutoItem,
 'trigger': _tiggerItemFactory,
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
    __slots__ = ('__eManager', '__equipments', 'onEquipmentAdded', 'onEquipmentUpdated', 'onEquipmentMarkerShown')

    def __init__(self):
        super(EquipmentsController, self).__init__()
        self.__eManager = Event.EventManager()
        self.onEquipmentAdded = Event.Event(self.__eManager)
        self.onEquipmentUpdated = Event.Event(self.__eManager)
        self.onEquipmentMarkerShown = Event.Event(self.__eManager)
        self.__equipments = {}

    def __repr__(self):
        return 'EquipmentsController({0!r:s})'.format(self.__equipments)

    @classmethod
    def createItem(cls, descriptor, quantity, stage, timeRemaining):
        tag = _getSupportedTag(descriptor)
        clazz = tag and _EQUIPMENT_TAG_TO_ITEM[tag]
        if not clazz:
            raise AssertionError
            item = clazz(descriptor, quantity, stage, timeRemaining, tag)
        else:
            item = _EquipmentItem(descriptor, quantity, stage, timeRemaining)
        return item

    def clear(self, leave = True):
        if leave:
            self.__eManager.clear()
        while len(self.__equipments):
            _, item = self.__equipments.popitem()
            item.clear()

    def cancel(self):
        item = findFirst(lambda item: item.getStage() == EQUIPMENT_STAGES.PREPARING, self.__equipments.itervalues())
        if item is not None:
            item.deactivate()
            return True
        else:
            return False

    def getEquipment(self, intCD):
        try:
            item = self.__equipments[intCD]
        except KeyError:
            LOG_ERROR('Equipment is not found.', intCD)
            item = None

        return item

    def setEquipment(self, intCD, quantity, stage, timeRemaining):
        if not intCD:
            self.onEquipmentAdded(intCD, None, False)
            return
        else:
            if intCD in self.__equipments:
                item = self.__equipments[intCD]
                isDeployed = item.getStage() == EQUIPMENT_STAGES.DEPLOYING and stage == EQUIPMENT_STAGES.READY
                item.update(quantity, stage, timeRemaining)
                self.onEquipmentUpdated(intCD, item, isinstance(item, _OrderItem), isDeployed)
            else:
                descriptor = vehicles.getDictDescr(intCD)
                item = self.createItem(descriptor, quantity, stage, timeRemaining)
                self.__equipments[intCD] = item
                self.onEquipmentAdded(intCD, item, isinstance(item, _OrderItem))
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

    def showMarker(self, eq, pos, direction, time):
        item = findFirst(lambda e: e.getEquipmentID() == eq.id[1], self.__equipments.itervalues())
        if item is None:
            item = self.createItem(eq, 0, -1, 0)
        self.onEquipmentMarkerShown(item, pos, direction, time)
        return

    def __doChangeSetting(self, item, entityName = None, avatar = None):
        result, error = item.canActivate(entityName, avatar)
        if result and avatar_getter.isPlayerOnArena(avatar):
            if item.getStage() == EQUIPMENT_STAGES.PREPARING:
                item.deactivate()
            else:
                forEach(lambda e: e.deactivate(), [ e for e in self.__equipments.itervalues() if e.getStage() == EQUIPMENT_STAGES.PREPARING ])
                item.activate(entityName, avatar)
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
    def createItem(cls, descriptor, quantity, stage, timeRemaining):
        return _ReplayItem(descriptor, quantity, timeRemaining, stage, _getSupportedTag(descriptor))

    def getActivationCode(self, intCD, entityName = None, avatar = None):
        return None

    def canActivate(self, intCD, entityName = None, avatar = None):
        return (False, None)

    def changeSetting(self, intCD, entityName = None, avatar = None):
        pass

    def changeSettingByTag(self, tag, entityName = None, avatar = None):
        pass


__all__ = ('EquipmentsController', 'EquipmentsReplayPlayer')
