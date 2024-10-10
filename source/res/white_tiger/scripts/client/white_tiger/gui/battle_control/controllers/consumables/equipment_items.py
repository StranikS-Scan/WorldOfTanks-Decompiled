# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/battle_control/controllers/consumables/equipment_items.py
import weakref
from functools import partial
import BigWorld
from constants import EQUIPMENT_STAGES
from equipment_sound import WtEquipmentSound
from gui.battle_control import avatar_getter
from gui.battle_control.controllers.consumables.equipment_ctrl import _ActivationError, InCooldownError, _TriggerItem, _AfterburningItem, _EQUIPMENT_TAG_TO_ITEM
from gui.Scaleform.genConsts.ANIMATION_TYPES import ANIMATION_TYPES
from gui.Scaleform.genConsts.BATTLE_CONSUMABLES_PANEL_TAGS import BATTLE_CONSUMABLES_PANEL_TAGS
from gui.Scaleform.genConsts.BATTLE_MARKERS_CONSTS import BATTLE_MARKERS_CONSTS
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from TeleportKeyPoint import TeleportKeyPoint
from gui.battle_control.controllers.consumables.equipment_ctrl import EquipmentSound

class WtHealthAtFullHP(_ActivationError):

    def __new__(cls, name):
        return super(WtHealthAtFullHP, cls).__new__(cls, 'wtEventTankIsAtFullHP', {'name': name})

    def __init__(self, name):
        super(WtHealthAtFullHP, self).__init__('wtEventTankIsAtFullHP', {'name': name})


class _LockableItem(_TriggerItem):

    def __init__(self, descriptor, quantity, stage, timeRemaining, totalTime, tags):
        super(_LockableItem, self).__init__(descriptor, quantity, stage, timeRemaining, totalTime, tags)
        self._isLocked = False

    def setAnimationType(self, animationType):
        self._animationType = animationType

    def getQuantity(self):
        return self._quantity if not self._isLocked else 0

    def getTimeRemaining(self):
        return self._timeRemaining if not self._isLocked else 0

    def getTotalTime(self):
        return self._totalTime if not self._isLocked else 0

    def setLocked(self, isLocked):
        self._isLocked = isLocked

    def isLocked(self):
        return self._isLocked


class _WtAfterburningItem(_AfterburningItem, _LockableItem):
    __slots__ = ()
    _FULL_CHARGE_DELAY_SOUND_TIME = 4.0

    def __init__(self, descriptor, quantity, stage, timeRemaining, _, tags=None):
        totalTime = descriptor.cooldownSeconds
        super(_WtAfterburningItem, self).__init__(descriptor, quantity, stage, timeRemaining, totalTime, tags)

    def canActivate(self, entityName=None, avatar=None):
        return (False, _ActivationError('equipmentAlreadyActivated', {'name': self._descriptor.userString})) if self._stage == EQUIPMENT_STAGES.ACTIVE else super(_WtAfterburningItem, self).canActivate(entityName, avatar)

    def getGuiIterator(self, avatar=None):
        return []

    def getTags(self):
        return self._tags

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(_WtAfterburningItem, self).update(quantity, stage, timeRemaining, totalTime)
        if stage == EQUIPMENT_STAGES.ACTIVE:
            self._totalTime = timeRemaining
        if stage == EQUIPMENT_STAGES.COOLDOWN:
            self._animationType = ANIMATION_TYPES.MOVE_ORANGE_BAR_UP | ANIMATION_TYPES.SHOW_COUNTER_ORANGE | ANIMATION_TYPES.DARK_COLOR_TRANSFORM

    def _soundUpdate(self, prevQuantity, quantity):
        if self.becomeReady:
            EquipmentSound.playReady(self)

    def _playReady(self):
        pass


class _EventItem(_LockableItem):

    def __init__(self, descriptor, quantity, stage, timeRemaining, _, tags=None):
        totalTime = descriptor.cooldownSeconds
        super(_EventItem, self).__init__(descriptor, quantity, stage, timeRemaining, totalTime, tags)

    def getMarker(self):
        pass

    def getEntitiesIterator(self, avatar=None):
        return []

    def getGuiIterator(self, avatar=None):
        return []

    def canActivate(self, entityName=None, avatar=None):
        if self._isLocked or self._timeRemaining > 0 and self._stage and self._stage in (EQUIPMENT_STAGES.DEPLOYING, EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.SHARED_COOLDOWN):
            result = False
            error = InCooldownError(self._descriptor.userString)
            return (result, error)
        return super(_EventItem, self).canActivate(entityName, avatar)

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(_EventItem, self).update(quantity, stage, timeRemaining, totalTime)
        if stage in (EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.READY):
            self._totalTime = totalTime
        elif stage == EQUIPMENT_STAGES.ACTIVE:
            self._totalTime = timeRemaining
        elif stage == EQUIPMENT_STAGES.PREPARING:
            self._totalTime = 0


class _WtSelfRepairItem(_EventItem):

    def canActivate(self, entityName=None, avatar=None):
        if self._stage == EQUIPMENT_STAGES.COOLDOWN:
            result = False
            error = InCooldownError(self._descriptor.userString)
            return (result, error)
        else:
            if self._stage == EQUIPMENT_STAGES.READY:
                vehicleID = avatar_getter.getPlayerVehicleID()
                if vehicleID is not None:
                    vehicle = BigWorld.entities.get(vehicleID)
                    if vehicle and vehicle.health == vehicle.maxHealth:
                        result = False
                        error = WtHealthAtFullHP(self._descriptor.userString)
                        return (result, error)
            return super(_WtSelfRepairItem, self).canActivate(entityName, avatar)


class _ComponentEquipment(_EventItem):

    def canActivate(self, entityName=None, avatar=None):
        result, error = super(_ComponentEquipment, self).canActivate(entityName, avatar)
        if not result:
            return (result, error)
        else:
            vehicleID = avatar_getter.getPlayerVehicleID()
            if vehicleID is not None:
                vehicle = BigWorld.entities.get(vehicleID)
                if vehicle is not None:
                    component = getattr(vehicle, self._descriptor.name, None)
                    if component:
                        res, keyError = component.canActivate()
                        return (res, _ActivationError(keyError, {'name': self._descriptor.userString}) if keyError else None)
            return (True, None)


class _EventPassiveItem(_EventItem):

    def getActivationCode(self, entityName=None, avatar=None):
        return None

    def canActivate(self, entityName=None, avatar=None):
        return (False, None)

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(_EventPassiveItem, self).update(self._quantity, stage, timeRemaining, totalTime)

    def activate(self, entityName=None, avatar=None):
        self._quantity = 1
        self._update(avatar)

    def deactivate(self, avatar=None):
        self._quantity = 0
        self._update(avatar)

    def _update(self, avatar):
        if avatar is not None:
            avatar.guiSessionProvider.shared.equipments.setEquipment(self._descriptor.compactDescr, 0, 0, 0, 0)
        return


class _ShellOverrideItem(_ComponentEquipment):

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(_ShellOverrideItem, self).update(quantity, stage, timeRemaining, totalTime)
        if stage == EQUIPMENT_STAGES.READY:
            self._timeRemaining = 0
            self._totalTime = 0
        elif stage == EQUIPMENT_STAGES.ACTIVE:
            self._timeRemaining = -1
            self._totalTime = 0


class _TeleportItem(_LockableItem):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, descriptor, quantity, stage, timeRemaining, _, tags=None):
        totalTime = descriptor.cooldownSeconds
        super(_TeleportItem, self).__init__(descriptor, quantity, stage, timeRemaining, totalTime, tags)

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(_TeleportItem, self).update(quantity, stage, timeRemaining, totalTime)
        if stage == EQUIPMENT_STAGES.DEPLOYING:
            self._totalTime = self._descriptor.deploySeconds
        elif stage == EQUIPMENT_STAGES.COOLDOWN:
            self._totalTime = self._descriptor.cooldownSeconds
        elif stage == EQUIPMENT_STAGES.ACTIVE:
            self._totalTime = timeRemaining
        elif stage == EQUIPMENT_STAGES.PREPARING:
            self._totalTime = 0
        teleport = self._sessionProvider.dynamic.teleport
        if stage != EQUIPMENT_STAGES.PREPARING and teleport.isSpawnPointsVisible:
            teleport.closeSpawnPoints()

    def canActivate(self, entityName=None, avatar=None):
        if self._isLocked or self._timeRemaining > 0 and self._stage and self._stage in (EQUIPMENT_STAGES.DEPLOYING, EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.SHARED_COOLDOWN):
            result = False
            error = InCooldownError(self._descriptor.userString)
            return (result, error)
        return super(_TeleportItem, self).canActivate(entityName, avatar)

    def activate(self, entityName=None, avatar=None):
        teleport = self._sessionProvider.dynamic.teleport
        if teleport is not None:
            points = [ {'guid': udo.guid,
             'position': (udo.position.x, udo.position.z),
             'index': udo.positionNumber} for udo in BigWorld.userDataObjects.values() if isinstance(udo, TeleportKeyPoint) ]
            teleport.setEquipment(weakref.proxy(self))
            teleport.showSpawnPoints(points)
            self._stage = EQUIPMENT_STAGES.PREPARING
        return

    def deactivate(self):
        teleport = self._sessionProvider.dynamic.teleport
        if teleport is not None:
            teleport.closeSpawnPoints()
            self._stage = EQUIPMENT_STAGES.READY
        return

    def getEntitiesIterator(self, avatar=None):
        return []

    def getGuiIterator(self, avatar=None):
        return []

    def apply(self, pointGuid):
        avatar_getter.activateVehicleEquipment(self.getEquipmentID(), pointGuid)


class _HyperionItem(_EventItem):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def getMarker(self):
        pass

    def getMarkerColor(self):
        return BATTLE_MARKERS_CONSTS.COLOR_YELLOW

    def getEntitiesIterator(self, avatar=None):
        return []

    def getGuiIterator(self, avatar=None):
        return []

    def activate(self, entityName=None, avatar=None):
        from AvatarInputHandler import MapCaseMode
        self._stage = EQUIPMENT_STAGES.PREPARING
        MapCaseMode.activateMapCase(self.getEquipmentID(), partial(self.deactivate), self.getAimingControlMode())
        self.__updateEquipmentState()

    def deactivate(self):
        self.__cancelAiming(True)
        self._stage = EQUIPMENT_STAGES.READY
        self.__updateEquipmentState()

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(_HyperionItem, self).update(quantity, stage, timeRemaining, totalTime)
        if self._stage in (EQUIPMENT_STAGES.EXHAUSTED, EQUIPMENT_STAGES.READY):
            self.__cancelAiming()

    def getStrikeSelector(self):
        from AvatarInputHandler import MapCaseMode
        return MapCaseMode.HyperionStrikeSelector

    def getAimingControlMode(self):
        from AvatarInputHandler.MapCaseMode import HyperionMapCaseControlMode
        return HyperionMapCaseControlMode

    def __cancelAiming(self, playCancelSound=False):
        if playCancelSound:
            WtEquipmentSound.playCancel(self)
        from AvatarInputHandler import MapCaseMode
        MapCaseMode.turnOffMapCase(self.getEquipmentID(), self.getAimingControlMode())

    def __updateEquipmentState(self):
        eqCtrl = self.__sessionProvider.shared.equipments
        eq = eqCtrl.getEquipment(self._descriptor.compactDescr)
        eqCtrl.onEquipmentUpdated(self._descriptor.compactDescr, eq)

    def getTotalTime(self):
        return self._descriptor.deploySeconds if not self._isLocked else 0


def isWtEventItem(item):
    return isinstance(item, (_EventItem,
     _WtAfterburningItem,
     _WtSelfRepairItem,
     _TeleportItem,
     _HyperionItem))


def _eventItemFactory(descriptor, quantity, stage, timeRemaining, totalTime, tag=None):
    if descriptor.name.lower().endswith('afterburning_wt'):
        return _WtAfterburningItem(descriptor, quantity, stage, timeRemaining, totalTime, tag)
    if descriptor.name.lower().endswith('selfrepair_wt'):
        return _WtSelfRepairItem(descriptor, quantity, stage, timeRemaining, totalTime, tag)
    if descriptor.name.lower().endswith('teleport_wt'):
        return _TeleportItem(descriptor, quantity, stage, timeRemaining, totalTime, tag)
    if 'eventShellOverride' in descriptor.tags:
        return _ShellOverrideItem(descriptor, quantity, stage, timeRemaining, totalTime, tag)
    return _HyperionItem(descriptor, quantity, stage, timeRemaining, totalTime, tag) if descriptor.name.lower().endswith('hyperion_wt') else _EventItem(descriptor, quantity, stage, timeRemaining, totalTime, tag)


def _eventPassiveItemFactory(descriptor, quantity, stage, timeRemaining, totalTime, tag=None):
    return _EventPassiveItem(descriptor, 0, stage, timeRemaining, totalTime, tag)


def registerTagsToEventItemMapping():
    _EQUIPMENT_TAG_TO_ITEM.update({(BATTLE_CONSUMABLES_PANEL_TAGS.EVENT_ITEM,): _eventItemFactory})
    _EQUIPMENT_TAG_TO_ITEM.update({(BATTLE_CONSUMABLES_PANEL_TAGS.EVENT_PASSIVE_ITEM,): _eventPassiveItemFactory})
