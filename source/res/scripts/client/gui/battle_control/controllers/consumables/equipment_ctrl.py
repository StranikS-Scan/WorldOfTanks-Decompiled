# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/consumables/equipment_ctrl.py
from collections import namedtuple
from functools import partial
import BigWorld
import Event
import SoundGroups
from constants import VEHICLE_SETTING, EQUIPMENT_STAGES
from debug_utils import LOG_ERROR, LOG_DEBUG
from gui.Scaleform.genConsts.ANIMATION_TYPES import ANIMATION_TYPES
from gui.battle_control import avatar_getter, vehicle_getter
from gui.battle_control.battle_constants import makeExtraName, VEHICLE_COMPLEX_ITEMS, BATTLE_CTRL_ID
from gui.battle_control.controllers.interfaces import IBattleController
from gui.shared.utils.MethodsRules import MethodsRules
from gui.shared.utils.decorators import ReprInjector
from helpers import i18n
from items import vehicles, EQUIPMENT_TYPES
from shared_utils import findFirst, forEach
from soft_exception import SoftException
_ActivationError = namedtuple('_ActivationError', 'key ctx')

class NotApplyingError(_ActivationError):
    pass


class InCooldownError(_ActivationError):
    pass


class NeedEntitySelection(_ActivationError):
    pass


class IgnoreEntitySelection(_ActivationError):
    pass


class EquipmentSound(object):
    _soundMap = {251: 'battle_equipment_251',
     507: 'battle_equipment_507',
     1019: 'battle_equipment_1019',
     763: 'battle_equipment_763',
     1531: 'battle_equipment_1531',
     1275: 'battle_equipment_1275'}

    @staticmethod
    def getSounds():
        return EquipmentSound._soundMap.values()

    @staticmethod
    def playSound(ID):
        soundName = EquipmentSound._soundMap.get(ID, None)
        if soundName is not None:
            SoundGroups.g_instance.playSound2D(soundName)
        return

    @staticmethod
    def playReady(item):
        if item.requiresSoundNotification:
            equipment = vehicles.g_cache.equipments()[item.getEquipmentID()]
            if equipment is not None:
                if equipment.soundNotification is not None:
                    avatar_getter.getSoundNotifications().play(equipment.soundNotification)
                    return
            avatar_getter.getSoundNotifications().play('combat_reserve')
        return


@ReprInjector.simple(('_tag', 'tag'), ('_quantity', 'quantity'), ('_stage', 'stage'), ('_prevStage', 'prevStage'), ('_timeRemaining', 'timeRemaining'), ('_totalTime', 'totalTime'), ('_animationType', 'animationType'))
class _EquipmentItem(object):
    __slots__ = ('_tag', '_descriptor', '_quantity', '_stage', '_prevStage', '_timeRemaining', '_prevQuantity', '_totalTime', '_animationType')

    def __init__(self, descriptor, quantity, stage, timeRemaining, totalTime, tag=None):
        super(_EquipmentItem, self).__init__()
        self._tag = tag
        self._descriptor = descriptor
        self._quantity = 0
        self._stage = 0
        self._prevStage = 0
        self._prevQuantity = 0
        self._timeRemaining = 0
        self._totalTime = 0
        self._animationType = ANIMATION_TYPES.MOVE_ORANGE_BAR_UP + ANIMATION_TYPES.SHOW_COUNTER_ORANGE + ANIMATION_TYPES.DARK_COLOR_TRANSFORM
        self.update(quantity, stage, timeRemaining, totalTime)
        if self.isReusable:
            self._totalTime = self._descriptor.cooldownSeconds

    @property
    def requiresSoundNotification(self):
        return self._tag not in ('extinguisher', 'medkit', 'repairkit')

    def getAnimationType(self):
        return self._animationType

    def getTag(self):
        return _getSupportedTag(self._descriptor)

    def isEntityRequired(self):
        return False

    def getEntitiesIterator(self, avatar=None):
        raise SoftException('Invokes getEntitiesIterator, than it is not required')

    def getGuiIterator(self, avatar=None):
        raise SoftException('Invokes getGuiIterator, than it is not required')

    @property
    def isAvailableToUse(self):
        return self.getQuantity() > 0 and self.isReady

    def canActivate(self, entityName=None, avatar=None):
        if self._timeRemaining > 0 and self._stage and self._stage not in (EQUIPMENT_STAGES.DEPLOYING, EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.SHARED_COOLDOWN):
            result = False
            error = _ActivationError('equipmentAlreadyActivated', {'name': self._descriptor.userString})
        elif self._stage and self._stage not in (EQUIPMENT_STAGES.READY, EQUIPMENT_STAGES.PREPARING):
            result = False
            error = None
            if self._stage == EQUIPMENT_STAGES.ACTIVE:
                error = _ActivationError('equipmentAlreadyActivated', {'name': self._descriptor.userString})
            elif self._stage == EQUIPMENT_STAGES.COOLDOWN:
                error = InCooldownError('equipmentIsInCooldown', {'name': self._descriptor.userString})
        elif self._quantity <= 0:
            result = False
            error = None
        else:
            result = True
            error = None
        return (result, error)

    def getActivationCode(self, entityName=None, avatar=None):
        return None

    def clear(self):
        self._descriptor = None
        self._quantity = 0
        self._prevQuantity = 0
        self._stage = 0
        self._prevStage = 0
        self._timeRemaining = 0
        self._totalTime = 0
        return

    def update(self, quantity, stage, timeRemaining, totalTime):
        self._prevQuantity = self._quantity
        self._quantity = quantity
        self._prevStage = self._stage
        self._stage = stage
        self._timeRemaining = timeRemaining
        if not self.isReusable:
            self._totalTime = totalTime
        self._soundUpdate(self._prevQuantity, quantity)

    def activate(self, entityName=None, avatar=None):
        if 'avatar' in self._descriptor.tags:
            avatar_getter.activateAvatarEquipment(self.getEquipmentID(), avatar)
        else:
            avatar_getter.changeVehicleSetting(VEHICLE_SETTING.ACTIVATE_EQUIPMENT, self.getActivationCode(entityName, avatar), avatar=avatar)

    def deactivate(self):
        if 'avatar' in self._descriptor.tags:
            avatar_getter.activateAvatarEquipment(self.getEquipmentID())
        else:
            avatar_getter.changeVehicleSetting(VEHICLE_SETTING.ACTIVATE_EQUIPMENT, self.getEquipmentID())

    @property
    def isReusable(self):
        return self._descriptor.reuseCount != 0

    @property
    def isReady(self):
        return self._stage == EQUIPMENT_STAGES.READY

    @property
    def becomeReady(self):
        return self.isReady and self._prevStage in (EQUIPMENT_STAGES.DEPLOYING, EQUIPMENT_STAGES.UNAVAILABLE, EQUIPMENT_STAGES.COOLDOWN)

    def getDescriptor(self):
        return self._descriptor

    def getQuantity(self):
        return self._quantity

    def getPrevQuantity(self):
        return self._prevQuantity

    def isQuantityUsed(self):
        return 'showQuantity' in self._descriptor.tags

    def getStage(self):
        return self._stage

    def getPrevStage(self):
        return self._prevStage

    def getTimeRemaining(self):
        return self._timeRemaining

    def getTotalTime(self):
        return self._totalTime

    def getMarker(self):
        return self._descriptor.name.split('_')[0]

    def getEquipmentID(self):
        _, innationID = self._descriptor.id
        return innationID

    def isAvatar(self):
        return 'avatar' in self._descriptor.tags

    def _soundUpdate(self, prevQuantity, quantity):
        if prevQuantity > quantity:
            if self._stage != EQUIPMENT_STAGES.NOT_RUNNING:
                EquipmentSound.playSound(self._descriptor.compactDescr)
        if self.becomeReady:
            EquipmentSound.playReady(self)


class _AutoItem(_EquipmentItem):

    def canActivate(self, entityName=None, avatar=None):
        return (False, None)


class _TriggerItem(_EquipmentItem):

    def getActivationCode(self, entityName=None, avatar=None):
        flag = 1 if self._timeRemaining == 0 else 0
        return (flag << 16) + self._descriptor.id[1]


class _ExpandedItem(_EquipmentItem):

    def isEntityRequired(self):
        return not self._descriptor.repairAll

    def canActivate(self, entityName=None, avatar=None):
        result, error = super(_ExpandedItem, self).canActivate(entityName, avatar)
        return (result, error) if not result else self._canActivate(entityName, avatar)

    def getActivationCode(self, entityName=None, avatar=None):
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
        pass

    def _getEntityIsSafeKey(self):
        pass

    def _getEntityUserString(self, entityName, avatar=None):
        extrasDict = avatar_getter.getVehicleExtrasDict(avatar)
        extraName = makeExtraName(entityName)
        if extraName in extrasDict:
            userString = extrasDict[extraName].deviceUserString
        else:
            userString = entityName
        return userString

    def _canActivate(self, entityName=None, avatar=None):
        deviceStates = avatar_getter.getVehicleDeviceStates(avatar)
        if not deviceStates:
            return (False, _ActivationError(self._getEntitiesAreSafeKey(), None))
        elif entityName is None:
            for item in self.getEntitiesIterator():
                if item[0] in deviceStates:
                    isEntityNotRequired = not self.isEntityRequired()
                    return (isEntityNotRequired, None if isEntityNotRequired else NeedEntitySelection('', None))

            return (False, _ActivationError(self._getEntitiesAreSafeKey(), None))
        else:
            return (False, NotApplyingError(self._getEntityIsSafeKey(), {'entity': self._getEntityUserString(entityName)})) if entityName not in deviceStates else (True, None)


class _ExtinguisherItem(_EquipmentItem):

    def canActivate(self, entityName=None, avatar=None):
        result, error = super(_ExtinguisherItem, self).canActivate(entityName, avatar)
        if not result:
            return (result, error)
        else:
            return (False, _ActivationError('extinguisherDoesNotActivated', {'name': self._descriptor.userString})) if not avatar_getter.isVehicleInFire(avatar) else (True, None)

    def getActivationCode(self, entityName=None, avatar=None):
        return 65536 + self._descriptor.id[1]


class _MedKitItem(_ExpandedItem):

    def getActivationCode(self, entityName=None, avatar=None):
        activationCode = super(_MedKitItem, self).getActivationCode(entityName, avatar)
        if activationCode is None and avatar_getter.isVehicleStunned() and self.isReusable:
            extrasDict = avatar_getter.getVehicleExtrasDict(avatar)
            activationCode = (extrasDict[makeExtraName('commander')].index << 16) + self._descriptor.id[1]
        return activationCode

    def getEntitiesIterator(self, avatar=None):
        return vehicle_getter.TankmenStatesIterator(avatar_getter.getVehicleDeviceStates(avatar), avatar_getter.getVehicleTypeDescriptor(avatar))

    def getGuiIterator(self, avatar=None):
        for name, state in self.getEntitiesIterator(avatar):
            yield (name, name, state)

    def _canActivate(self, entityName=None, avatar=None):
        result, error = super(_MedKitItem, self)._canActivate(entityName, avatar)
        return (True, IgnoreEntitySelection('', None)) if not result and type(error) not in (NeedEntitySelection, NotApplyingError) and avatar_getter.isVehicleStunned() and self.isReusable else (result, error)

    def _getEntitiesAreSafeKey(self):
        pass

    def _getEntityIsSafeKey(self):
        pass


class _RepairKitItem(_ExpandedItem):

    def getEntitiesIterator(self, avatar=None):
        return vehicle_getter.VehicleDeviceStatesIterator(avatar_getter.getVehicleDeviceStates(avatar), avatar_getter.getVehicleTypeDescriptor(avatar))

    def getGuiIterator(self, avatar=None):
        return vehicle_getter.VehicleGUIItemStatesIterator(avatar_getter.getVehicleDeviceStates(avatar), avatar_getter.getVehicleTypeDescriptor(avatar))

    def _getEntitiesAreSafeKey(self):
        pass

    def _getEntityIsSafeKey(self):
        pass

    def _getEntityUserString(self, entityName, avatar=None):
        return i18n.makeString('#ingame_gui:devices/{0}'.format(entityName)) if entityName in VEHICLE_COMPLEX_ITEMS else super(_RepairKitItem, self)._getEntityUserString(entityName, avatar)


class _OrderItem(_TriggerItem):

    def deactivate(self):
        if self._descriptor is not None:
            super(_OrderItem, self).deactivate()
        return

    def canActivate(self, entityName=None, avatar=None):
        if self._timeRemaining > 0 and self._stage and self._stage in (EQUIPMENT_STAGES.DEPLOYING, EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.SHARED_COOLDOWN):
            result = False
            error = _ActivationError('orderNotReady', {'name': self._descriptor.userString})
            return (result, error)
        return super(_OrderItem, self).canActivate(entityName, avatar)

    def update(self, quantity, stage, timeRemaining, totalTime):
        from AvatarInputHandler import MapCaseMode
        if stage == EQUIPMENT_STAGES.PREPARING and self._stage != stage:
            MapCaseMode.activateMapCase(self.getEquipmentID(), partial(self.deactivate))
        elif self._stage == EQUIPMENT_STAGES.PREPARING and self._stage != stage:
            MapCaseMode.turnOffMapCase(self.getEquipmentID())
        super(_OrderItem, self).update(quantity, stage, timeRemaining, totalTime)


class _ArtilleryItem(_OrderItem):

    def getMarker(self):
        pass


class _BomberItem(_OrderItem):

    def getMarker(self):
        pass


class _ReconItem(_OrderItem):

    def getMarker(self):
        pass


class _SmokeItem(_OrderItem):

    def getMarker(self):
        pass


class _LastChanceItem(_TriggerItem):
    __slots__ = ('__cooldownTime',)

    def __init__(self, descriptor, quantity, stage, timeRemaining, totalTime, tag=None):
        self.__cooldownTime = descriptor.cooldownTime
        super(_LastChanceItem, self).__init__(descriptor, quantity, stage, timeRemaining, totalTime, tag)

    def getTag(self):
        pass

    def update(self, quantity, stage, timeRemaining, totalTime):
        if stage == EQUIPMENT_STAGES.UNAVAILABLE:
            quantity = 0
        if stage == EQUIPMENT_STAGES.COOLDOWN:
            quantity = 1
            totalTime = self.__cooldownTime
        super(_LastChanceItem, self).update(quantity, stage, timeRemaining, totalTime)

    def getEntitiesIterator(self, avatar=None):
        return []


class _AfterburningItem(_TriggerItem):
    __slots__ = ('__totalConsumingTime', '__totalRechargingTime', '_prevTimeRemaining')

    def __init__(self, descriptor, quantity, stage, timeRemaining, totalTime, tag=None):
        self.__totalConsumingTime = descriptor.maxAmount / descriptor.consumePerSec
        self.__totalRechargingTime = descriptor.maxAmount / descriptor.rechargePerSec
        self._prevTimeRemaining = -1
        super(_AfterburningItem, self).__init__(descriptor, quantity, stage, timeRemaining, totalTime, tag)

    def getTag(self):
        pass

    def update(self, quantity, stage, timeRemaining, totalTime):
        self._prevTimeRemaining = self._timeRemaining
        if stage == EQUIPMENT_STAGES.ACTIVE:
            self._animationType = ANIMATION_TYPES.MOVE_GREEN_BAR_DOWN + ANIMATION_TYPES.CENTER_COUNTER + ANIMATION_TYPES.GREEN_GLOW_SHOW + ANIMATION_TYPES.DARK_COLOR_TRANSFORM
            totalTime = self.__totalConsumingTime
        elif stage == EQUIPMENT_STAGES.READY:
            self._animationType = ANIMATION_TYPES.MOVE_GREEN_BAR_UP + ANIMATION_TYPES.SHOW_COUNTER_GREEN
            if self._stage != stage != EQUIPMENT_STAGES.COOLDOWN:
                self._animationType += ANIMATION_TYPES.GREEN_GLOW_HIDE
            totalTime = self.__totalRechargingTime
        elif stage == EQUIPMENT_STAGES.DEPLOYING:
            self._animationType = ANIMATION_TYPES.MOVE_ORANGE_BAR_UP + ANIMATION_TYPES.SHOW_COUNTER_ORANGE
            totalTime = timeRemaining
        elif stage == EQUIPMENT_STAGES.COOLDOWN:
            self._animationType = ANIMATION_TYPES.MOVE_ORANGE_BAR_UP + ANIMATION_TYPES.SHOW_COUNTER_ORANGE + ANIMATION_TYPES.FILL_PARTIALLY
            totalTime = self.__totalRechargingTime
        super(_AfterburningItem, self).update(quantity, stage, timeRemaining, totalTime)

    def canActivate(self, entityName=None, avatar=None):
        result, error = False, None
        if self._stage in (EQUIPMENT_STAGES.READY, EQUIPMENT_STAGES.ACTIVE):
            result = True
        elif self._stage in (EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.DEPLOYING):
            error = InCooldownError('equipmentIsInCooldown', {'name': self._descriptor.userString})
        return (result, error)

    def getEntitiesIterator(self, avatar=None):
        return []

    @property
    def becomeReady(self):
        return self._prevTimeRemaining >= 0 and self._timeRemaining == -1 and self._stage == EQUIPMENT_STAGES.READY

    def _soundUpdate(self, prevQuantity, quantity):
        if self.becomeReady:
            EquipmentSound.playReady(self)


def _triggerItemFactory(descriptor, quantity, stage, timeRemaining, totalTime, tag=None):
    if descriptor.name.startswith('artillery'):
        return _ArtilleryItem(descriptor, quantity, stage, timeRemaining, totalTime, tag)
    if descriptor.name.startswith('bomber'):
        return _BomberItem(descriptor, quantity, stage, timeRemaining, totalTime, tag)
    if descriptor.name.startswith('recon'):
        return _ReconItem(descriptor, quantity, stage, timeRemaining, totalTime, tag)
    if descriptor.name.startswith('smoke'):
        return _SmokeItem(descriptor, quantity, stage, timeRemaining, totalTime, tag)
    if descriptor.name.endswith('afterburning'):
        return _AfterburningItem(descriptor, quantity, stage, timeRemaining, totalTime, tag)
    return _LastChanceItem(descriptor, quantity, stage, timeRemaining, totalTime, tag) if descriptor.name.startswith('lastchance') else _TriggerItem(descriptor, quantity, stage, timeRemaining, totalTime, tag)


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


class EquipmentsController(MethodsRules, IBattleController):
    __slots__ = ('__eManager', '_order', '_equipments', '__preferredPosition', 'onEquipmentAdded', 'onEquipmentUpdated', 'onEquipmentMarkerShown', 'onEquipmentCooldownInPercent', 'onEquipmentCooldownTime')

    def __init__(self):
        super(EquipmentsController, self).__init__()
        self.__eManager = Event.EventManager()
        self.onEquipmentAdded = Event.Event(self.__eManager)
        self.onEquipmentUpdated = Event.Event(self.__eManager)
        self.onEquipmentMarkerShown = Event.Event(self.__eManager)
        self.onEquipmentCooldownInPercent = Event.Event(self.__eManager)
        self.onEquipmentCooldownTime = Event.Event(self.__eManager)
        self._order = []
        self._equipments = {}
        self.__preferredPosition = None
        return

    def __repr__(self):
        return 'EquipmentsController({0!r:s})'.format(self._equipments)

    def getControllerID(self):
        return BATTLE_CTRL_ID.EQUIPMENTS

    def startControl(self, *args):
        pass

    def stopControl(self):
        self.clear(leave=True)

    @classmethod
    def createItem(cls, descriptor, quantity, stage, timeRemaining, totalTime):
        tag = _getSupportedTag(descriptor)
        if tag:
            clazz = _EQUIPMENT_TAG_TO_ITEM[tag]
            item = clazz(descriptor, quantity, stage, timeRemaining, totalTime, tag)
        else:
            item = _EquipmentItem(descriptor, quantity, stage, timeRemaining, totalTime)
        return item

    def clear(self, leave=True):
        super(EquipmentsController, self).clear()
        LOG_DEBUG('EquipmentsController CLEARED')
        if leave:
            self.__eManager.clear()
        self._order = []
        while self._equipments:
            _, item = self._equipments.popitem()
            item.clear()

    def cancel(self):
        item = findFirst(lambda item: item.getStage() == EQUIPMENT_STAGES.PREPARING, self._equipments.itervalues())
        if item is not None:
            item.deactivate()
            return True
        else:
            return False

    def hasEquipment(self, intCD):
        return intCD in self._equipments

    def iterEquipmentsByTag(self, tag, condition=None):
        return ((intCD, item) for intCD, item in self._equipments.iteritems() if item.getTag() == tag and (condition is None or condition(item)))

    def getEquipment(self, intCD):
        try:
            item = self._equipments[intCD]
        except KeyError:
            LOG_ERROR('Equipment is not found.', intCD)
            item = None

        return item

    def getOrderedEquipmentsLayout(self):
        return map(lambda intCD: (intCD, self._equipments[intCD]), self._order)

    @MethodsRules.delayable()
    def notifyPlayerVehicleSet(self):
        pass

    @MethodsRules.delayable('notifyPlayerVehicleSet')
    def setEquipment(self, intCD, quantity, stage, timeRemaining, totalTime):
        LOG_DEBUG('Equipment added: ', str(intCD), ' ', str(quantity), ' ', str(stage), ' ', str(timeRemaining), ' ', str(totalTime))
        if not intCD:
            if len(self._order) < vehicles.NUM_EQUIPMENT_SLOTS_BY_TYPE[EQUIPMENT_TYPES.regular]:
                self._order.append(0)
                self.onEquipmentAdded(0, None)
        elif intCD in self._equipments:
            item = self._equipments[intCD]
            item.update(quantity, stage, timeRemaining, totalTime)
            self.onEquipmentUpdated(intCD, item)
        else:
            descriptor = vehicles.getItemByCompactDescr(intCD)
            if descriptor.equipmentType in (EQUIPMENT_TYPES.regular, EQUIPMENT_TYPES.battleAbilities):
                item = self.createItem(descriptor, quantity, stage, timeRemaining, totalTime)
                self._equipments[intCD] = item
                self._order.append(intCD)
                self.onEquipmentAdded(intCD, item)
        return

    def getActivationCode(self, intCD, entityName=None, avatar=None):
        code = None
        item = self.getEquipment(intCD)
        if item:
            code = item.getActivationCode(entityName, avatar)
        return code

    def canActivate(self, intCD, entityName=None, avatar=None):
        result, error = False, None
        item = self.getEquipment(intCD)
        if item:
            result, error = item.canActivate(entityName, avatar)
        return (result, error)

    def changeSetting(self, intCD, entityName=None, avatar=None):
        if not avatar_getter.isVehicleAlive(avatar):
            return (False, None)
        else:
            result, error = False, None
            item = self.getEquipment(intCD)
            if item:
                result, error = self.__doChangeSetting(item, entityName, avatar)
            return (result, error)

    def changeSettingByTag(self, tag, entityName=None, avatar=None):
        if not avatar_getter.isVehicleAlive(avatar):
            return (False, None)
        else:
            result, error = True, None
            for _, item in self._equipments.iteritems():
                if item.getTag() == tag and item.isAvailableToUse:
                    result, error = self.__doChangeSetting(item, entityName, avatar)
                    break

            return (result, error)

    def showMarker(self, eq, pos, direction, time):
        item = findFirst(lambda e: e.getEquipmentID() == eq.id[1], self._equipments.itervalues())
        if item is None:
            item = self.createItem(eq, 0, -1, 0, 0)
        self.onEquipmentMarkerShown(item, pos, direction, time)
        return

    def consumePreferredPosition(self):
        value = self.__preferredPosition
        self.__preferredPosition = None
        return value

    def __doChangeSetting(self, item, entityName=None, avatar=None):
        result, error = item.canActivate(entityName, avatar)
        if result and avatar_getter.isPlayerOnArena(avatar):
            if item.getStage() == EQUIPMENT_STAGES.PREPARING:
                item.deactivate()
            else:
                curCtrl = BigWorld.player().inputHandler.ctrl
                if curCtrl is not None and curCtrl.isEnabled:
                    self.__preferredPosition = curCtrl.getDesiredShotPoint(ignoreAimingMode=True)
                forEach(lambda e: e.deactivate(), [ e for e in self._equipments.itervalues() if e.getStage() == EQUIPMENT_STAGES.PREPARING ])
                item.activate(entityName, avatar)
        return (result, error)


class _ReplayItem(_EquipmentItem):
    __slots__ = ('__cooldownTime',)

    def __init__(self, descriptor, quantity, stage, timeRemaining, totalTime, tag=None):
        super(_ReplayItem, self).__init__(descriptor, quantity, stage, timeRemaining, totalTime, tag)
        self.__cooldownTime = BigWorld.serverTime() + timeRemaining

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(_ReplayItem, self).update(quantity, stage, timeRemaining, totalTime)
        self.__cooldownTime = BigWorld.serverTime() + timeRemaining

    def getEntitiesIterator(self, avatar=None):
        return []

    def getGuiIterator(self, avatar=None):
        return []

    def canActivate(self, entityName=None, avatar=None):
        return (False, None)

    def getReplayTimeRemaining(self):
        return max(0, self.__cooldownTime - BigWorld.serverTime())

    def getCooldownPercents(self):
        totalTime = self.getTotalTime()
        timeRemaining = self.getReplayTimeRemaining()
        return round(float(totalTime - timeRemaining) / totalTime * 100.0) if totalTime > 0 else 0.0


class _ReplayMedKitItem(_ReplayItem):
    __slots__ = ('__cooldownTime',)

    def getEntitiesIterator(self, avatar=None):
        return vehicle_getter.TankmenStatesIterator(avatar_getter.getVehicleDeviceStates(avatar), avatar_getter.getVehicleTypeDescriptor(avatar))


class _ReplayRepairKitItem(_ReplayItem):
    __slots__ = ('__cooldownTime',)

    def getEntitiesIterator(self, avatar=None):
        return vehicle_getter.VehicleDeviceStatesIterator(avatar_getter.getVehicleDeviceStates(avatar), avatar_getter.getVehicleTypeDescriptor(avatar))


class _ReplayOrderItem(_ReplayItem):

    def deactivate(self):
        if self._descriptor is not None:
            super(_ReplayOrderItem, self).deactivate()
        return

    def update(self, quantity, stage, timeRemaining, totalTime):
        from AvatarInputHandler import MapCaseMode
        if stage == EQUIPMENT_STAGES.PREPARING and self._stage != stage:
            MapCaseMode.activateMapCase(self.getEquipmentID(), partial(self.deactivate))
        elif self._stage == EQUIPMENT_STAGES.PREPARING and self._stage != stage:
            MapCaseMode.turnOffMapCase(self.getEquipmentID())
        super(_ReplayOrderItem, self).update(quantity, stage, timeRemaining, totalTime)


class _ReplayArtilleryItem(_ReplayOrderItem):

    def getMarker(self):
        pass


class _ReplayBomberItem(_ReplayOrderItem):

    def getMarker(self):
        pass


class _ReplayReconItem(_ReplayOrderItem):

    def getMarker(self):
        pass


class _ReplaySmokeItem(_ReplayOrderItem):

    def getMarker(self):
        pass


class _ReplayAfterburningItem(_ReplayItem):
    __slots__ = ('__totalConsumingTime', '__totalRechargingTime', '_prevTimeRemaining')

    def __init__(self, descriptor, quantity, stage, timeRemaining, totalTime, tag=None):
        self.__totalConsumingTime = descriptor.maxAmount / descriptor.consumePerSec
        self.__totalRechargingTime = descriptor.maxAmount / descriptor.rechargePerSec
        self._prevTimeRemaining = -1
        super(_ReplayAfterburningItem, self).__init__(descriptor, quantity, stage, timeRemaining, totalTime, tag)

    def getTag(self):
        pass

    def update(self, quantity, stage, timeRemaining, totalTime):
        self._prevTimeRemaining = self._timeRemaining
        if stage == EQUIPMENT_STAGES.ACTIVE:
            self._animationType = ANIMATION_TYPES.MOVE_GREEN_BAR_DOWN + ANIMATION_TYPES.CENTER_COUNTER + ANIMATION_TYPES.GREEN_GLOW_SHOW + ANIMATION_TYPES.DARK_COLOR_TRANSFORM
            totalTime = self.__totalConsumingTime
        elif stage == EQUIPMENT_STAGES.READY:
            self._animationType = ANIMATION_TYPES.MOVE_GREEN_BAR_UP + ANIMATION_TYPES.SHOW_COUNTER_GREEN
            if self._stage != stage != EQUIPMENT_STAGES.COOLDOWN:
                self._animationType += ANIMATION_TYPES.GREEN_GLOW_HIDE
            totalTime = self.__totalRechargingTime
        elif stage == EQUIPMENT_STAGES.DEPLOYING:
            self._animationType = ANIMATION_TYPES.MOVE_ORANGE_BAR_UP + ANIMATION_TYPES.SHOW_COUNTER_ORANGE
            totalTime = timeRemaining
        elif stage == EQUIPMENT_STAGES.COOLDOWN:
            self._animationType = ANIMATION_TYPES.MOVE_ORANGE_BAR_UP + ANIMATION_TYPES.SHOW_COUNTER_ORANGE + ANIMATION_TYPES.FILL_PARTIALLY
            totalTime = timeRemaining = self.__totalRechargingTime
        super(_ReplayAfterburningItem, self).update(quantity, stage, timeRemaining, totalTime)

    @property
    def becomeReady(self):
        return self._prevTimeRemaining >= 0 and self._timeRemaining == -1 and self._prevStage == EQUIPMENT_STAGES.READY

    def _soundUpdate(self, prevQuantity, quantity):
        if self._stage == EQUIPMENT_STAGES.READY and self._prevStage in (EQUIPMENT_STAGES.DEPLOYING, EQUIPMENT_STAGES.UNAVAILABLE, EQUIPMENT_STAGES.COOLDOWN):
            EquipmentSound.playReady(self)
        if self.becomeReady:
            EquipmentSound.playReady(self)


class _ReplayLastChanceItem(_ReplayItem):
    __slots__ = ('__cooldownTime',)

    def __init__(self, descriptor, quantity, stage, timeRemaining, totalTime, tag=None):
        self.__cooldownTime = descriptor.cooldownTime
        super(_ReplayLastChanceItem, self).__init__(descriptor, quantity, stage, timeRemaining, totalTime, tag)

    def update(self, quantity, stage, timeRemaining, totalTime):
        if stage == EQUIPMENT_STAGES.UNAVAILABLE:
            quantity = 0
        if stage == EQUIPMENT_STAGES.COOLDOWN:
            quantity = 1
            totalTime = self.__cooldownTime
        super(_ReplayLastChanceItem, self).update(quantity, stage, timeRemaining, totalTime)


def _replayTriggerItemFactory(descriptor, quantity, stage, timeRemaining, totalTime, tag=None):
    if descriptor.name.startswith('artillery'):
        return _ReplayArtilleryItem(descriptor, quantity, stage, timeRemaining, totalTime, tag)
    if descriptor.name.startswith('bomber'):
        return _ReplayBomberItem(descriptor, quantity, stage, timeRemaining, totalTime, tag)
    if descriptor.name.startswith('recon'):
        return _ReplayReconItem(descriptor, quantity, stage, timeRemaining, totalTime, tag)
    if descriptor.name.startswith('smoke'):
        return _ReplaySmokeItem(descriptor, quantity, stage, timeRemaining, totalTime, tag)
    if descriptor.name.endswith('afterburning'):
        return _ReplayAfterburningItem(descriptor, quantity, stage, timeRemaining, totalTime, tag)
    return _ReplayLastChanceItem(descriptor, quantity, stage, timeRemaining, totalTime, tag) if descriptor.name.startswith('lastchance') else _ReplayItem(descriptor, quantity, stage, timeRemaining, totalTime, tag)


_REPLAY_EQUIPMENT_TAG_TO_ITEM = {'fuel': _ReplayItem,
 'stimulator': _ReplayItem,
 'trigger': _replayTriggerItemFactory,
 'extinguisher': _ReplayItem,
 'medkit': _ReplayMedKitItem,
 'repairkit': _ReplayRepairKitItem}

class EquipmentsReplayPlayer(EquipmentsController):
    __slots__ = ('__callbackID', '__callbackTimeID', '__percentGetters', '__percents', '__timeGetters', '__times')

    def __init__(self):
        super(EquipmentsReplayPlayer, self).__init__()
        self.__callbackID = None
        self.__callbackTimeID = None
        self.__percentGetters = {}
        self.__percents = {}
        self.__timeGetters = {}
        self.__times = {}
        return

    def clear(self, leave=True):
        if leave:
            if self.__callbackID is not None:
                BigWorld.cancelCallback(self.__callbackID)
                self.__callbackID = None
            if self.__callbackTimeID is not None:
                BigWorld.cancelCallback(self.__callbackTimeID)
                self.__callbackTimeID = None
            self.__percents.clear()
            self.__percentGetters.clear()
            self.__times.clear()
            self.__timeGetters.clear()
        super(EquipmentsReplayPlayer, self).clear(leave)
        return

    def setEquipment(self, intCD, quantity, stage, timeRemaining, totalTime):
        super(EquipmentsReplayPlayer, self).setEquipment(intCD, quantity, stage, timeRemaining, totalTime)
        self.__percents.pop(intCD, None)
        self.__percentGetters.pop(intCD, None)
        self.__times.pop(intCD, None)
        self.__timeGetters.pop(intCD, None)
        if stage in (EQUIPMENT_STAGES.DEPLOYING,
         EQUIPMENT_STAGES.COOLDOWN,
         EQUIPMENT_STAGES.SHARED_COOLDOWN,
         EQUIPMENT_STAGES.ACTIVE) or stage == EQUIPMENT_STAGES.READY and self.getEquipment(intCD).getTimeRemaining() != -1:
            equipment = self._equipments[intCD]
            self.__percentGetters[intCD] = equipment.getCooldownPercents
            if self.__callbackID is not None:
                BigWorld.cancelCallback(self.__callbackID)
                self.__callbackID = None
            if equipment.getTotalTime() > 0:
                self.__timeGetters[intCD] = equipment.getReplayTimeRemaining
                if self.__callbackTimeID is not None:
                    BigWorld.cancelCallback(self.__callbackTimeID)
                    self.__callbackTimeID = None
            self.__timeLoop()
            self.__timeLoopInSeconds()
        return

    @classmethod
    def createItem(cls, descriptor, quantity, stage, timeRemaining, totalTime):
        tag = _getSupportedTag(descriptor)
        if tag:
            clazz = _REPLAY_EQUIPMENT_TAG_TO_ITEM[tag]
            item = clazz(descriptor, quantity, stage, timeRemaining, totalTime, tag)
        else:
            item = _ReplayItem(descriptor, quantity, stage, timeRemaining, totalTime)
        return item

    def getActivationCode(self, intCD, entityName=None, avatar=None):
        return None

    def canActivate(self, intCD, entityName=None, avatar=None):
        return (False, None)

    def changeSetting(self, intCD, entityName=None, avatar=None):
        return (False, None)

    def changeSettingByTag(self, tag, entityName=None, avatar=None):
        return (False, None)

    def __timeLoop(self):
        self.__callbackID = None
        self.__tick()
        self.__callbackID = BigWorld.callback(0.1, self.__timeLoop)
        return

    def __timeLoopInSeconds(self):
        self.__callbackTimeID = None
        self.__tickInSeconds()
        self.__callbackTimeID = BigWorld.callback(0.3, self.__timeLoopInSeconds)
        return

    def __tick(self):
        for intCD, percentGetter in self.__percentGetters.iteritems():
            percent = percentGetter()
            currentPercent = self.__percents.get(intCD)
            if currentPercent != percent:
                self.__percents[intCD] = percent
                self.onEquipmentCooldownInPercent(intCD, percent)

    def __tickInSeconds(self):
        for intCD, timeGetter in self.__timeGetters.iteritems():
            time = timeGetter()
            currentTime = self.__times.get(intCD)
            if currentTime != time:
                self.__times[intCD] = time
                self.onEquipmentCooldownTime(intCD, time, time == 0, time == 0)


__all__ = ('EquipmentsController', 'EquipmentsReplayPlayer')
