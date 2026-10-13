# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/battle/ribbons_aggregator.py
from __future__ import absolute_import
import BigWorld
import BattleReplay
from halloween_common.hw_battle_feedback import HWGameplayActionID
from halloween_common.hw_battle_feedback import unpackGameplayActionFeedback
from gui.Scaleform.daapi.view.battle.shared.ribbons_aggregator import RibbonsAggregator, _RibbonClassFactory, _ACCUMULATED_RIBBON_TYPES, _FEEDBACK_EVENTS_TO_IGNORE as _DEFAULT_EVENTS_TO_IGNORE, _FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY as _DEFAULT_RIBBON_FACTORIES, _CausedDamageRibbon, _RIBBON_TYPES_AGGREGATED_WITH_KILL_RIBBON as _DEFAULT_RIBBONS_AGGREGATED_WITH_KILL, DAMAGE_SOURCE, _Ribbon, _SingleVehicleReceivedHitRibbon, _AssistRibbonClassFactory, _RadioAssistRibbon, _TrackAssistRibbon, _StunAssistRibbon, _EnemyKillRibbon, _RIBBON_TYPES_EXCLUDED_IF_KILL_RIBBON
from gui.Scaleform.daapi.view.battle.shared.ribbons_panel import _singleVehRibbonFormatter, _getVehicleData
from halloween.gui.halloween_gui_constants import FEEDBACK_EVENT_ID
from halloween_common.halloween_constants import ATTACK_REASON, BATTLE_EVENT_TYPE
from halloween.gui.scaleform.genConsts.HW_BATTLE_EFFICIENCY_TYPES import HW_BATTLE_EFFICIENCY_TYPES
from gui.Scaleform.genConsts.BATTLE_EFFICIENCY_TYPES import BATTLE_EFFICIENCY_TYPES
from gui.battle_control.controllers.feedback_events import _BATTLE_EVENT_TO_PLAYER_FEEDBACK_EVENT, _PLAYER_FEEDBACK_EXTRA_DATA_CONVERTERS
from gui.impl import backport
from gui.impl.gen import R
_BATTLE_EVENT_TO_PLAYER_FEEDBACK_EVENT.update({BATTLE_EVENT_TYPE.HW_GAMEPLAY_ACTION: FEEDBACK_EVENT_ID.HW_GAMEPLAY_ACTION})
_PLAYER_FEEDBACK_EXTRA_DATA_CONVERTERS.update({FEEDBACK_EVENT_ID.HW_GAMEPLAY_ACTION: unpackGameplayActionFeedback})
_HW_FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY = {}
_HW_FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY.update(_DEFAULT_RIBBON_FACTORIES)
_HW_FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY.pop(FEEDBACK_EVENT_ID.VEHICLE_HEALTH_ADDED, None)
_HW_FEEDBACK_EVENTS_TO_IGNORE = _DEFAULT_EVENTS_TO_IGNORE + (FEEDBACK_EVENT_ID.VEHICLE_HEALTH_ADDED,)
_HW_RIBBON_TYPES_AGGREGATED_WITH_KILL_RIBBON = []
_HW_RIBBON_TYPES_AGGREGATED_WITH_KILL_RIBBON.extend(_DEFAULT_RIBBONS_AGGREGATED_WITH_KILL)
_HW_RIBBON_TYPES_COPY_TO = {}
_HW_EXCLUDED_RIBBONS = {}

def _formatAddition(value):
    return backport.text(R.strings.halloween_battle.efficiencyRibbons.additionFormat(), value=value)


def _formatSubtraction(value):
    return backport.text(R.strings.halloween_battle.efficiencyRibbons.subtractionFormat(), value=value)


def _formatCounter(value):
    return backport.text(R.strings.halloween_battle.efficiencyRibbons.counterFormat(), value=value)


def _hwWithoutLeftFieldRibbonFormatter(ribbon, arenaDP, updater):
    if ribbon.isShowActionSource:
        vehicleName, vehicleClassTag = _getVehicleData(arenaDP, ribbon.vehicleID)
    else:
        vehicleName, vehicleClassTag = ('', '')
    updater(ribbonID=ribbon.getID(), ribbonType=ribbon.getType(), vehName=vehicleName, vehType=vehicleClassTag)


def _hwActionRibbonFormatter(ribbon, arenaDP, updater):
    if ribbon.isShowActionSource:
        vehicleName, vehicleClassTag = _getVehicleData(arenaDP, ribbon.vehicleID)
    else:
        vehicleName, vehicleClassTag = ('', '')
    updater(ribbonID=ribbon.getID(), ribbonType=ribbon.getType(), leftFieldStr=ribbon.actionValue, vehName=vehicleName, vehType=vehicleClassTag)


def _hwCounterRibbonFormatter(ribbon, arenaDP, updater):
    if ribbon.isShowActionSource:
        vehicleName, vehicleClassTag = _getVehicleData(arenaDP, ribbon.vehicleID)
    else:
        vehicleName, vehicleClassTag = ('', '')
    updater(ribbonID=ribbon.getID(), ribbonType=ribbon.getType(), leftFieldStr=_formatCounter(ribbon.actionValue), vehName=vehicleName, vehType=vehicleClassTag)


def _hwShellsPickupRibbonFormatter(ribbon, arenaDP, updater, format_=_formatAddition):
    if ribbon.isShowActionSource:
        vehicleName, vehicleClassTag = _getVehicleData(arenaDP, ribbon.vehicleID)
    else:
        vehicleName, vehicleClassTag = ('', '')
    updater(ribbonID=ribbon.getID(), ribbonType=ribbon.getType(), leftFieldStr=format_(ribbon.actionValue), vehName=vehicleName, vehType=vehicleClassTag)


def _hwSoulsMiriumizationDecreaseRibbonFormatter(ribbon, arenaDP, updater):
    _hwShellsPickupRibbonFormatter(ribbon, arenaDP, updater, _formatSubtraction)


def _hwSoulsRefundRibbonFormatter(ribbon, _, updater):
    updater(ribbonID=ribbon.getID(), ribbonType=ribbon.getType(), leftFieldStr=_formatAddition(ribbon.actionValue))


class _HWGameplayActionRibbon(_Ribbon):
    __slots__ = ('_actionValue', '_actionID', '_vehicleID', '_effType', '_isPlayerVehicle')
    BATTLE_EFFICIENCY_TYPE = None

    def __init__(self, ribbonID, actionCtx):
        super(_HWGameplayActionRibbon, self).__init__(ribbonID)
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
        return _hwActionRibbonFormatter

    def getType(self):
        return self._effType

    def _canAggregate(self, ribbon):
        return isinstance(ribbon, self.__class__) and ribbon.actionID == self.actionID and self._vehicleID == ribbon._vehicleID

    def _aggregate(self, ribbon):
        self._actionValue += ribbon.actionValue


def registerRibbonsFactory(eventID):

    def decorator(cls):
        _HW_FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY[eventID] = cls()
        return cls

    return decorator


def aggregateWithKillRibbon(cls):
    effType = cls.BATTLE_EFFICIENCY_TYPE
    if effType not in _HW_RIBBON_TYPES_AGGREGATED_WITH_KILL_RIBBON:
        _HW_RIBBON_TYPES_AGGREGATED_WITH_KILL_RIBBON.append(effType)
    return cls


def hwCopyTo(ribbonType, isMergeCopy=False):

    def decorator(cls):
        setattr(cls, 'hwIsMergeCopy', isMergeCopy)
        _HW_RIBBON_TYPES_COPY_TO.setdefault(cls, set()).add(ribbonType)

    return decorator


def hwExcludeRibbons(ribbonTypes):

    def decorator(cls):
        _HW_EXCLUDED_RIBBONS.setdefault(cls, set()).update(ribbonTypes)

    return decorator


class _HWCausedDamageRibbon(_CausedDamageRibbon):
    __slots__ = ()
    BATTLE_EFFICIENCY_TYPE = None

    def getType(self):
        return self.BATTLE_EFFICIENCY_TYPE

    def getFormatter(self):
        return _singleVehRibbonFormatter


class _HWCausedAoeAbilityDamage(_HWCausedDamageRibbon):
    __slots__ = ()
    BATTLE_EFFICIENCY_TYPE = None

    def getDamageSource(self):
        return DAMAGE_SOURCE.HIDE

    def _canAggregate(self, ribbon):
        return isinstance(ribbon, self.__class__)


class _HWEnemyKillRibbon(_EnemyKillRibbon):
    __slots__ = ()
    BATTLE_EFFICIENCY_TYPE = None

    def getType(self):
        return self.BATTLE_EFFICIENCY_TYPE

    @property
    def isShowActionSource(self):
        return True

    @property
    def vehicleID(self):
        return self.getVehicleID()


class _HWAbstractDamageRibbonsFactory(_RibbonClassFactory):
    ATTACK_REASONS = None

    def getRibbonClass(self, event):
        result = self._getHWRibbonClass(event.getExtra().getAttackReasonID(), event.getExtra().getSecondaryAttackReasonID())
        return result or self._DEFAULT_FACTORY.getRibbonClass(event)

    @classmethod
    def registerAttackReasonRibbon(cls, reason, secondaryReason=None):

        def decorator(ribbonCls):
            key = (ATTACK_REASON.getIndex(reason), ATTACK_REASON.getIndex(secondaryReason)) if secondaryReason else ATTACK_REASON.getIndex(reason)
            cls.ATTACK_REASONS[key] = ribbonCls
            return ribbonCls

        return decorator

    @classmethod
    def _getHWRibbonClass(cls, reasonID, secondaryReasonID):
        registry = cls.ATTACK_REASONS
        return registry.get((reasonID, secondaryReasonID), None) or registry.get(reasonID, None)


@registerRibbonsFactory(FEEDBACK_EVENT_ID.PLAYER_DAMAGED_HP_ENEMY)
class HWDamageRibbonsFactory(_HWAbstractDamageRibbonsFactory):
    ATTACK_REASONS = {}
    _DEFAULT_FACTORY = _DEFAULT_RIBBON_FACTORIES[FEEDBACK_EVENT_ID.PLAYER_DAMAGED_HP_ENEMY]


@registerRibbonsFactory(FEEDBACK_EVENT_ID.ENEMY_DAMAGED_HP_PLAYER)
class HWReceiveDamageRibbonsFactory(_HWAbstractDamageRibbonsFactory):
    ATTACK_REASONS = {}
    _DEFAULT_FACTORY = _DEFAULT_RIBBON_FACTORIES[FEEDBACK_EVENT_ID.ENEMY_DAMAGED_HP_PLAYER]


@registerRibbonsFactory(FEEDBACK_EVENT_ID.HW_GAMEPLAY_ACTION)
class HWGameplayActionRibbonsFactory(_RibbonClassFactory):
    GAMEPLAY_ACTIONS = {}

    def getRibbonClass(self, event):
        actionID = event.getExtra().id
        return self._getHWRibbonClass(actionID)

    @classmethod
    def registerActionRibbon(cls, reason):

        def decorator(ribbonCls):
            cls.GAMEPLAY_ACTIONS[reason] = ribbonCls
            return ribbonCls

        return decorator

    @classmethod
    def _getHWRibbonClass(cls, key):
        return cls.GAMEPLAY_ACTIONS.get(key, None)


@hwCopyTo(BATTLE_EFFICIENCY_TYPES.DESTRUCTION, isMergeCopy=True)
@HWDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.HALLOWEEN_ABILITY_VAMPIRE)
class _HWCausedVampiricDamageRibbon(_HWCausedAoeAbilityDamage):
    __slots__ = ()
    BATTLE_EFFICIENCY_TYPE = HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_DMG_VAMPIRE


@hwCopyTo(BATTLE_EFFICIENCY_TYPES.DESTRUCTION, isMergeCopy=True)
@HWDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.HALLOWEEN_ABILITY_AOE_DAMAGE)
class _HWCausedAoeDamageRibbon(_HWCausedAoeAbilityDamage):
    __slots__ = ()
    BATTLE_EFFICIENCY_TYPE = HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_AOE_DAMAGE


@hwCopyTo(BATTLE_EFFICIENCY_TYPES.DESTRUCTION, isMergeCopy=True)
@HWDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.HALLOWEEN_SHOT_AOE_DAMAGE)
class _HWCausedAoeDamageInstantShotRibbon(_HWCausedAoeAbilityDamage):
    __slots__ = ()
    BATTLE_EFFICIENCY_TYPE = HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_SHOT_AOE_DAMAGE


@hwCopyTo(BATTLE_EFFICIENCY_TYPES.DESTRUCTION, isMergeCopy=True)
@HWDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.HALLOWEEN_SHOT_AOE_DRAIN_ENEMY_HP)
class _HWCausedAoeDrainEnemyHpInstantShotDamageRibbon(_HWCausedAoeAbilityDamage):
    __slots__ = ()
    BATTLE_EFFICIENCY_TYPE = HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_SHOT_AOE_DRAIN_ENEMY_HP


@hwCopyTo(BATTLE_EFFICIENCY_TYPES.DESTRUCTION, isMergeCopy=True)
@HWDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.HALLOWEEN_SHOT_AOE_STUN)
class _HWCausedAoeStunInstantShotRibbon(_HWCausedAoeAbilityDamage):
    __slots__ = ()
    BATTLE_EFFICIENCY_TYPE = HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_SHOT_AOE_STUN


@hwCopyTo(BATTLE_EFFICIENCY_TYPES.DESTRUCTION, isMergeCopy=True)
@HWDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.FIRE, ATTACK_REASON.HALLOWEEN_ABILITY_IGNITE)
class _HWAoeFireDamageRibbon(_HWCausedAoeAbilityDamage):
    __slots__ = ()
    BATTLE_EFFICIENCY_TYPE = HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_AOE_BURN


@HWDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.FIRE, ATTACK_REASON.HALLOWEEN_PASSIVE_IGNITE)
class _HWPassiveFireDamageRibbon(_SingleVehicleReceivedHitRibbon):
    __slots__ = ()
    TYPE = HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_PASSIVE_IGNITE

    def getType(self):
        return self.TYPE

    def getFormatter(self):
        return _singleVehRibbonFormatter


@HWReceiveDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.HALLOWEEN_BOSS_AURA)
class _ReceivedBossAuraHitRibbon(_SingleVehicleReceivedHitRibbon):
    __slots__ = ()
    TYPE = HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_AOE_BOSS_BURN

    def getType(self):
        return self.TYPE

    def getFormatter(self):
        return _singleVehRibbonFormatter


@HWReceiveDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.HALLOWEEN_BOMBER_EXPLOSION)
class _HWReceivedBomberExplosionHitRibbon(_SingleVehicleReceivedHitRibbon):
    __slots__ = ()
    TYPE = HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_BOMBER_EXPLOSION

    def getType(self):
        return self.TYPE

    def getFormatter(self):
        return _singleVehRibbonFormatter


@HWReceiveDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.HALLOWEEN_ABILITY_VAMPIRE)
class _ReceivedVampireAbilityRibbon(_SingleVehicleReceivedHitRibbon):
    __slots__ = ()
    TYPE = HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_DMG_VAMPIRE_RECEIVED

    def getType(self):
        return self.TYPE

    def getFormatter(self):
        return _singleVehRibbonFormatter


@HWReceiveDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.HALLOWEEN_ABILITY_AOE_DAMAGE)
class _ReceivedAOEDamageAbilityHitRibbon(_SingleVehicleReceivedHitRibbon):
    __slots__ = ()
    TYPE = HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_AOE_DAMAGE_RECEIVED

    def getType(self):
        return self.TYPE

    def getFormatter(self):
        return _singleVehRibbonFormatter


@HWReceiveDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.FIRE, ATTACK_REASON.HALLOWEEN_DEATH_ZONE_IGNITE)
class _HWDeathZoneIgniteDamageRibbon(_SingleVehicleReceivedHitRibbon):
    __slots__ = ()
    TYPE = HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_IGNITE_DAMAGE_RECEIVED

    def getType(self):
        return self.TYPE

    def getFormatter(self):
        return _singleVehRibbonFormatter


@HWReceiveDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.HALLOWEEN_DEATH_ZONE_IGNITE)
class _HWDeathZoneSingleIgniteDamageRibbon(_HWDeathZoneIgniteDamageRibbon):
    pass


@HWReceiveDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.HALLOWEEN_DEATH_ZONE_STUN)
class _HWDeathZoneStunDamageRibbon(_SingleVehicleReceivedHitRibbon):
    __slots__ = ()
    TYPE = HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_STUN_DAMAGE_RECEIVED

    def getType(self):
        return self.TYPE

    def getFormatter(self):
        return _singleVehRibbonFormatter


@HWReceiveDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.HALLOWEEN_DEATH_ZONE_INTERVAL)
class _HWDeathZoneIntervalDamageRibbon(_SingleVehicleReceivedHitRibbon):
    __slots__ = ()
    TYPE = HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_DAMAGE_OVERTIME_RECEIVED

    def getType(self):
        return self.TYPE

    def getDamageSource(self):
        return DAMAGE_SOURCE.HIDE

    def getFormatter(self):
        return _singleVehRibbonFormatter


@HWReceiveDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.HALLOWEEN_DEATH_ZONE)
class _HWStaticDeathZoneRibbon(_SingleVehicleReceivedHitRibbon):
    __slots__ = ()
    TYPE = BATTLE_EFFICIENCY_TYPES.STATIC_DEATH_ZONE

    def getType(self):
        return self.TYPE

    def getDamageSource(self):
        return DAMAGE_SOURCE.HIDE

    def getFormatter(self):
        return _singleVehRibbonFormatter


@HWReceiveDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.HALLOWEEN_CORROSION)
class _HWCorrosionDamageRibbon(_SingleVehicleReceivedHitRibbon):
    __slots__ = ()
    TYPE = HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_CORROSION_DAMAGE

    def getType(self):
        return self.TYPE

    def getDamageSource(self):
        return DAMAGE_SOURCE.HIDE

    def getFormatter(self):
        return _singleVehRibbonFormatter


@HWReceiveDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.HALLOWEEN_STOMPING)
class _HWStompingDamageRibbon(_SingleVehicleReceivedHitRibbon):
    __slots__ = ()
    TYPE = HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_STOMPING_DAMAGE

    def getType(self):
        return self.TYPE

    def getFormatter(self):
        return _singleVehRibbonFormatter


@HWGameplayActionRibbonsFactory.registerActionRibbon(HWGameplayActionID.VEHICLE_REPAIR_INCOMING)
class _HWIncomingRepairRibbon(_HWGameplayActionRibbon):
    BATTLE_EFFICIENCY_TYPE = HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_REPAIR

    @property
    def healerID(self):
        return self.vehicleID

    @property
    def isSelfHeal(self):
        return self._isPlayerVehicle

    def getType(self):
        return HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_REPAIR if self.isSelfHeal else HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_REPAIR_BY_OTHER

    def _canAggregate(self, ribbon):
        return super(_HWIncomingRepairRibbon, self)._canAggregate(ribbon) and self.healerID == ribbon.healerID


@HWGameplayActionRibbonsFactory.registerActionRibbon(HWGameplayActionID.VEHICLE_REPAIR_OUTCOMING)
class _HWOutcomingRepairRibbon(_HWGameplayActionRibbon):
    BATTLE_EFFICIENCY_TYPE = HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_REPAIR_OTHER

    @property
    def isShowActionSource(self):
        return False

    def _canAggregate(self, ribbon):
        return isinstance(ribbon, self.__class__) and ribbon.actionID == self.actionID


@HWGameplayActionRibbonsFactory.registerActionRibbon(HWGameplayActionID.MODULES_DAMAGE_BLOCKED)
class _HWModulesDamageBlockedRibbon(_HWGameplayActionRibbon):
    BATTLE_EFFICIENCY_TYPE = HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_MODULES_DAMAGE_BLOCKED

    @property
    def isShowActionSource(self):
        return False

    def getFormatter(self):
        return _hwCounterRibbonFormatter

    def _canAggregate(self, ribbon):
        return isinstance(ribbon, self.__class__) and ribbon.actionID == self.actionID

    def _aggregate(self, ribbon):
        self._actionValue += ribbon.actionValue


@HWGameplayActionRibbonsFactory.registerActionRibbon(HWGameplayActionID.HEALTH_DRAINED_BY_PASSIVE_VAMPIRE)
class _HWHealthDrainedByPassiveVampireRibbon(_HWGameplayActionRibbon):
    BATTLE_EFFICIENCY_TYPE = HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_PASSIVE_VAMPIRE

    @property
    def isShowActionSource(self):
        return False

    def _canAggregate(self, ribbon):
        return isinstance(ribbon, self.__class__) and ribbon.actionID == self.actionID


@HWGameplayActionRibbonsFactory.registerActionRibbon(HWGameplayActionID.SHELLS_LOOT_PICKUP)
class _HWShellsPickupRibbon(_HWGameplayActionRibbon):
    BATTLE_EFFICIENCY_TYPE = HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_SHELLS_PICKUP

    @property
    def isShowActionSource(self):
        return False

    def getFormatter(self):
        return _hwShellsPickupRibbonFormatter

    def _canAggregate(self, ribbon):
        return isinstance(ribbon, self.__class__) and ribbon.actionID == self.actionID


@HWGameplayActionRibbonsFactory.registerActionRibbon(HWGameplayActionID.SHELLS_LOOT_RECEIVE)
class _HWShellsReceiveRibbon(_HWGameplayActionRibbon):
    BATTLE_EFFICIENCY_TYPE = HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_SHELLS_RECEIVE

    @property
    def isShowActionSource(self):
        return True

    def getFormatter(self):
        return _hwShellsPickupRibbonFormatter

    def _canAggregate(self, ribbon):
        return isinstance(ribbon, self.__class__) and ribbon.actionID == self.actionID


@HWGameplayActionRibbonsFactory.registerActionRibbon(HWGameplayActionID.SOULS_LOOT_PICKUP)
class _HWSoulsPickupRibbon(_HWGameplayActionRibbon):
    BATTLE_EFFICIENCY_TYPE = HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_SOULS_PICKUP

    @property
    def isShowActionSource(self):
        return False

    def getFormatter(self):
        return _hwShellsPickupRibbonFormatter

    def _canAggregate(self, ribbon):
        return isinstance(ribbon, self.__class__) and ribbon.actionID == self.actionID


@HWGameplayActionRibbonsFactory.registerActionRibbon(HWGameplayActionID.SOULS_MIRIUMIZATION_ADD)
class _HWSoulsMiriumizationAddedRibbon(_HWSoulsPickupRibbon):
    pass


@HWGameplayActionRibbonsFactory.registerActionRibbon(HWGameplayActionID.SOULS_MIRIUMIZATION_DECREASE)
class _HWSoulsMiriumizationDecreasedRibbon(_HWSoulsPickupRibbon):
    BATTLE_EFFICIENCY_TYPE = HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_SOULS_DRAINED

    def getFormatter(self):
        return _hwSoulsMiriumizationDecreaseRibbonFormatter


@HWGameplayActionRibbonsFactory.registerActionRibbon(HWGameplayActionID.SOULS_LOOT_RECEIVE)
class _HWSoulsReceiveRibbon(_HWGameplayActionRibbon):
    BATTLE_EFFICIENCY_TYPE = HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_SOULS_RECEIVE

    @property
    def isShowActionSource(self):
        return True

    def getFormatter(self):
        return _hwShellsPickupRibbonFormatter

    def _canAggregate(self, ribbon):
        return isinstance(ribbon, self.__class__) and ribbon.actionID == self.actionID


@HWGameplayActionRibbonsFactory.registerActionRibbon(HWGameplayActionID.SOULS_LOOT_REFUND)
class _HWSoulsRefundRibbon(_HWGameplayActionRibbon):
    BATTLE_EFFICIENCY_TYPE = HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_SOULS_REFUND

    @property
    def isShowActionSource(self):
        return False

    def getFormatter(self):
        return _hwSoulsRefundRibbonFormatter

    def _canAggregate(self, ribbon):
        return isinstance(ribbon, self.__class__) and ribbon.actionID == self.actionID


@HWGameplayActionRibbonsFactory.registerActionRibbon(HWGameplayActionID.HANGAR_ITEMS_LOOT_PICKUP)
class _HWHangarItemPickupRibbon(_HWGameplayActionRibbon):
    BATTLE_EFFICIENCY_TYPE = HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_HANGAR_ITEMS_PICKUP

    @property
    def isShowActionSource(self):
        return False

    def getFormatter(self):
        return _hwCounterRibbonFormatter

    def _canAggregate(self, ribbon):
        return isinstance(ribbon, self.__class__) and ribbon.actionID == self.actionID


@HWGameplayActionRibbonsFactory.registerActionRibbon(HWGameplayActionID.HANGAR_ITEMS_LOOT_RECEIVE)
class _HWHangarItemReceiveRibbon(_HWHangarItemPickupRibbon):
    BATTLE_EFFICIENCY_TYPE = HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_HANGAR_ITEMS_RECEIVE

    @property
    def isShowActionSource(self):
        return True


@HWGameplayActionRibbonsFactory.registerActionRibbon(HWGameplayActionID.ANOMALY_LOOT_PICKUP)
class _HWAnomalyPickupRibbon(_HWGameplayActionRibbon):
    BATTLE_EFFICIENCY_TYPE = HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_ANOMALY_PICKUP

    @property
    def isShowActionSource(self):
        return False

    def getFormatter(self):
        return _hwWithoutLeftFieldRibbonFormatter

    def _canAggregate(self, ribbon):
        return isinstance(ribbon, self.__class__) and ribbon.actionID == self.actionID


@HWGameplayActionRibbonsFactory.registerActionRibbon(HWGameplayActionID.ANOMALY_LOOT_RECEIVE)
class _HWAnomalyReceiveRibbon(_HWAnomalyPickupRibbon):
    BATTLE_EFFICIENCY_TYPE = HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_ANOMALY_RECEIVE

    @property
    def isShowActionSource(self):
        return True


@HWGameplayActionRibbonsFactory.registerActionRibbon(HWGameplayActionID.BOMBER_RESIST)
class _HWBomberResistRibbon(_HWGameplayActionRibbon):
    BATTLE_EFFICIENCY_TYPE = HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_BOMBER_RESIST

    @property
    def isShowActionSource(self):
        return False

    def getFormatter(self):
        return _hwCounterRibbonFormatter


@hwExcludeRibbons(_RIBBON_TYPES_EXCLUDED_IF_KILL_RIBBON + (BATTLE_EFFICIENCY_TYPES.DESTRUCTION,))
@HWDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.HALLOWEEN_INSTANT_KILL)
class _HWInstantKillRibbon(_HWEnemyKillRibbon):
    __slots__ = ()
    BATTLE_EFFICIENCY_TYPE = HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_INSTANT_KILL

    def getFormatter(self):
        return _hwWithoutLeftFieldRibbonFormatter


class HWRibbonsAggregator(RibbonsAggregator):
    FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY = _HW_FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY
    FEEDBACK_EVENTS_TO_IGNORE = _HW_FEEDBACK_EVENTS_TO_IGNORE
    RIBBON_TYPES_AGGREGATED_WITH_KILL_RIBBON = _HW_RIBBON_TYPES_AGGREGATED_WITH_KILL_RIBBON
    RIBBON_TYPES_COPY_TO = _HW_RIBBON_TYPES_COPY_TO
    EXCLUDED_RIBBONS = _HW_EXCLUDED_RIBBONS

    def _aggregateRibbons(self, ribbons):
        filteredRibbons = []
        ribbonsByType = {}
        for ribbon in ribbons:
            if ribbon is None:
                continue
            ribbonsByType.setdefault(ribbon.getType(), set()).add(ribbon)
            filteredRibbons.append(ribbon)

        ribbonsForRemove = set()
        for ribbon in filteredRibbons:
            for excludeRibbonType in self.EXCLUDED_RIBBONS.get(ribbon.__class__, set()):
                if excludeRibbonType in ribbonsByType:
                    ribbonsForRemove.update(ribbonsByType.pop(excludeRibbonType))

            for ribbonToCopyType in self.RIBBON_TYPES_COPY_TO.get(ribbon.__class__, set()):
                for r in ribbonsByType.get(ribbonToCopyType, set()):
                    if r.aggregate(ribbon) and getattr(ribbon, 'hwIsMergeCopy', False):
                        ribbonsForRemove.add(ribbon)

        return super(HWRibbonsAggregator, self)._aggregateRibbons([ r for r in filteredRibbons if r not in ribbonsForRemove ])


class _HWStunAssistRibbon(_StunAssistRibbon):

    def getDamageSource(self):
        return DAMAGE_SOURCE.HIDE

    def _canAggregate(self, ribbon):
        return isinstance(ribbon, self.__class__)


@registerRibbonsFactory(FEEDBACK_EVENT_ID.PLAYER_ASSIST_TO_KILL_ENEMY)
class HWAssistToKillEnemyRibbonsFactory(_AssistRibbonClassFactory):

    def __init__(self):
        _AssistRibbonClassFactory.__init__(self, trackAssistCls=_TrackAssistRibbon, radioAssistCls=_RadioAssistRibbon, stunAssistCls=_HWStunAssistRibbon)


@registerRibbonsFactory(FEEDBACK_EVENT_ID.PLAYER_ASSIST_TO_STUN_ENEMY)
class HWAssistToStunEnemyRibbonsFactory(_AssistRibbonClassFactory):

    def __init__(self):
        _AssistRibbonClassFactory.__init__(self, trackAssistCls=_TrackAssistRibbon, radioAssistCls=_RadioAssistRibbon, stunAssistCls=_HWStunAssistRibbon)


class HWRibbonsAggregatorPlayer(HWRibbonsAggregator):

    def _onPlayerFeedbackReceived(self, events):
        if BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            self.suspend()
        super(HWRibbonsAggregatorPlayer, self)._onPlayerFeedbackReceived(events)

    def _aggregateRibbons(self, ribbons):
        replayRibbons = []
        for ribbon in ribbons:
            if ribbon is None or BattleReplay.g_replayCtrl.isTimeWarpInProgress and ribbon.getType() not in _ACCUMULATED_RIBBON_TYPES:
                continue
            replayRibbons.append(ribbon)

        super(HWRibbonsAggregatorPlayer, self)._aggregateRibbons(replayRibbons)
        return


def createRibbonsAggregator():
    return HWRibbonsAggregatorPlayer() if BattleReplay.g_replayCtrl.isPlaying else HWRibbonsAggregator()
