# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/battle_control/controllers/equipment_items.py
import importlib
from collections import namedtuple
import BigWorld
from gui.shared.system_factory import registerEquipmentItem
from gui.battle_control import avatar_getter
from constants import EQUIPMENT_STAGES
from gui.Scaleform.genConsts.ANIMATION_TYPES import ANIMATION_TYPES
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control.controllers.consumables.equipment_ctrl import _RepairCrewAndModules, _EquipmentItem, _ArcadeMineFieldItem, _ArtilleryItem, _TriggerItem, _ArcadeSmokeItem, _ReplayItem, _ReplayOrderItem, _ReplayAfterburningItem, _ReplayBomberItem, _ReplaySmokeItem, _ArcadeBomberItem, _AfterburningItem, _ActivationError, InCooldownError, _ReplayArtilleryItem
from battle_royale.gui.constants import BattleRoyaleEquipments
MapCaseMode = importlib.import_module('AvatarInputHandler.MapCaseMode')

class _BuffItem(_TriggerItem):

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(_BuffItem, self).update(quantity, stage, timeRemaining, totalTime)
        if stage == EQUIPMENT_STAGES.ACTIVE and self._prevStage != EQUIPMENT_STAGES.ACTIVE:
            self._animationType = ANIMATION_TYPES.MOVE_GREEN_BAR_DOWN | ANIMATION_TYPES.CENTER_COUNTER | ANIMATION_TYPES.GREEN_GLOW_SHOW | ANIMATION_TYPES.DARK_COLOR_TRANSFORM
        elif stage == EQUIPMENT_STAGES.COOLDOWN:
            self._animationType = ANIMATION_TYPES.MOVE_ORANGE_BAR_UP | ANIMATION_TYPES.SHOW_COUNTER_ORANGE | ANIMATION_TYPES.FILL_PARTIALLY


class _BomberStrikeSelector(object):

    def getStrikeSelector(self):
        return MapCaseMode._ArcadeBomberStrikeSelector


class _RepairBattleRoyaleCrewAndModules(_RepairCrewAndModules):

    def _canActivate(self, entityName=None, avatar=None):
        vehicle = BigWorld.entities.get(avatar_getter.getPlayerVehicleID())
        isAlive = avatar_getter.isVehicleAlive()
        return (True, None) if vehicle and isAlive and self.__hasDebuffComponentsForStop(vehicle) else super(_RepairBattleRoyaleCrewAndModules, self)._canActivate(entityName, avatar)

    def __hasDebuffComponentsForStop(self, vehicle):
        return bool([ True for comp in vehicle.dynamicComponents.values() if hasattr(comp, 'canBeStoppedRepairKit') and comp.canBeStoppedRepairKit ])


class _RegenerationKitBattleRoyaleItem(_EquipmentItem):

    def canActivate(self, entityName=None, avatar=None):
        if self._timeRemaining <= 0 < self._quantity and self._stage in (EQUIPMENT_STAGES.READY, EQUIPMENT_STAGES.PREPARING):
            result = True
            error = None
        else:
            result = False
            error = None
            if self._stage == EQUIPMENT_STAGES.COOLDOWN and self._quantity:
                error = InCooldownError(self._descriptor.userString)
        if not result or not avatar:
            return (result, error)
        else:
            vehicle = BigWorld.entities.get(avatar.playerVehicleID)
            return (False, _ActivationError('vehicleIsNotDamaged', {'name': self._descriptor.userString})) if not vehicle or vehicle.health >= vehicle.maxHealth else (True, None)

    def getActivationCode(self, entityName=None, avatar=None):
        return 65536 + self._descriptor.id[1]

    def getAnimationType(self):
        return ANIMATION_TYPES.MOVE_GREEN_BAR_DOWN | ANIMATION_TYPES.SHOW_COUNTER_ORANGE | ANIMATION_TYPES.DARK_COLOR_TRANSFORM if self._stage == EQUIPMENT_STAGES.ACTIVE else super(_RegenerationKitBattleRoyaleItem, self).getAnimationType()


class _ArcadeMineFieldBattleRoyaleItem(_ArcadeMineFieldItem, _BomberStrikeSelector):

    def _getErrorMsg(self):
        return InCooldownError(self._descriptor.userString) if self._quantity else None


class _FireCircle(_TriggerItem):

    def getTags(self):
        pass

    def getEntitiesIterator(self, avatar=None):
        return []


CorrodingShotInfo = namedtuple('CorrodingShotInfo', ('stage', 'endTime'))

class _CorrodingShotIndicator(object):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    __EQUIPMENT_NAME = BattleRoyaleEquipments.CORRODING_SHOT

    @classmethod
    def updateIndicator(cls, stage, timeRemaining):
        info = CorrodingShotInfo(stage, BigWorld.serverTime() + timeRemaining)
        cls.guiSessionProvider.shared.vehicleState.onEquipmentComponentUpdated(cls.__EQUIPMENT_NAME, None, info)
        return


class _CorrodingShot(_TriggerItem):
    __slots__ = ('__crosshairIndicator',)

    def __init__(self, descriptor, quantity, stage, timeRemaining, totalTime, tags):
        self.__crosshairIndicator = _CorrodingShotIndicator()
        super(_CorrodingShot, self).__init__(descriptor, quantity, stage, timeRemaining, totalTime, tags)

    def getTags(self):
        pass

    def getEntitiesIterator(self, avatar=None):
        return []

    def canActivate(self, entityName=None, avatar=None):
        return (False, None) if self._stage == EQUIPMENT_STAGES.PREPARING else super(_CorrodingShot, self).canActivate(entityName, avatar)

    def canDeactivate(self):
        return False

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(_CorrodingShot, self).update(quantity, stage, timeRemaining, totalTime)
        self.__crosshairIndicator.updateIndicator(stage, timeRemaining)


class _BotSpawner(_ArtilleryItem, _BomberStrikeSelector):
    MAX_SHIFT = 5
    MIN_SHIFT = 0

    def getAimingControlMode(self):
        return MapCaseMode.ArcadeMapCaseControlMode

    def _getErrorMsg(self):
        return InCooldownError(self._descriptor.userString) if self._quantity else None

    def getStrikeSelector(self):

        def selectorFunc(*args, **kwargs):
            selector = MapCaseMode._ArcadeBomberStrikeSelector(*args, **kwargs)
            selector.maxHeightShift = _BotSpawner.MAX_SHIFT
            selector.minHeightShift = _BotSpawner.MIN_SHIFT
            return selector

        return selectorFunc


class _ThunderStrike(_ArtilleryItem, _BomberStrikeSelector):
    MAX_SHIFT = 5
    MIN_SHIFT = -5

    def getAimingControlMode(self):
        return MapCaseMode.ArcadeMapCaseControlMode

    def _getErrorMsg(self):
        return InCooldownError(self._descriptor.userString) if self._quantity else None

    def getStrikeSelector(self):

        def selectorFunc(*args, **kwargs):
            selector = MapCaseMode._ArcadeBomberStrikeSelector(*args, **kwargs)
            selector.maxHeightShift = _ThunderStrike.MAX_SHIFT
            selector.minHeightShift = _ThunderStrike.MIN_SHIFT
            return selector

        return selectorFunc


class _AdaptationHealthRestore(_TriggerItem):

    def __init__(self, descriptor, quantity, stage, timeRemaining, totalTime, tags=None):
        self.__duration = descriptor.duration
        self.__cooldownSeconds = descriptor.cooldownSeconds
        super(_AdaptationHealthRestore, self).__init__(descriptor, quantity, stage, timeRemaining, totalTime, tags)

    def getTags(self):
        pass

    def getEntitiesIterator(self, avatar=None):
        return []

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(_AdaptationHealthRestore, self).update(quantity, stage, timeRemaining, totalTime)
        if stage == EQUIPMENT_STAGES.ACTIVE and self._prevStage != EQUIPMENT_STAGES.ACTIVE:
            self._animationType = ANIMATION_TYPES.MOVE_GREEN_BAR_DOWN | ANIMATION_TYPES.CENTER_COUNTER | ANIMATION_TYPES.GREEN_GLOW_SHOW | ANIMATION_TYPES.DARK_COLOR_TRANSFORM
            totalTime = self.__duration
        elif stage == EQUIPMENT_STAGES.COOLDOWN:
            self._animationType = ANIMATION_TYPES.MOVE_ORANGE_BAR_UP | ANIMATION_TYPES.SHOW_COUNTER_ORANGE | ANIMATION_TYPES.FILL_PARTIALLY
            totalTime = self.__cooldownSeconds
        self._totalTime = totalTime


class _ShotPassion(_BuffItem):

    def getTags(self):
        pass

    def getEntitiesIterator(self, avatar=None):
        return []


class _ArcadeBomber(_ArcadeBomberItem, _BomberStrikeSelector):
    pass


class _ArcadeSmoke(_ArcadeSmokeItem, _BomberStrikeSelector):
    pass


class _BRReplayMinefield(_ReplayOrderItem, _BomberStrikeSelector):
    pass


class _BRReplayBomber(_ReplayBomberItem, _BomberStrikeSelector):
    pass


class _BRReplaySpawnBot(_ReplayOrderItem, _BomberStrikeSelector):
    pass


class _BRReplaySmoke(_ReplaySmokeItem, _BomberStrikeSelector):
    pass


class _BRReplayThunderStrike(_ReplayArtilleryItem, _BomberStrikeSelector):
    pass


class _GameplayConsumableItem(_TriggerItem):

    def getTags(self):
        pass

    def getEntitiesIterator(self, avatar=None):
        return []


class _RepairPointItem(_TriggerItem):

    def getTags(self):
        pass

    def getEntitiesIterator(self, avatar=None):
        return []


class _BRReplayCorrodingShot(_ReplayItem):
    __slots__ = ('__crosshairIndicator',)

    def __init__(self, descriptor, quantity, stage, timeRemaining, totalTime, tags=None):
        self.__crosshairIndicator = _CorrodingShotIndicator()
        super(_BRReplayCorrodingShot, self).__init__(descriptor, quantity, stage, timeRemaining, totalTime, tags)

    def update(self, quantity, stage, timeRemaining, totalTime):
        super(_BRReplayCorrodingShot, self).update(quantity, stage, timeRemaining, totalTime)
        self.__crosshairIndicator.updateIndicator(stage, timeRemaining)


def registerBREquipmentsItems():
    registerEquipmentItem('large_repairkit_battle_royale', _RepairBattleRoyaleCrewAndModules, _ReplayItem)
    registerEquipmentItem('regenerationKit', _RegenerationKitBattleRoyaleItem, _ReplayItem)
    registerEquipmentItem('arcade_minefield_battle_royale', _ArcadeMineFieldBattleRoyaleItem, _BRReplayMinefield)
    registerEquipmentItem('healPoint', _BuffItem, _ReplayItem)
    registerEquipmentItem('afterburning_battle_royale', _AfterburningItem, _ReplayAfterburningItem)
    registerEquipmentItem('repairpoint', _RepairPointItem, _ReplayItem)
    registerEquipmentItem('selfBuff', _BuffItem, _ReplayItem)
    registerEquipmentItem('trappoint', _GameplayConsumableItem, _ReplayItem)
    registerEquipmentItem('arcade_bomber_battle_royale', _ArcadeBomber, _BRReplayBomber)
    registerEquipmentItem('spawn_kamikaze', _BotSpawner, _BRReplaySpawnBot)
    registerEquipmentItem('arcade_smoke_battle_royale_with_damage', _ArcadeSmoke, _BRReplaySmoke)
    registerEquipmentItem('berserker', _BuffItem, _ReplayItem)
    registerEquipmentItem('fireCircle', _FireCircle, _ReplayItem)
    registerEquipmentItem('adaptationHealthRestore', _AdaptationHealthRestore, _ReplayItem)
    registerEquipmentItem('corrodingShot', _CorrodingShot, _BRReplayCorrodingShot)
    registerEquipmentItem('clingBrander', _BotSpawner, _BRReplaySpawnBot)
    registerEquipmentItem('thunderStrike', _ThunderStrike, _BRReplayThunderStrike)
    registerEquipmentItem('shotPassion', _ShotPassion, _ReplayItem)
