# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/battle/ribbons_aggregator.py
import BigWorld
import BattleReplay
from last_stand_common.ls_battle_feedback import LSGameplayActionID
from last_stand_common.ls_battle_feedback import unpackGameplayActionFeedback
from gui.Scaleform.daapi.view.battle.shared.ribbons_aggregator import RibbonsAggregator, _RibbonClassFactory, _ACCUMULATED_RIBBON_TYPES, _FEEDBACK_EVENTS_TO_IGNORE as _DEFAULT_EVENTS_TO_IGNORE, _FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY as _DEFAULT_RIBBON_FACTORIES, _CausedDamageRibbon, _RIBBON_TYPES_AGGREGATED_WITH_KILL_RIBBON as _DEFAULT_RIBBONS_AGGREGATED_WITH_KILL, DAMAGE_SOURCE, _Ribbon, _SingleVehicleReceivedHitRibbon, _AssistRibbonClassFactory, _RadioAssistRibbon, _TrackAssistRibbon, _StunAssistRibbon
from gui.Scaleform.daapi.view.battle.shared.ribbons_panel import _singleVehRibbonFormatter, _getVehicleData, _formatCounter
from last_stand.gui.ls_gui_constants import FEEDBACK_EVENT_ID
from last_stand_common.last_stand_constants import ATTACK_REASON, BATTLE_EVENT_TYPE
from last_stand.gui.scaleform.genConsts.LS_BATTLE_EFFICIENCY_TYPES import LS_BATTLE_EFFICIENCY_TYPES
from gui.Scaleform.genConsts.BATTLE_EFFICIENCY_TYPES import BATTLE_EFFICIENCY_TYPES
from gui.battle_control.controllers.feedback_events import _BATTLE_EVENT_TO_PLAYER_FEEDBACK_EVENT, _PLAYER_FEEDBACK_EXTRA_DATA_CONVERTERS
from items import vehicles
_BATTLE_EVENT_TO_PLAYER_FEEDBACK_EVENT.update({BATTLE_EVENT_TYPE.LS_GAMEPLAY_ACTION: FEEDBACK_EVENT_ID.LS_GAMEPLAY_ACTION})
_PLAYER_FEEDBACK_EXTRA_DATA_CONVERTERS.update({FEEDBACK_EVENT_ID.LS_GAMEPLAY_ACTION: unpackGameplayActionFeedback})
_LS_FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY = {}
_LS_FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY.update(_DEFAULT_RIBBON_FACTORIES)
_LS_FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY.pop(FEEDBACK_EVENT_ID.VEHICLE_HEALTH_ADDED, None)
_LS_FEEDBACK_EVENTS_TO_IGNORE = _DEFAULT_EVENTS_TO_IGNORE + (FEEDBACK_EVENT_ID.VEHICLE_HEALTH_ADDED,)
_LS_RIBBON_TYPES_AGGREGATED_WITH_KILL_RIBBON = []
_LS_RIBBON_TYPES_AGGREGATED_WITH_KILL_RIBBON.extend(_DEFAULT_RIBBONS_AGGREGATED_WITH_KILL)
_LS_RIBBON_TYPES_COPY_TO = {}

def _lsActionRibbonFormatter(ribbon, arenaDP, updater):
    if ribbon.isShowActionSource:
        vehicleName, vehicleClassTag = _getVehicleData(arenaDP, ribbon.vehicleID)
    else:
        vehicleName, vehicleClassTag = ('', '')
    updater(ribbonID=ribbon.getID(), ribbonType=ribbon.getType(), leftFieldStr=ribbon.actionValue, vehName=vehicleName, vehType=vehicleClassTag)


def _lsModulesInvulnerabilityRibbonFormatter(ribbon, arenaDP, updater):
    if ribbon.isShowActionSource:
        vehicleName, vehicleClassTag = _getVehicleData(arenaDP, ribbon.vehicleID)
    else:
        vehicleName, vehicleClassTag = ('', '')
    updater(ribbonID=ribbon.getID(), ribbonType=ribbon.getType(), leftFieldStr=_formatCounter(ribbon.actionValue), vehName=vehicleName, vehType=vehicleClassTag)


class _LSGameplayActionRibbon(_Ribbon):
    __slots__ = ('_actionValue', '_actionID', '_vehicleID', '_effType', '_isPlayerVehicle')
    BATTLE_EFFICIENCY_TYPE = None

    def __init__(self, ribbonID, actionCtx):
        super(_LSGameplayActionRibbon, self).__init__(ribbonID)
        self._vehicleID = actionCtx.targetID
        self._actionValue = actionCtx.value
        self._actionID = actionCtx.id
        self._effType = self.BATTLE_EFFICIENCY_TYPE
        self._isPlayerVehicle = self._vehicleID == BigWorld.player().playerVehicleID

    @classmethod
    def createFromFeedbackEvent(cls, ribbonID, event):
        return cls(ribbonID, event.getExtra())

    @property
    def actionValue(self):
        return self._actionValue

    @property
    def actionID(self):
        return self._actionID

    @property
    def vehicleID(self):
        return self._vehicleID

    @property
    def isShowActionSource(self):
        return not self._isPlayerVehicle

    def getFormatter(self):
        return _lsActionRibbonFormatter

    def getType(self):
        return self._effType

    def _canAggregate(self, ribbon):
        return isinstance(ribbon, self.__class__) and ribbon.actionID == self.actionID and self._vehicleID == ribbon._vehicleID

    def _aggregate(self, ribbon):
        self._actionValue += ribbon.actionValue


def registerRibbonsFactory(eventID):

    def decorator(cls):
        _LS_FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY[eventID] = cls()
        return cls

    return decorator


def aggregateWithKillRibbon(cls):
    effType = cls.BATTLE_EFFICIENCY_TYPE
    if effType not in _LS_RIBBON_TYPES_AGGREGATED_WITH_KILL_RIBBON:
        _LS_RIBBON_TYPES_AGGREGATED_WITH_KILL_RIBBON.append(effType)
    return cls


def lsCopyTo(ribbonType, isMergeCopy=False):

    def decorator(cls):
        setattr(cls, 'LSIsMergeCopy', isMergeCopy)
        _LS_RIBBON_TYPES_COPY_TO.setdefault(ribbonType, set()).add(cls)

    return decorator


class _LSDelayedRibbonMixin(object):
    DELAY = 0.1

    def __init__(self):
        self._delayedTill = BigWorld.time() + self.DELAY

    @property
    def delayedTill(self):
        return self._delayedTill


class _LSCausedDamageRibbon(_CausedDamageRibbon):
    __slots__ = ()
    BATTLE_EFFICIENCY_TYPE = None

    def getType(self):
        return self.BATTLE_EFFICIENCY_TYPE

    def getFormatter(self):
        return _singleVehRibbonFormatter


class _LSCausedAoeAbilityDamage(_LSCausedDamageRibbon):
    __slots__ = ()
    BATTLE_EFFICIENCY_TYPE = None

    def getDamageSource(self):
        return DAMAGE_SOURCE.HIDE

    def _canAggregate(self, ribbon):
        return isinstance(ribbon, self.__class__)


class _LSAbstractDamageRibbonsFactory(_RibbonClassFactory):
    ATTACK_REASONS = None

    def getRibbonClass(self, event):
        result = self._getLSRibbonClass(event.getExtra().getAttackReasonID(), event.getExtra().getSecondaryAttackReasonID())
        return result or self._DEFAULT_FACTORY.getRibbonClass(event)

    @classmethod
    def registerAttackReasonRibbon(cls, reason, secondaryReason=None):

        def decorator(ribbonCls):
            key = (ATTACK_REASON.getIndex(reason), ATTACK_REASON.getIndex(secondaryReason)) if secondaryReason else ATTACK_REASON.getIndex(reason)
            cls.ATTACK_REASONS[key] = ribbonCls
            return ribbonCls

        return decorator

    @classmethod
    def _getLSRibbonClass(cls, reasonID, secondaryReasonID):
        registry = cls.ATTACK_REASONS
        return registry.get((reasonID, secondaryReasonID), None) or registry.get(reasonID, None)


@registerRibbonsFactory(FEEDBACK_EVENT_ID.PLAYER_DAMAGED_HP_ENEMY)
class LSDamageRibbonsFactory(_LSAbstractDamageRibbonsFactory):
    ATTACK_REASONS = {}
    _DEFAULT_FACTORY = _DEFAULT_RIBBON_FACTORIES[FEEDBACK_EVENT_ID.PLAYER_DAMAGED_HP_ENEMY]


@registerRibbonsFactory(FEEDBACK_EVENT_ID.ENEMY_DAMAGED_HP_PLAYER)
class LSReceiveDamageRibbonsFactory(_LSAbstractDamageRibbonsFactory):
    ATTACK_REASONS = {}
    _DEFAULT_FACTORY = _DEFAULT_RIBBON_FACTORIES[FEEDBACK_EVENT_ID.ENEMY_DAMAGED_HP_PLAYER]


@registerRibbonsFactory(FEEDBACK_EVENT_ID.LS_GAMEPLAY_ACTION)
class LSGameplayActionRibbonsFactory(_RibbonClassFactory):
    GAMEPLAY_ACTIONS = {}

    def getRibbonClass(self, event):
        actionID = event.getExtra().id
        return self._getLSRibbonClass(actionID)

    @classmethod
    def registerActionRibbon(cls, reason):

        def decorator(ribbonCls):
            cls.GAMEPLAY_ACTIONS[reason] = ribbonCls
            return ribbonCls

        return decorator

    @classmethod
    def _getLSRibbonClass(cls, key):
        return cls.GAMEPLAY_ACTIONS.get(key, None)


@lsCopyTo(BATTLE_EFFICIENCY_TYPES.DESTRUCTION, isMergeCopy=True)
@LSDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.LS_ABILITY_VAMPIRE)
class _LSCausedVampiricDamageRibbon(_LSCausedAoeAbilityDamage):
    __slots__ = ()
    BATTLE_EFFICIENCY_TYPE = LS_BATTLE_EFFICIENCY_TYPES.LS_DMG_VAMPIRE


@lsCopyTo(BATTLE_EFFICIENCY_TYPES.DESTRUCTION, isMergeCopy=True)
@LSDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.LS_ABILITY_AOE_DAMAGE)
class _LSCausedAoeDamageRibbon(_LSCausedAoeAbilityDamage):
    __slots__ = ()
    BATTLE_EFFICIENCY_TYPE = LS_BATTLE_EFFICIENCY_TYPES.LS_AOE_DAMAGE


@lsCopyTo(BATTLE_EFFICIENCY_TYPES.DESTRUCTION, isMergeCopy=True)
@LSDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.LS_SHOT_AOE_DAMAGE)
class _LSCausedAoeDamageInstantShotRibbon(_LSCausedAoeAbilityDamage):
    __slots__ = ()
    BATTLE_EFFICIENCY_TYPE = LS_BATTLE_EFFICIENCY_TYPES.LS_SHOT_AOE_DAMAGE


@lsCopyTo(BATTLE_EFFICIENCY_TYPES.DESTRUCTION, isMergeCopy=True)
@LSDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.LS_SHOT_AOE_DRAIN_ENEMY_HP)
class _LSCausedAoeDrainEnemyHpInstantShotDamageRibbon(_LSCausedAoeAbilityDamage):
    __slots__ = ()
    BATTLE_EFFICIENCY_TYPE = LS_BATTLE_EFFICIENCY_TYPES.LS_SHOT_AOE_DRAIN_ENEMY_HP


@lsCopyTo(BATTLE_EFFICIENCY_TYPES.DESTRUCTION, isMergeCopy=True)
@LSDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.LS_SHOT_AOE_STUN)
class _LSCausedAoeStunInstantShotRibbon(_LSCausedAoeAbilityDamage):
    __slots__ = ()
    BATTLE_EFFICIENCY_TYPE = LS_BATTLE_EFFICIENCY_TYPES.LS_SHOT_AOE_STUN


@lsCopyTo(BATTLE_EFFICIENCY_TYPES.DESTRUCTION, isMergeCopy=True)
@LSDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.FIRE, ATTACK_REASON.LS_ABILITY_IGNITE)
class _LSAoeFireDamageRibbon(_LSCausedAoeAbilityDamage):
    __slots__ = ()
    BATTLE_EFFICIENCY_TYPE = LS_BATTLE_EFFICIENCY_TYPES.LS_AOE_BURN


@LSDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.LS_EXTRA_DAMAGE_SITUATIONAL)
class _LSCausedExtraDamageRibbon(_LSCausedDamageRibbon, _LSDelayedRibbonMixin):
    __slots__ = ()
    BATTLE_EFFICIENCY_TYPE = LS_BATTLE_EFFICIENCY_TYPES.LS_EXTRA_DAMAGE_SITUATIONAL
    DELAY = 0.8

    def getDamageSource(self):
        return DAMAGE_SOURCE.HIDE


@aggregateWithKillRibbon
@LSDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.FIRE, ATTACK_REASON.LS_PASSIVE_IGNITE)
class _LSPassiveFireDamageRibbon(_LSCausedDamageRibbon):
    __slots__ = ()
    BATTLE_EFFICIENCY_TYPE = LS_BATTLE_EFFICIENCY_TYPES.LS_PASSIVE_IGNITE


@LSReceiveDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.LS_BOMBER_EXPLOSION)
class _LSReceivedBomberExplosionHitRibbon(_SingleVehicleReceivedHitRibbon):
    __slots__ = ()
    TYPE = LS_BATTLE_EFFICIENCY_TYPES.LS_BOMBER_EXPLOSION

    def getType(self):
        return self.TYPE

    def getFormatter(self):
        return _singleVehRibbonFormatter


@LSReceiveDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.LS_ABILITY_VAMPIRE)
class _ReceivedVampireAbilityRibbon(_SingleVehicleReceivedHitRibbon):
    __slots__ = ()
    TYPE = LS_BATTLE_EFFICIENCY_TYPES.LS_DMG_VAMPIRE_RECEIVED

    def getType(self):
        return self.TYPE

    def getFormatter(self):
        return _singleVehRibbonFormatter


@LSReceiveDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.LS_ABILITY_AOE_DAMAGE)
class _ReceivedAOEDamageAbilityHitRibbon(_SingleVehicleReceivedHitRibbon):
    __slots__ = ()
    TYPE = LS_BATTLE_EFFICIENCY_TYPES.LS_AOE_DAMAGE_RECEIVED

    def getType(self):
        return self.TYPE

    def getFormatter(self):
        return _singleVehRibbonFormatter


@LSGameplayActionRibbonsFactory.registerActionRibbon(LSGameplayActionID.VEHICLE_REPAIR_INCOMING)
class _LSIncomingRepairRibbon(_LSGameplayActionRibbon):
    BATTLE_EFFICIENCY_TYPE = LS_BATTLE_EFFICIENCY_TYPES.LS_REPAIR

    @property
    def healerID(self):
        return self.vehicleID

    @property
    def isSelfHeal(self):
        return self._isPlayerVehicle

    def getType(self):
        return LS_BATTLE_EFFICIENCY_TYPES.LS_REPAIR if self.isSelfHeal else LS_BATTLE_EFFICIENCY_TYPES.LS_REPAIR_BY_OTHER

    def _canAggregate(self, ribbon):
        return super(_LSIncomingRepairRibbon, self)._canAggregate(ribbon) and self.healerID == ribbon.healerID


@LSGameplayActionRibbonsFactory.registerActionRibbon(LSGameplayActionID.VEHICLE_REPAIR_OUTCOMING)
class _LSOutcomingRepairRibbon(_LSGameplayActionRibbon):
    BATTLE_EFFICIENCY_TYPE = LS_BATTLE_EFFICIENCY_TYPES.LS_REPAIR_OTHER

    @property
    def isShowActionSource(self):
        return False

    def _canAggregate(self, ribbon):
        return isinstance(ribbon, self.__class__) and ribbon.actionID == self.actionID


@LSGameplayActionRibbonsFactory.registerActionRibbon(LSGameplayActionID.MODULES_DAMAGE_BLOCKED)
class _LSModulesDamageBlockedRibbon(_LSGameplayActionRibbon):
    BATTLE_EFFICIENCY_TYPE = LS_BATTLE_EFFICIENCY_TYPES.LS_MODULES_DAMAGE_BLOCKED

    @property
    def isShowActionSource(self):
        return False

    def getFormatter(self):
        return _lsModulesInvulnerabilityRibbonFormatter

    def _canAggregate(self, ribbon):
        return isinstance(ribbon, self.__class__) and ribbon.actionID == self.actionID

    def _aggregate(self, ribbon):
        self._actionValue += ribbon.actionValue


@LSGameplayActionRibbonsFactory.registerActionRibbon(LSGameplayActionID.HEALTH_DRAINED_BY_PASSIVE_VAMPIRE)
class _LSHealthDrainedByPassiveVampireRibbon(_LSGameplayActionRibbon):
    BATTLE_EFFICIENCY_TYPE = LS_BATTLE_EFFICIENCY_TYPES.LS_PASSIVE_VAMPIRE

    @property
    def isShowActionSource(self):
        return False

    def _canAggregate(self, ribbon):
        return isinstance(ribbon, self.__class__) and ribbon.actionID == self.actionID


@LSGameplayActionRibbonsFactory.registerActionRibbon(LSGameplayActionID.HEAL_BY_SELF_SITUATIONAL)
class _LSSituationalHealRibbon(_LSGameplayActionRibbon):
    BATTLE_EFFICIENCY_TYPE = LS_BATTLE_EFFICIENCY_TYPES.LS_HEAL_SITUATIONAL

    @property
    def isShowActionSource(self):
        return False

    def _canAggregate(self, ribbon):
        return isinstance(ribbon, self.__class__) and ribbon.actionID == self.actionID


@LSGameplayActionRibbonsFactory.registerActionRibbon(LSGameplayActionID.EQUIPMENT_ACTIVATED)
class _LSEquipmentActivatedRibbon(_LSGameplayActionRibbon):
    EQUIPMENT_TO_RIBBON = {'LS_nitroSituational': LS_BATTLE_EFFICIENCY_TYPES.LS_NITRO_ACTIVATED}

    def __init__(self, ribbonID, actionCtx):
        super(_LSEquipmentActivatedRibbon, self).__init__(ribbonID, actionCtx)
        equipment = vehicles.g_cache.equipments().get(self._actionValue)
        self._effType = self.EQUIPMENT_TO_RIBBON.get(equipment.name) if equipment is not None else None
        return

    @property
    def isShowActionSource(self):
        return False

    @property
    def actionValue(self):
        pass

    @property
    def shouldShow(self):
        return self._effType is not None

    def getFormatter(self):
        return _lsActionRibbonFormatter

    def getType(self):
        return self._effType

    def _canAggregate(self, ribbon):
        return False


class LSRibbonsAggregator(RibbonsAggregator):
    FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY = _LS_FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY
    FEEDBACK_EVENTS_TO_IGNORE = _LS_FEEDBACK_EVENTS_TO_IGNORE
    RIBBON_TYPES_AGGREGATED_WITH_KILL_RIBBON = _LS_RIBBON_TYPES_AGGREGATED_WITH_KILL_RIBBON
    RIBBON_TYPES_COPY_TO = _LS_RIBBON_TYPES_COPY_TO

    def _aggregateRibbons(self, ribbons):
        copyMergedRibbons = []
        for destEffType, sourceClasses in self.RIBBON_TYPES_COPY_TO.iteritems():
            sourceRibbons = [ r for r in ribbons if r is not None and r.__class__ in sourceClasses ]
            destRibbons = [ r for r in ribbons if r is not None and r.getType() == destEffType ]
            for r in destRibbons:
                for other in sourceRibbons:
                    if r.aggregate(other) and getattr(other, 'LSIsMergeCopy', False):
                        copyMergedRibbons.append(other)

        return super(LSRibbonsAggregator, self)._aggregateRibbons([ r for r in ribbons if r not in copyMergedRibbons ])


class _LSStunAssistRibbon(_StunAssistRibbon):

    def getDamageSource(self):
        return DAMAGE_SOURCE.HIDE

    def _canAggregate(self, ribbon):
        return isinstance(ribbon, self.__class__)


@registerRibbonsFactory(FEEDBACK_EVENT_ID.PLAYER_ASSIST_TO_KILL_ENEMY)
class LSAssistToKillEnemyRibbonsFactory(_AssistRibbonClassFactory):

    def __init__(self):
        _AssistRibbonClassFactory.__init__(self, trackAssistCls=_TrackAssistRibbon, radioAssistCls=_RadioAssistRibbon, stunAssistCls=_LSStunAssistRibbon)


@registerRibbonsFactory(FEEDBACK_EVENT_ID.PLAYER_ASSIST_TO_STUN_ENEMY)
class LSAssistToStunEnemyRibbonsFactory(_AssistRibbonClassFactory):

    def __init__(self):
        _AssistRibbonClassFactory.__init__(self, trackAssistCls=_TrackAssistRibbon, radioAssistCls=_RadioAssistRibbon, stunAssistCls=_LSStunAssistRibbon)


class LSRibbonsAggregatorPlayer(LSRibbonsAggregator):

    def _onPlayerFeedbackReceived(self, events):
        if BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            self.suspend()
        super(LSRibbonsAggregatorPlayer, self)._onPlayerFeedbackReceived(events)

    def _aggregateRibbons(self, ribbons):
        replayRibbons = []
        for ribbon in ribbons:
            if ribbon is None:
                continue
            if BattleReplay.g_replayCtrl.isTimeWarpInProgress and ribbon.getType() not in _ACCUMULATED_RIBBON_TYPES:
                continue
            replayRibbons.append(ribbon)

        super(LSRibbonsAggregatorPlayer, self)._aggregateRibbons(replayRibbons)
        return


def createRibbonsAggregator():
    return LSRibbonsAggregatorPlayer() if BattleReplay.g_replayCtrl.isPlaying else LSRibbonsAggregator()
