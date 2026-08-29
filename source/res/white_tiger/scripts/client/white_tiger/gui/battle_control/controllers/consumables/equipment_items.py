# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/battle_control/controllers/consumables/equipment_items.py
import weakref
import BigWorld
import SoundGroups
from items import vehicles
from constants import EQUIPMENT_STAGES
from gui.battle_control import avatar_getter
from gui.battle_control.controllers.consumables.equipment_ctrl import _ActivationError, InCooldownError, _TriggerItem, _AfterburningItem, _RepairKitItem, _MedKitItem, _OrderItem
from gui.Scaleform.genConsts.ANIMATION_TYPES import ANIMATION_TYPES
from gui.Scaleform.genConsts.BATTLE_MARKERS_CONSTS import BATTLE_MARKERS_CONSTS
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from TeleportKeyPoint import TeleportKeyPoint
from gui.battle_control.controllers.consumables.equipment_ctrl import EquipmentSound
from cgf_components import wt_helpers
from white_tiger.gui.Scaleform.genConsts.WHITE_TIGER_BATTLE_CONSUMABLES_PANEL_TAGS import WHITE_TIGER_BATTLE_CONSUMABLES_PANEL_TAGS
from gui.Scaleform.genConsts.BATTLE_CONSUMABLES_PANEL_TAGS import BATTLE_CONSUMABLES_PANEL_TAGS

class _LockableItem(_TriggerItem):

    def __init__(self, descriptor, quantity, stage, timeRemaining, totalTime, tags):
        self._isLocked = False
        super(_LockableItem, self).__init__(descriptor, quantity, stage, timeRemaining, totalTime, tags)

    def setAnimationType(self, animationType):
        self._animationType = animationType

    def getQuantity(self):
        return self._quantity if not self._isLocked else 0

    def setLocked(self, isLocked):
        self._isLocked = isLocked

    def isLocked(self):
        return self._isLocked

    def canActivate(self, entityName=None, avatar=None):
        if self._isLocked or self._stage == EQUIPMENT_STAGES.UNAVAILABLE:
            result = False
            error = None
            if wt_helpers.isBoss():
                error = WtNoActiveShieldOnBoss(self._descriptor.userString)
            else:
                error = WtHunterAbilitiesDisabled(self._descriptor.userString)
            return (result, error)
        else:
            return super(_LockableItem, self).canActivate(entityName, avatar)

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(_LockableItem, self).update(quantity, stage, timeRemaining, totalTime)
        if stage == EQUIPMENT_STAGES.UNAVAILABLE:
            self._quantity = 1
            self._timeRemaining = 0
            self._totalTime = 0

    def getEntitiesIterator(self, avatar=None):
        return []


class WTRepairKit(_RepairKitItem, _LockableItem):

    def canActivate(self, entityName=None, avatar=None):
        if self._isLocked or self._stage and self._stage == EQUIPMENT_STAGES.UNAVAILABLE:
            result = False
            error = WtHunterAbilitiesDisabled(self._descriptor.userString)
            return (result, error)
        return super(WTRepairKit, self).canActivate(entityName, avatar)

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(WTRepairKit, self).update(quantity, stage, timeRemaining, totalTime)
        if stage == EQUIPMENT_STAGES.UNAVAILABLE:
            self._quantity = 1
            self._timeRemaining = 0
            self._totalTime = 0

    def getTags(self):
        return (BATTLE_CONSUMABLES_PANEL_TAGS.REPAIR_KIT,)


class WTMedKitItem(_MedKitItem, _LockableItem):
    __FACTOR_APPLIER_KEY = 'wtFactorAppliers_{}'
    __ABILITY_LOCK_KEY = 'wtAbilityLock_{}'

    def __init__(self, descriptor, quantity, stage, timeRemaining, totalTime, tags):
        super(WTMedKitItem, self).__init__(descriptor, quantity, stage, timeRemaining, totalTime, tags)
        self.__debuffComponentsName = self.__getDebuffComponentsName()

    def canActivate(self, entityName=None, avatar=None):
        if self._isLocked or self._stage and self._stage == EQUIPMENT_STAGES.UNAVAILABLE:
            result = False
            error = WtHunterAbilitiesDisabled(self._descriptor.userString)
            return (result, error)
        else:
            if self._stage and self._stage == EQUIPMENT_STAGES.READY:
                for componentKey in self.__debuffComponentsName:
                    component = BigWorld.player().vehicle.dynamicComponents.get(componentKey)
                    if component and component.finishTime != 0:
                        return (True, None)

            return super(WTMedKitItem, self).canActivate(entityName, avatar)

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(WTMedKitItem, self).update(quantity, stage, timeRemaining, totalTime)
        if stage == EQUIPMENT_STAGES.UNAVAILABLE:
            self._quantity = 1
            self._timeRemaining = 0
            self._totalTime = 0

    def __getDebuffComponentsName(self):
        componentsName = []
        for abilityName in self.getDescriptor().removeDebuffsFromAbilities:
            eqId = vehicles.g_cache.equipmentIDs()[abilityName]
            for key in [self.__FACTOR_APPLIER_KEY, self.__ABILITY_LOCK_KEY]:
                resultKey = key.format(eqId)
                componentsName.append(resultKey)

        return componentsName

    def getTags(self):
        return (BATTLE_CONSUMABLES_PANEL_TAGS.MED_KIT,)


class _PassiveAbility(_TriggerItem):

    def __init__(self, *args, **kwargs):
        super(_PassiveAbility, self).__init__(*args, **kwargs)
        self._consumablePanel = None
        self._idx = None
        return

    def canActivate(self, entityName=None, avatar=None):
        return (False, None)

    def getEntitiesIterator(self, avatar=None):
        return []

    def getGuiIterator(self, avatar=None):
        return []

    def getTags(self):
        return (WHITE_TIGER_BATTLE_CONSUMABLES_PANEL_TAGS.WT_PASSIVE_ABILITY_ITEM,)

    def init(self, consumablePanelObj, idx):
        self._consumablePanel = consumablePanelObj
        self._idx = idx

    def clear(self):
        super(_PassiveAbility, self).clear()
        self._consumablePanel = None
        self._idx = None
        return


class _WTOrderItem(_OrderItem):

    @property
    def becomeActive(self):
        return self._prevStage == EQUIPMENT_STAGES.PREPARING and self._stage == EQUIPMENT_STAGES.ACTIVE

    @property
    def becomeCanceled(self):
        return self._prevStage == EQUIPMENT_STAGES.PREPARING and self._stage == EQUIPMENT_STAGES.READY

    def _soundUpdate(self, prevQuantity, quantity):
        if self.becomeReady:
            self._playReady()
        if self.becomeActive:
            self._playActive()
        elif self.becomeCanceled:
            self._playCancel()

    def _playReady(self):
        sound = self.getDescriptor().soundNotification
        if sound is not None:
            avatar_getter.getSoundNotifications().play(sound)
        return

    def _playActive(self):
        sound = self.getDescriptor().activationSound
        if sound is not None:
            SoundGroups.g_instance.playSound2D(sound)
        return

    def _playCancel(self):
        sound = self.getDescriptor().soundPressedCancel
        if sound is not None:
            SoundGroups.g_instance.playSound2D(sound)
        return


class WTPassiveHeal(_PassiveAbility):

    @property
    def becomeActive(self):
        return self._stage == EQUIPMENT_STAGES.ACTIVE and self._prevStage == EQUIPMENT_STAGES.NOT_RUNNING


class WTUnionStrength(_PassiveAbility):
    pass


class WTInvisibilityModA(_LockableItem):
    pass


class WTInvisibilityModB(_LockableItem):
    pass


class WTCloneItem(_WTOrderItem, _LockableItem):

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(WTCloneItem, self).update(quantity, stage, timeRemaining, totalTime)
        if stage == EQUIPMENT_STAGES.ACTIVE and self._prevStage != EQUIPMENT_STAGES.ACTIVE:
            self._animationType = ANIMATION_TYPES.MOVE_GREEN_BAR_DOWN | ANIMATION_TYPES.CENTER_COUNTER | ANIMATION_TYPES.GREEN_GLOW_SHOW | ANIMATION_TYPES.DARK_COLOR_TRANSFORM
            self._totalTime = self._descriptor.consumeSeconds
        elif stage == EQUIPMENT_STAGES.COOLDOWN:
            self._animationType = ANIMATION_TYPES.MOVE_ORANGE_BAR_UP | ANIMATION_TYPES.SHOW_COUNTER_ORANGE | ANIMATION_TYPES.FILL_PARTIALLY
            self._totalTime = self._descriptor.cooldownSeconds

    def getAimingControlMode(self):
        from AvatarInputHandler import MapCaseMode
        return MapCaseMode.ArcadeMapCaseControlMode

    def getAnimationType(self):
        if self._stage == EQUIPMENT_STAGES.ACTIVE:
            return ANIMATION_TYPES.MOVE_GREEN_BAR_DOWN | ANIMATION_TYPES.SHOW_COUNTER_GREEN
        return ANIMATION_TYPES.MOVE_ORANGE_BAR_UP | ANIMATION_TYPES.SHOW_COUNTER_ORANGE | ANIMATION_TYPES.FILL_PARTIALLY if self._stage == EQUIPMENT_STAGES.COOLDOWN else super(WTCloneItem, self).getAnimationType()

    def getEntitiesIterator(self, avatar=None):
        return []

    def canActivate(self, entityName=None, avatar=None):
        if self._isLocked or self._stage == EQUIPMENT_STAGES.UNAVAILABLE:
            return (False, WtHunterAbilitiesDisabled(self._descriptor.userString))
        if self._stage and self._stage == EQUIPMENT_STAGES.COOLDOWN:
            result = False
            error = InCooldownError(self._descriptor.userString)
            return (result, error)
        return super(WTCloneItem, self).canActivate(entityName, avatar)


class WTStunArea(_LockableItem):
    pass


class WTStunAreaModA(WTStunArea):
    pass


class WTChargedShot(_LockableItem):

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(WTChargedShot, self).update(quantity, stage, timeRemaining, totalTime)
        if stage == EQUIPMENT_STAGES.ACTIVE:
            self._totalTime = 0


class WTExplosiveShot(WTChargedShot):
    pass


class WTNitro(_LockableItem):

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(WTNitro, self).update(quantity, stage, timeRemaining, totalTime)
        if stage == EQUIPMENT_STAGES.ACTIVE:
            self._totalTime = self._descriptor.consumeSeconds


class WTDamageShield(_LockableItem):

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(WTDamageShield, self).update(quantity, stage, timeRemaining, totalTime)
        if stage == EQUIPMENT_STAGES.ACTIVE:
            self._totalTime = self._descriptor.durationSeconds


class WTImpulseModA(_LockableItem):

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(WTImpulseModA, self).update(quantity, stage, timeRemaining, totalTime)
        if stage == EQUIPMENT_STAGES.ACTIVE:
            self._totalTime = self._descriptor.consumeSeconds


class WtHealthAtFullHP(_ActivationError):

    def __new__(cls, name):
        return super(WtHealthAtFullHP, cls).__new__(cls, 'wtEventTankIsAtFullHP', {'name': name})

    def __init__(self, name):
        super(WtHealthAtFullHP, self).__init__('wtEventTankIsAtFullHP', {'name': name})


class WtHunterAbilitiesDisabled(_ActivationError):

    def __new__(cls, name):
        return super(WtHunterAbilitiesDisabled, cls).__new__(cls, 'wtHunterAbilitiesDisabled', {'name': name})

    def __init__(self, name):
        super(WtHunterAbilitiesDisabled, self).__init__('wtHunterAbilitiesDisabled', {'name': name})


class WtNoActiveShieldOnBoss(_ActivationError):

    def __new__(cls, name):
        return super(WtNoActiveShieldOnBoss, cls).__new__(cls, 'wtNoActiveShieldOnBoss', {'name': name})

    def __init__(self, name):
        super(WtNoActiveShieldOnBoss, self).__init__('wtNoActiveShieldOnBoss', {'name': name})


class _WtAfterburningItem(_LockableItem, _AfterburningItem):
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
        if self._timeRemaining > 0 and self._stage and self._stage in (EQUIPMENT_STAGES.DEPLOYING, EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.SHARED_COOLDOWN):
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


class _ShellOverrideItem(_ComponentEquipment):

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(_ShellOverrideItem, self).update(quantity, stage, timeRemaining, totalTime)
        if stage == EQUIPMENT_STAGES.READY:
            self._timeRemaining = 0
            self._totalTime = 0
        elif stage == EQUIPMENT_STAGES.ACTIVE:
            self._timeRemaining = -1
            self._totalTime = 0


class WTTeleportModA(_LockableItem):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(WTTeleportModA, self).update(quantity, stage, timeRemaining, totalTime)
        if stage == EQUIPMENT_STAGES.COOLDOWN:
            self._totalTime = self._descriptor.cooldownSeconds
        elif stage == EQUIPMENT_STAGES.ACTIVE:
            self._totalTime = self._descriptor.consumeSeconds
        elif stage == EQUIPMENT_STAGES.READY:
            self._totalTime = 0
        teleport = self._sessionProvider.dynamic.teleport
        if teleport.isSpawnPointsVisible:
            teleport.closeSpawnPoints()

    def setLocked(self, isLocked):
        super(WTTeleportModA, self).setLocked(isLocked)
        teleport = self._sessionProvider.dynamic.teleport
        if self._isLocked and teleport.isSpawnPointsVisible:
            teleport.closeSpawnPoints()

    def canActivate(self, entityName=None, avatar=None):
        if not self._isLocked and self._timeRemaining > 0 and self._stage and self._stage in (EQUIPMENT_STAGES.DEPLOYING, EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.SHARED_COOLDOWN):
            result = False
            error = InCooldownError(self._descriptor.userString)
            return (result, error)
        return super(WTTeleportModA, self).canActivate(entityName, avatar)

    def activate(self, entityName=None, avatar=None):
        teleport = self._sessionProvider.dynamic.teleport
        if teleport is not None:
            points = [ {'guid': udo.guid,
             'position': (udo.position.x, udo.position.z),
             'index': udo.positionNumber} for udo in BigWorld.userDataObjects.values() if isinstance(udo, TeleportKeyPoint) ]
            teleport.setEquipment(weakref.proxy(self))
            teleport.showSpawnPoints(points)
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


class WTTeleportModB(WTTeleportModA):
    pass


class WTHyperionModA(_WTOrderItem, _LockableItem):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def getMarker(self):
        pass

    def getMarkerColor(self):
        return BATTLE_MARKERS_CONSTS.COLOR_YELLOW

    def getEntitiesIterator(self, avatar=None):
        return []

    def getGuiIterator(self, avatar=None):
        return []

    def canActivate(self, entityName=None, avatar=None):
        if self._isLocked or self._stage == EQUIPMENT_STAGES.UNAVAILABLE:
            return (False, WtNoActiveShieldOnBoss(self._descriptor.userString))
        if self._stage and self._stage == EQUIPMENT_STAGES.COOLDOWN:
            result = False
            error = InCooldownError(self._descriptor.userString)
            return (result, error)
        return super(WTHyperionModA, self).canActivate(entityName, avatar)

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(WTHyperionModA, self).update(quantity, stage, timeRemaining, totalTime)
        if stage in (EQUIPMENT_STAGES.COOLDOWN, EQUIPMENT_STAGES.READY):
            self._totalTime = self._descriptor.cooldownSeconds
        elif stage == EQUIPMENT_STAGES.DEPLOYING:
            self._totalTime = 0
        elif stage == EQUIPMENT_STAGES.ACTIVE:
            self._totalTime = self._descriptor.chargingDelay

    def getAnimationType(self):
        if self._stage == EQUIPMENT_STAGES.ACTIVE:
            return ANIMATION_TYPES.MOVE_ORANGE_BAR_DOWN
        return ANIMATION_TYPES.DARK_COLOR_TRANSFORM if self._stage == EQUIPMENT_STAGES.EXHAUSTED else super(WTHyperionModA, self).getAnimationType()

    def getAimingControlMode(self):
        from white_tiger.avatar_input_handler.wt_map_case_mode import HyperionMapCaseControlMode
        return HyperionMapCaseControlMode


class WTHyperionModB(WTHyperionModA):
    pass


class WTBarrier(_LockableItem):

    def __init__(self, descriptor, quantity, stage, timeRemaining, totalTime, tags):
        super(WTBarrier, self).__init__(descriptor, quantity, stage, timeRemaining, totalTime, tags)
        self.__preparingTime = 0

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(WTBarrier, self).update(quantity, stage, timeRemaining, totalTime)
        if stage == EQUIPMENT_STAGES.COOLDOWN:
            self._totalTime = self._descriptor.cooldownSeconds
        else:
            self._totalTime = 0

    def canActivate(self, entityName=None, avatar=None):
        result = True
        error = None
        if self._isLocked or self._stage == EQUIPMENT_STAGES.UNAVAILABLE:
            result = False
            error = WtHunterAbilitiesDisabled(self._descriptor.userString)
            return (result, error)
        else:
            if self._stage and self._stage == EQUIPMENT_STAGES.COOLDOWN:
                result = False
                error = InCooldownError(self._descriptor.userString)
            return (result, error)

    def getEntitiesIterator(self, avatar=None):
        return []


class WTMissile(_LockableItem):

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(WTMissile, self).update(quantity, stage, timeRemaining, totalTime)
        if stage == EQUIPMENT_STAGES.ACTIVE:
            self._totalTime = self._descriptor.consumeSeconds
        elif stage == EQUIPMENT_STAGES.COOLDOWN:
            self._totalTime = self._descriptor.cooldownSeconds
        else:
            self._totalTime = 0

    def getEntitiesIterator(self, avatar=None):
        return []


class WTVampirism(_PassiveAbility):
    pass


class WTDecreaseReloadTime(_PassiveAbility):
    pass


class WTGroupRepair(_LockableItem):

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(WTGroupRepair, self).update(quantity, stage, timeRemaining, totalTime)
        if stage == EQUIPMENT_STAGES.COOLDOWN:
            self._totalTime = self._descriptor.cooldownSeconds
        else:
            self._totalTime = 0

    def canActivate(self, entityName=None, avatar=None):
        result = True
        error = None
        if self._isLocked or self._stage == EQUIPMENT_STAGES.UNAVAILABLE:
            result = False
            error = WtHunterAbilitiesDisabled(self._descriptor.userString)
            return (result, error)
        else:
            if self._stage and self._stage == EQUIPMENT_STAGES.COOLDOWN:
                result = False
                error = InCooldownError(self._descriptor.userString)
            return (result, error)

    def getEntitiesIterator(self, avatar=None):
        return []


class WTSmokeScreen(_LockableItem):

    def getEntitiesIterator(self, avatar=None):
        return []


class WTPlasmaRetention(_PassiveAbility):
    pass


class WTExtractorShot(_LockableItem):

    def getEntitiesIterator(self, avatar=None):
        return []


def isWtEventItem(item):
    return isinstance(item, (WTRepairKit,
     WTMedKitItem,
     WTInvisibilityModA,
     WTInvisibilityModB,
     WTHyperionModA,
     WTHyperionModB))


class WTIncreaseDamage(_LockableItem):

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(WTIncreaseDamage, self).update(quantity, stage, timeRemaining, totalTime)
        if stage == EQUIPMENT_STAGES.COOLDOWN:
            self._totalTime = self._descriptor.cooldownSeconds
        else:
            self._totalTime = 0

    def getEntitiesIterator(self, avatar=None):
        return []


class WTExplosiveDamageShield(_LockableItem):

    def getEntitiesIterator(self, avatar=None):
        return []

    def canActivate(self, entityName=None, avatar=None):
        return (False, InCooldownError(self._descriptor.userString)) if self._stage and self._stage == EQUIPMENT_STAGES.COOLDOWN else super(WTExplosiveDamageShield, self).canActivate(entityName, avatar)


class WTDome(_LockableItem):

    def getEntitiesIterator(self, avatar=None):
        return []
