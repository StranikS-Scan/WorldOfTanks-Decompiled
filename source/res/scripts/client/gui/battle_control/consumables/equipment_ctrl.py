# Embedded file name: scripts/client/gui/battle_control/consumables/equipment_ctrl.py
from collections import namedtuple
from functools import partial
import Event
import FMOD
import SoundGroups
import BigWorld
from constants import VEHICLE_SETTING, EQUIPMENT_STAGES
from debug_utils import LOG_ERROR
from gui.battle_control import avatar_getter, vehicle_getter
from gui.battle_control.battle_constants import makeExtraName, VEHICLE_COMPLEX_ITEMS
from gui.shared.utils.decorators import ReprInjector
from helpers import i18n
from items import vehicles
from shared_utils import findFirst, forEach
_ActivationError = namedtuple('_ActivationError', 'key ctx')

@ReprInjector.simple(('_tag', 'tag'), ('_quantity', 'quantity'), ('_stage', 'stage'), ('_prevStage', 'prevStage'), ('_timeRemaining', 'timeRemaining'))

class _EquipmentItem(object):
    __slots__ = ('_tag', '_descriptor', '_quantity', '_stage', '_prevStage', '_timeRemaining')

    def __init__(self, descriptor, quantity, stage, timeRemaining, tag = None):
        super(_EquipmentItem, self).__init__()
        self._tag = tag
        self._descriptor = descriptor
        self._quantity = 0
        self._stage = 0
        self._prevStage = 0
        self._timeRemaining = 0
        self.update(quantity, stage, timeRemaining)

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
        self._prevStage = 0
        self._timeRemaining = 0
        return

    def update(self, quantity, stage, timeRemaining):
        self._quantity = quantity
        self._prevStage = self._stage
        self._stage = stage
        self._timeRemaining = timeRemaining

    def activate(self, entityName = None, avatar = None):
        if 'avatar' in self._descriptor.tags:
            avatar_getter.activateAvatarEquipment(self.getEquipmentID(), avatar)
        else:
            avatar_getter.changeVehicleSetting(VEHICLE_SETTING.ACTIVATE_EQUIPMENT, self.getActivationCode(entityName, avatar), avatar=avatar)

    def deactivate(self):
        if 'avatar' in self._descriptor.tags:
            avatar_getter.activateAvatarEquipment(self.getEquipmentID())
        else:
            avatar_getter.changeVehicleSetting(VEHICLE_SETTING.ACTIVATE_EQUIPMENT, self.getEquipmentID())

    def getDescriptor(self):
        return self._descriptor

    def getQuantity(self):
        return self._quantity

    def isQuantityUsed(self):
        return False

    def getStage(self):
        return self._stage

    def getPrevStage(self):
        return self._prevStage

    def getTimeRemaining(self):
        return self._timeRemaining

    def getTotalTime(self):
        return -1

    def getMarker(self):
        return self._descriptor.name.split('_')[0]

    def getEquipmentID(self):
        nationID, innationID = self._descriptor.id
        return innationID

    def isAvatar(self):
        return 'avatar' in self._descriptor.tags


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

    def getTotalTime(self):
        if self._stage == EQUIPMENT_STAGES.DEPLOYING:
            return self._descriptor.deployTime
        if self._stage == EQUIPMENT_STAGES.COOLDOWN:
            return self._descriptor.cooldownTime
        return super(_OrderItem, self).getTotalTime()


class _ArtilleryItem(_OrderItem):

    def getMarker(self):
        return 'artillery'


class _BomberItem(_OrderItem):

    def getMarker(self):
        return 'bomber'


def _triggerItemFactory(descriptor, quantity, stage, timeRemaining, tag = None):
    if descriptor.name.startswith('artillery'):
        return _ArtilleryItem(descriptor, quantity, stage, timeRemaining, tag)
    if descriptor.name.startswith('bomber'):
        return _BomberItem(descriptor, quantity, stage, timeRemaining, tag)
    return _TriggerItem(descriptor, quantity, stage, timeRemaining, tag)


_EQUIPMENT_TAG_TO_ITEM = {'fuel': _AutoItem,
 'stimulator': _AutoItem,
 'trigger': _triggerItemFactory,
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
    __slots__ = ('__eManager', '_equipments', '__readySndName', 'onEquipmentAdded', 'onEquipmentUpdated', 'onEquipmentMarkerShown', 'onEquipmentCooldownInPercent')

    def __init__(self):
        super(EquipmentsController, self).__init__()
        self.__eManager = Event.EventManager()
        self.onEquipmentAdded = Event.Event(self.__eManager)
        self.onEquipmentUpdated = Event.Event(self.__eManager)
        self.onEquipmentMarkerShown = Event.Event(self.__eManager)
        self.onEquipmentCooldownInPercent = Event.Event(self.__eManager)
        self._equipments = {}
        self.__readySndName = 'combat_reserve'
        if FMOD.enabled:
            self.__readySndName = '/ingame_voice/ingame_voice_flt/combat_reserve'

    def __repr__(self):
        return 'EquipmentsController({0!r:s})'.format(self._equipments)

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
        while len(self._equipments):
            _, item = self._equipments.popitem()
            item.clear()

    def cancel(self):
        item = findFirst(lambda item: item.getStage() == EQUIPMENT_STAGES.PREPARING, self._equipments.itervalues())
        if item is not None:
            item.deactivate()
            return True
        else:
            return False

    def getEquipment(self, intCD):
        try:
            item = self._equipments[intCD]
        except KeyError:
            LOG_ERROR('Equipment is not found.', intCD)
            item = None

        return item

    def setEquipment(self, intCD, quantity, stage, timeRemaining):
        if not intCD:
            self.onEquipmentAdded(intCD, None)
            return
        else:
            if intCD in self._equipments:
                item = self._equipments[intCD]
                item.update(quantity, stage, timeRemaining)
                self.onEquipmentUpdated(intCD, item)
                if item.getPrevStage() in (EQUIPMENT_STAGES.DEPLOYING, EQUIPMENT_STAGES.UNAVAILABLE, EQUIPMENT_STAGES.COOLDOWN) and item.getStage() == EQUIPMENT_STAGES.READY:
                    SoundGroups.g_instance.playSound2D(self.__readySndName)
            else:
                descriptor = vehicles.getDictDescr(intCD)
                item = self.createItem(descriptor, quantity, stage, timeRemaining)
                self._equipments[intCD] = item
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
            for intCD, item in self._equipments.iteritems():
                if item.getTag() == tag and item.getQuantity() > 0:
                    result, error = self.__doChangeSetting(item, entityName, avatar)
                    break

            return (result, error)

    def showMarker(self, eq, pos, direction, time):
        item = findFirst(lambda e: e.getEquipmentID() == eq.id[1], self._equipments.itervalues())
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
                forEach(lambda e: e.deactivate(), [ e for e in self._equipments.itervalues() if e.getStage() == EQUIPMENT_STAGES.PREPARING ])
                item.activate(entityName, avatar)
        return (result, error)


class _ReplayItem(_EquipmentItem):
    __slots__ = '__cooldonwTime'

    def __init__(self, descriptor, quantity, stage, timeRemaining, tag = None):
        super(_ReplayItem, self).__init__(descriptor, quantity, stage, timeRemaining, tag)
        self.__cooldonwTime = BigWorld.serverTime() + timeRemaining

    def update(self, quantity, stage, timeRemaining):
        super(_ReplayItem, self).update(quantity, stage, timeRemaining)
        self.__cooldonwTime = BigWorld.serverTime() + timeRemaining

    def getEntitiesIterator(self, avatar = None):
        return []

    def getGuiIterator(self, avatar = None):
        return []

    def canActivate(self, entityName = None, avatar = None):
        return (False, None)

    def getTimeRemaining(self):
        return max(0, self.__cooldonwTime - BigWorld.serverTime())

    def getCooldownPercents(self):
        totalTime = self.getTotalTime()
        timeRemaining = self.getTimeRemaining()
        if totalTime > 0:
            return round(float(totalTime - timeRemaining) / totalTime * 100.0)
        return 0.0


class _ReplayOrderItem(_ReplayItem):

    def update(self, quantity, stage, timeRemaining):
        from AvatarInputHandler import MapCaseMode
        if stage == EQUIPMENT_STAGES.PREPARING and self._stage != stage:
            MapCaseMode.activateMapCase(self.getEquipmentID(), partial(self.deactivate))
        elif self._stage == EQUIPMENT_STAGES.PREPARING and self._stage != stage:
            MapCaseMode.turnOffMapCase(self.getEquipmentID())
        super(_ReplayOrderItem, self).update(quantity, stage, timeRemaining)

    def getTotalTime(self):
        if self._stage == EQUIPMENT_STAGES.DEPLOYING:
            return self._descriptor.deployTime
        if self._stage == EQUIPMENT_STAGES.COOLDOWN:
            return self._descriptor.cooldownTime
        return super(_ReplayOrderItem, self).getTotalTime()


class _ReplayArtilleryItem(_ReplayOrderItem):

    def getMarker(self):
        return 'artillery'


class _ReplayBomberItem(_ReplayOrderItem):

    def getMarker(self):
        return 'bomber'


def _replayTriggerItemFactory(descriptor, quantity, stage, timeRemaining, tag = None):
    if descriptor.name.startswith('artillery'):
        return _ReplayArtilleryItem(descriptor, quantity, stage, timeRemaining, tag)
    if descriptor.name.startswith('bomber'):
        return _ReplayBomberItem(descriptor, quantity, stage, timeRemaining, tag)
    return _ReplayItem(descriptor, quantity, stage, timeRemaining, tag)


_REPLAY_EQUIPMENT_TAG_TO_ITEM = {'fuel': _ReplayItem,
 'stimulator': _ReplayItem,
 'trigger': _replayTriggerItemFactory,
 'extinguisher': _ReplayItem,
 'medkit': _ReplayItem,
 'repairkit': _ReplayItem}

class EquipmentsReplayPlayer(EquipmentsController):
    __slots__ = ('__callbackID', '__percentGetters', '__percents')

    def __init__(self):
        super(EquipmentsReplayPlayer, self).__init__()
        self.__callbackID = None
        self.__percentGetters = {}
        self.__percents = {}
        return

    def clear(self, leave = True):
        if leave:
            if self.__callbackID is not None:
                BigWorld.cancelCallback(self.__callbackID)
                self.__callbackID = None
            self.__percents.clear()
            self.__percentGetters.clear()
        super(EquipmentsReplayPlayer, self).clear(leave)
        return

    def setEquipment(self, intCD, quantity, stage, timeRemaining):
        super(EquipmentsReplayPlayer, self).setEquipment(intCD, quantity, stage, timeRemaining)
        self.__percents.pop(intCD, None)
        self.__percentGetters.pop(intCD, None)
        if stage in (EQUIPMENT_STAGES.DEPLOYING, EQUIPMENT_STAGES.COOLDOWN):
            self.__percentGetters[intCD] = self._equipments[intCD].getCooldownPercents
            if self.__callbackID is not None:
                BigWorld.cancelCallback(self.__callbackID)
                self.__callbackID = None
            self.__timeLoop()
        return

    @classmethod
    def createItem(cls, descriptor, quantity, stage, timeRemaining):
        tag = _getSupportedTag(descriptor)
        clazz = tag and _REPLAY_EQUIPMENT_TAG_TO_ITEM[tag]
        if not clazz:
            raise AssertionError
            item = clazz(descriptor, quantity, stage, timeRemaining, tag)
        else:
            item = _ReplayItem(descriptor, quantity, timeRemaining, stage)
        return item

    def getActivationCode(self, intCD, entityName = None, avatar = None):
        return None

    def canActivate(self, intCD, entityName = None, avatar = None):
        return (False, None)

    def changeSetting(self, intCD, entityName = None, avatar = None):
        return (False, None)

    def changeSettingByTag(self, tag, entityName = None, avatar = None):
        return (False, None)

    def __timeLoop(self):
        self.__callbackID = None
        self.__tick()
        self.__callbackID = BigWorld.callback(0.1, self.__timeLoop)
        return

    def __tick(self):
        for intCD, percentGetter in self.__percentGetters.iteritems():
            percent = percentGetter()
            currentPercent = self.__percents.get(intCD)
            if currentPercent != percent:
                self.__percents[intCD] = percent
                self.onEquipmentCooldownInPercent(intCD, percent)


__all__ = ('EquipmentsController', 'EquipmentsReplayPlayer')
