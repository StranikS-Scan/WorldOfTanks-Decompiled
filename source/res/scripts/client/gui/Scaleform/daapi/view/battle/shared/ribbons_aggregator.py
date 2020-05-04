# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/ribbons_aggregator.py
from collections import defaultdict
import logging
import Event
import BattleReplay
from ids_generators import SequenceIDGenerator
from gui.Scaleform.genConsts.BATTLE_EFFICIENCY_TYPES import BATTLE_EFFICIENCY_TYPES
from BattleFeedbackCommon import BATTLE_EVENT_TYPE as _BET
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
from gui.battle_control import avatar_getter
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

class DAMAGE_SOURCE():
    PLAYER = 'player'
    ARTILLERY = 'artillery'
    BOMBERS = 'airstrike'


class _Ribbon(object):
    __slots__ = ('_id',)

    def __init__(self, ribbonID):
        super(_Ribbon, self).__init__()
        self._id = ribbonID

    @classmethod
    def createFromFeedbackEvent(cls, ribbonID, event):
        raise NotImplementedError

    def getType(self):
        raise NotImplementedError

    def getID(self):
        return self._id

    def aggregate(self, ribbon):
        if self._canAggregate(ribbon):
            self._aggregate(ribbon)
            return True
        return False

    def _aggregate(self, ribbon):
        pass

    def _canAggregate(self, ribbon):
        return self.getType() == ribbon.getType()


class _BasePointsRibbon(_Ribbon):
    __slots__ = ('_points',)

    def __init__(self, ribbonID, points):
        super(_BasePointsRibbon, self).__init__(ribbonID)
        self._points = points

    @classmethod
    def createFromFeedbackEvent(cls, ribbonID, event):
        return cls(ribbonID, event.getExtra())

    def getType(self):
        raise NotImplementedError

    def getPoints(self):
        return self._points

    def _aggregate(self, ribbon):
        self._points += ribbon.getPoints()


class _BaseCaptureRibbon(_BasePointsRibbon):
    __slots__ = ('_sessionID',)

    def __init__(self, ribbonID, points, sessionID):
        super(_BaseCaptureRibbon, self).__init__(ribbonID, points)
        self._sessionID = sessionID

    @classmethod
    def createFromFeedbackEvent(cls, ribbonID, event):
        return cls(ribbonID, event.getExtra(), event.getTargetID())

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.CAPTURE

    def getSessionID(self):
        return self._sessionID

    def _canAggregate(self, ribbon):
        return super(_BaseCaptureRibbon, self)._canAggregate(ribbon) and self._sessionID == ribbon.getSessionID()


class _BaseCaptureBlocked(_BaseCaptureRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.BASE_CAPTURE_BLOCKED


class _BaseDefenceRibbon(_BasePointsRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.DEFENCE


class _SingleVehicleRibbon(_Ribbon):
    __slots__ = ('_extraValue', '_targetVehID')

    def __init__(self, ribbonID, vehID, extraValue):
        super(_SingleVehicleRibbon, self).__init__(ribbonID)
        self._extraValue = extraValue
        self._targetVehID = vehID

    @classmethod
    def createFromFeedbackEvent(cls, ribbonID, event):
        return cls(ribbonID, event.getTargetID(), cls._extractExtraValue(event))

    def getType(self):
        raise NotImplementedError

    def getExtraValue(self):
        return self._extraValue

    def setExtraValue(self, value):
        self._extraValue = value

    def getVehicleID(self):
        return self._targetVehID

    @classmethod
    def _extractExtraValue(cls, event):
        raise NotImplementedError

    def _canAggregate(self, ribbon):
        return super(_SingleVehicleRibbon, self)._canAggregate(ribbon) and self.getVehicleID() == ribbon.getVehicleID()

    def _aggregate(self, ribbon):
        self._extraValue += ribbon.getExtraValue()

    def getDamageSource(self):
        return DAMAGE_SOURCE.PLAYER


class _SingleVehicleDamageRibbon(_SingleVehicleRibbon):
    __slots__ = ('_isRoleBonus',)

    def __init__(self, ribbonID, vehID, extraValue, isRoleBonus):
        super(_SingleVehicleDamageRibbon, self).__init__(ribbonID, vehID, extraValue)
        self._isRoleBonus = isRoleBonus

    @classmethod
    def createFromFeedbackEvent(cls, ribbonID, event):
        return cls(ribbonID, event.getTargetID(), cls._extractExtraValue(event), _isRoleBonus(event))

    def getType(self):
        raise NotImplementedError

    def isRoleBonus(self):
        return self._isRoleBonus

    @classmethod
    def _extractExtraValue(cls, event):
        return event.getExtra().getDamage()

    def _canAggregate(self, ribbon):
        return super(_SingleVehicleDamageRibbon, self)._canAggregate(ribbon) and self.isRoleBonus() == ribbon.isRoleBonus()


class _CriticalHitRibbon(_SingleVehicleRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.CRITS

    @classmethod
    def _extractExtraValue(cls, event):
        return event.getExtra().getCritsCount()


class _TrackAssistRibbon(_SingleVehicleDamageRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.ASSIST_TRACK


class _RadioAssistRibbon(_SingleVehicleDamageRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.ASSIST_SPOT


class _EnemyKillRibbon(_SingleVehicleDamageRibbon):
    __slots__ = ()

    @classmethod
    def createFromFeedbackEvent(cls, ribbonID, event):
        return cls(ribbonID, event.getTargetID(), cls._extractExtraValue(event), False)

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.DESTRUCTION

    @classmethod
    def _extractExtraValue(cls, event):
        pass

    def _canAggregate(self, ribbon):
        return self.getVehicleID() == ribbon.getVehicleID() and self.isRoleBonus() == ribbon.isRoleBonus()


class _BlockedDamageRibbon(_SingleVehicleDamageRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.ARMOR


class _CausedDamageRibbon(_SingleVehicleDamageRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.DAMAGE


class _FireHitRibbon(_SingleVehicleDamageRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.BURN


class _RamHitRibbon(_SingleVehicleDamageRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.RAM


class _ArtilleryHitRibbon(_SingleVehicleDamageRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.DAMAGE


class _BombersHitRibbon(_SingleVehicleDamageRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.DAMAGE


class _EventAbilityHitRibbon(_SingleVehicleDamageRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.EVENT_ABILITY_DAMAGE


class _EventDeathZoneHitRibbon(_SingleVehicleDamageRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.EVENT_DEATHZONE_DAMAGE

    def getDamageSource(self):
        return DAMAGE_SOURCE.ARTILLERY


class _ArtilleryFireHitRibbon(_SingleVehicleDamageRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.BURN


class _BombersFireHitRibbon(_SingleVehicleDamageRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.BURN


class _WorldCollisionHitRibbon(_SingleVehicleDamageRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.WORLD_COLLISION


class _ReceivedCriticalHitRibbon(_CriticalHitRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.RECEIVED_CRITS


class _ArtilleryCriticalHitRibbon(_ReceivedCriticalHitRibbon):
    __slots__ = ()

    def getDamageSource(self):
        return DAMAGE_SOURCE.ARTILLERY


class _BombersReceivedCriticalHitRibbon(_ReceivedCriticalHitRibbon):
    __slots__ = ()

    def getDamageSource(self):
        return DAMAGE_SOURCE.BOMBERS


class _SingleVehicleReceivedHitRibbon(_SingleVehicleRibbon):
    __slots__ = ('_isRoleBonus',)

    def __init__(self, ribbonID, vehID, extraValue, isRoleBonus):
        super(_SingleVehicleReceivedHitRibbon, self).__init__(ribbonID, vehID, extraValue)
        self._isRoleBonus = isRoleBonus

    @classmethod
    def createFromFeedbackEvent(cls, ribbonID, event):
        return cls(ribbonID, event.getTargetID(), cls._extractExtraValue(event), _isRoleBonus(event))

    def getType(self):
        raise NotImplementedError

    def isRoleBonus(self):
        return self._isRoleBonus

    @classmethod
    def _extractExtraValue(cls, event):
        return event.getExtra().getDamage()

    def _canAggregate(self, ribbon):
        return super(_SingleVehicleReceivedHitRibbon, self)._canAggregate(ribbon) and self.isRoleBonus() == ribbon.isRoleBonus()


class _ReceivedDamageHitRibbon(_SingleVehicleReceivedHitRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.RECEIVED_DAMAGE


class _ArtilleryReceivedDamageHitRibbon(_ReceivedDamageHitRibbon):
    __slots__ = ()

    def getDamageSource(self):
        return DAMAGE_SOURCE.ARTILLERY


class _BombersReceivedDamageHitRibbon(_ReceivedDamageHitRibbon):
    __slots__ = ()

    def getDamageSource(self):
        return DAMAGE_SOURCE.BOMBERS


class _ReceivedFireHitRibbon(_SingleVehicleReceivedHitRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.RECEIVED_BURN


class _BombersReceivedFireHitRibbon(_ReceivedFireHitRibbon):
    __slots__ = ()

    def getDamageSource(self):
        return DAMAGE_SOURCE.BOMBERS


class _ArtilleryReceivedFireHitRibbon(_ReceivedFireHitRibbon):
    __slots__ = ()

    def getDamageSource(self):
        return DAMAGE_SOURCE.ARTILLERY


class _ReceivedRamHitRibbon(_SingleVehicleReceivedHitRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.RECEIVED_RAM


class _ReceivedWorldCollisionHitRibbon(_SingleVehicleReceivedHitRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.RECEIVED_WORLD_COLLISION


class _StunAssistRibbon(_SingleVehicleDamageRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.ASSIST_STUN


class _MultiTargetsRibbon(_Ribbon):
    __slots__ = ('_targetsAmount', '_isRoleBonus')

    def __init__(self, ribbonID, extraValue, isRoleBonus):
        super(_MultiTargetsRibbon, self).__init__(ribbonID)
        self._targetsAmount = self._extractTargetsAmount(extraValue)
        self._isRoleBonus = isRoleBonus

    @classmethod
    def _extractExtraValue(cls, event):
        return event.getExtra()

    @classmethod
    def _extractTargetsAmount(cls, _):
        raise NotImplementedError

    def getTargetsAmount(self):
        return self._targetsAmount

    def isRoleBonus(self):
        return self._isRoleBonus

    def _canAggregate(self, ribbon):
        return super(_MultiTargetsRibbon, self)._canAggregate(ribbon) and self.isRoleBonus() == ribbon.isRoleBonus()

    def _aggregate(self, ribbon):
        self._targetsAmount += ribbon.getTargetsAmount()


class _EnemiesStunRibbon(_MultiTargetsRibbon):
    __slots__ = ()

    @classmethod
    def createFromFeedbackEvent(cls, ribbonID, event):
        return cls(ribbonID, cls._extractExtraValue(event), _isRoleBonus(event))

    @classmethod
    def _extractTargetsAmount(cls, extraValue):
        return extraValue.getTargetsAmount()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.STUN


class _MultiVehicleRibbon(_MultiTargetsRibbon):
    __slots__ = ('_vehicles',)

    def __init__(self, ribbonID, vehID, extraValue, isRoleBonus):
        super(_MultiVehicleRibbon, self).__init__(ribbonID, extraValue, isRoleBonus)
        self._vehicles = defaultdict(int)
        self._vehicles[vehID] = extraValue

    @classmethod
    def createFromFeedbackEvent(cls, ribbonID, event):
        return cls(ribbonID, event.getTargetID(), cls._extractExtraValue(event), _isRoleBonus(event))

    def getVehIDs(self):
        return self._vehicles.keys()

    def getExtraValue(self, vehID):
        return self._vehicles[vehID]

    def getTotalExtraValue(self):
        return sum(self._vehicles.itervalues())

    def isRoleBonus(self):
        return self._isRoleBonus

    def _canAggregate(self, ribbon):
        return super(_MultiVehicleRibbon, self)._canAggregate(ribbon) and self.isRoleBonus() == ribbon.isRoleBonus()

    def _aggregate(self, ribbon):
        super(_MultiVehicleRibbon, self)._aggregate(ribbon)
        for targetID in ribbon.getVehIDs():
            self._vehicles[targetID] += ribbon.getExtraValue(targetID)


class _EnemyDetectionRibbon(_MultiVehicleRibbon):
    __slots__ = ()

    @classmethod
    def _extractExtraValue(cls, _):
        pass

    @classmethod
    def _extractTargetsAmount(cls, _):
        pass

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.DETECTION


class _RibbonClassFactory(object):
    __slots__ = ()

    def getRibbonClass(self, event):
        return None


class _RibbonSingleClassFactory(_RibbonClassFactory):
    __slots__ = ('__cls',)

    def __init__(self, ribbonCls):
        super(_RibbonSingleClassFactory, self).__init__()
        self.__cls = ribbonCls

    def getRibbonClass(self, event):
        return self.__cls


class _CriticalRibbonClassFactory(_RibbonClassFactory):

    def getRibbonClass(self, event):
        damageExtra = event.getExtra()
        if damageExtra.isProtectionZone() or damageExtra.isProtectionZone(primary=False) or damageExtra.isArtilleryEq() or damageExtra.isArtilleryEq(primary=False):
            ribbonCls = _ArtilleryCriticalHitRibbon
        elif damageExtra.isBombers() or damageExtra.isBombers(primary=False) or damageExtra.isBomberEq() or damageExtra.isBomberEq(primary=False):
            ribbonCls = _BombersReceivedCriticalHitRibbon
        else:
            ribbonCls = _ReceivedCriticalHitRibbon
        return ribbonCls


class _DamageRibbonClassFactory(_RibbonClassFactory):
    __slots__ = ('__damageCls', '__fireCls', '__ramCls', '__wcCls', '__artDmgCls', '__bombDmgCls', '__artFireCls', '__bombFireCls', '__recoveryCls', '__eventAbilityCls', '__deathZoneCls')
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, damageCls, fireCls, ramCls, wcCls, artDmgCls, bombDmgCls, artFireCls, bombFireCls, recoveryCls, eventAbilityCls=None, deathZoneCls=None):
        super(_DamageRibbonClassFactory, self).__init__()
        self.__damageCls = damageCls
        self.__fireCls = fireCls
        self.__ramCls = ramCls
        self.__wcCls = wcCls
        self.__artDmgCls = artDmgCls
        self.__artFireCls = artFireCls
        self.__bombDmgCls = bombDmgCls
        self.__bombFireCls = bombFireCls
        self.__recoveryCls = recoveryCls
        self.__eventAbilityCls = eventAbilityCls
        self.__deathZoneCls = deathZoneCls

    def getRibbonClass(self, event):
        damageExtra = event.getExtra()
        if damageExtra.isShot():
            ribbonCls = self.__damageCls
        elif damageExtra.isFire():
            if damageExtra.isBombers(primary=False) or damageExtra.isBomberEq(primary=False):
                ribbonCls = self.__bombFireCls
            elif damageExtra.isProtectionZone(primary=False) or damageExtra.isArtilleryEq(primary=False):
                ribbonCls = self.__artFireCls
            else:
                ribbonCls = self.__fireCls
        elif damageExtra.isWorldCollision():
            ribbonCls = self.__wcCls
        elif damageExtra.isProtectionZone() or damageExtra.isArtilleryEq():
            if self.__eventAbilityCls is not None and self.sessionProvider.arenaVisitor.gui.isEventBattle():
                ribbonCls = self.__eventAbilityCls
            else:
                ribbonCls = self.__artDmgCls
        elif damageExtra.isBombers() or damageExtra.isBomberEq():
            if self.__eventAbilityCls is not None and self.sessionProvider.arenaVisitor.gui.isEventBattle():
                ribbonCls = self.__eventAbilityCls
            else:
                ribbonCls = self.__bombDmgCls
        elif damageExtra.isAttackReason(ATTACK_REASON.RECOVERY):
            ribbonCls = self.__recoveryCls
        elif damageExtra.isAttackReason(ATTACK_REASON.MINEFIELD_EQ):
            ribbonCls = self.__eventAbilityCls
        elif damageExtra.isDeathZone():
            ribbonCls = self.__deathZoneCls
        else:
            if damageExtra.isEventPhaseChange():
                return
            ribbonCls = self.__ramCls
        if not ribbonCls:
            ribbonCls = self.__ramCls
        return ribbonCls


class _AssistRibbonClassFactory(_RibbonClassFactory):
    __slots__ = ('__trackAssistCls', '__radioAssistCls', '__stunAssistCls')

    def __init__(self, trackAssistCls, radioAssistCls, stunAssistCls):
        super(_AssistRibbonClassFactory, self).__init__()
        self.__trackAssistCls = trackAssistCls
        self.__radioAssistCls = radioAssistCls
        self.__stunAssistCls = stunAssistCls

    def getRibbonClass(self, event):
        if event.getBattleEventType() == _BET.TRACK_ASSIST:
            return self.__trackAssistCls
        elif event.getBattleEventType() == _BET.RADIO_ASSIST:
            return self.__radioAssistCls
        else:
            return self.__stunAssistCls if event.getBattleEventType() == _BET.STUN_ASSIST else None


class _EpicBaseRibbon(_Ribbon):
    __slots__ = ()

    @classmethod
    def createFromFeedbackEvent(cls, ribbonID, event):
        return cls(ribbonID)

    def getType(self):
        raise NotImplementedError

    def getExtraValue(self):
        pass


class _EpicRecoveryRibbon(_EpicBaseRibbon):
    __slots__ = ('__extraValue',)

    def __init__(self, ribbonID, extraValue):
        super(_EpicRecoveryRibbon, self).__init__(ribbonID)
        self.__extraValue = extraValue

    @classmethod
    def createFromFeedbackEvent(cls, ribbonID, event):
        return cls(ribbonID, event.getExtra().getDamage())

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.VEHICLE_RECOVERY

    def getExtraValue(self):
        return self.__extraValue


class _EpicEnemySectorCapturedRibbon(_EpicBaseRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.ENEMY_SECTOR_CAPTURED


class _EpicDestructibleDestroyed(_EpicBaseRibbon):
    __slots__ = ('__extraValue',)

    def __init__(self, ribbonID, extraValue):
        super(_EpicDestructibleDestroyed, self).__init__(ribbonID)
        self.__extraValue = extraValue

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.DESTRUCTIBLE_DESTROYED

    @classmethod
    def createFromFeedbackEvent(cls, ribbonID, event):
        return cls(ribbonID, event.getExtra())

    def getExtraValue(self):
        return self.__extraValue


class _EpicDestructiblesDefended(_EpicBaseRibbon):
    __slots__ = ('__extraValue',)

    def __init__(self, ribbonID, extraValue):
        super(_EpicDestructiblesDefended, self).__init__(ribbonID)
        self.__extraValue = extraValue

    @classmethod
    def createFromFeedbackEvent(cls, ribbonID, event):
        return cls(ribbonID, event.getExtra())

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.DESTRUCTIBLES_DEFENDED

    def getExtraValue(self):
        return self.__extraValue


class _EpicDefenderBonus(_EpicBaseRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.DEFENDER_BONUS


class _EpicAbilityAssist(_SingleVehicleReceivedHitRibbon):
    __slots__ = ()

    @classmethod
    def createFromFeedbackEvent(cls, ribbonID, event):
        return cls(ribbonID, event.getTargetID(), cls._extractExtraValue(event), False)

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.ASSIST_BY_ABILITY


class _EpicDestructibleDamaged(_Ribbon):
    __slots__ = ('_damagePoints',)

    def __init__(self, ribbonID, damagePoints):
        super(_EpicDestructibleDamaged, self).__init__(ribbonID)
        self._damagePoints = damagePoints

    @classmethod
    def createFromFeedbackEvent(cls, ribbonID, event):
        return cls(ribbonID, event.getExtra())

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.DESTRUCTIBLE_DAMAGED

    def getExtraValue(self):
        return self._damagePoints

    def _canAggregate(self, ribbon):
        return True

    def _aggregate(self, ribbon):
        self._damagePoints += ribbon.getExtraValue()


_RIBBON_TYPES_AGGREGATED_WITH_KILL_RIBBON = (BATTLE_EFFICIENCY_TYPES.DAMAGE,
 BATTLE_EFFICIENCY_TYPES.BURN,
 BATTLE_EFFICIENCY_TYPES.RAM,
 BATTLE_EFFICIENCY_TYPES.WORLD_COLLISION,
 BATTLE_EFFICIENCY_TYPES.EVENT_ABILITY_DAMAGE)
_RIBBON_TYPES_EXCLUDED_IF_KILL_RIBBON = (BATTLE_EFFICIENCY_TYPES.CRITS,)
_RIBBON_TYPES_EXCLUDED_IN_POSTMORTEM = (BATTLE_EFFICIENCY_TYPES.RECEIVED_CRITS,)
_NOT_CACHED_RIBBON_TYPES = (BATTLE_EFFICIENCY_TYPES.DETECTION, BATTLE_EFFICIENCY_TYPES.DEFENCE, BATTLE_EFFICIENCY_TYPES.STUN)
_ACCUMULATED_RIBBON_TYPES = (BATTLE_EFFICIENCY_TYPES.CAPTURE, BATTLE_EFFICIENCY_TYPES.BASE_CAPTURE_BLOCKED)
_FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY = {FEEDBACK_EVENT_ID.PLAYER_CAPTURED_BASE: _RibbonSingleClassFactory(_BaseCaptureRibbon),
 FEEDBACK_EVENT_ID.PLAYER_DROPPED_CAPTURE: _RibbonSingleClassFactory(_BaseDefenceRibbon),
 FEEDBACK_EVENT_ID.PLAYER_BLOCKED_CAPTURE: _RibbonSingleClassFactory(_BaseCaptureBlocked),
 FEEDBACK_EVENT_ID.PLAYER_SPOTTED_ENEMY: _RibbonSingleClassFactory(_EnemyDetectionRibbon),
 FEEDBACK_EVENT_ID.PLAYER_STUN_ENEMIES: _RibbonSingleClassFactory(_EnemiesStunRibbon),
 FEEDBACK_EVENT_ID.PLAYER_USED_ARMOR: _RibbonSingleClassFactory(_BlockedDamageRibbon),
 FEEDBACK_EVENT_ID.PLAYER_DAMAGED_DEVICE_ENEMY: _RibbonSingleClassFactory(_CriticalHitRibbon),
 FEEDBACK_EVENT_ID.PLAYER_KILLED_ENEMY: _RibbonSingleClassFactory(_EnemyKillRibbon),
 FEEDBACK_EVENT_ID.ENEMY_DAMAGED_DEVICE_PLAYER: _CriticalRibbonClassFactory(),
 FEEDBACK_EVENT_ID.PLAYER_DAMAGED_HP_ENEMY: _DamageRibbonClassFactory(damageCls=_CausedDamageRibbon, fireCls=_FireHitRibbon, ramCls=_RamHitRibbon, wcCls=_WorldCollisionHitRibbon, artDmgCls=_ArtilleryHitRibbon, bombDmgCls=_BombersHitRibbon, artFireCls=_ArtilleryFireHitRibbon, bombFireCls=_BombersFireHitRibbon, recoveryCls=_EpicRecoveryRibbon, eventAbilityCls=_EventAbilityHitRibbon),
 FEEDBACK_EVENT_ID.ENEMY_DAMAGED_HP_PLAYER: _DamageRibbonClassFactory(damageCls=_ReceivedDamageHitRibbon, fireCls=_ReceivedFireHitRibbon, ramCls=_ReceivedRamHitRibbon, wcCls=_ReceivedWorldCollisionHitRibbon, artDmgCls=_ArtilleryReceivedDamageHitRibbon, bombDmgCls=_BombersReceivedDamageHitRibbon, artFireCls=_ArtilleryReceivedFireHitRibbon, bombFireCls=_BombersReceivedFireHitRibbon, recoveryCls=_EpicRecoveryRibbon, deathZoneCls=_EventDeathZoneHitRibbon),
 FEEDBACK_EVENT_ID.PLAYER_ASSIST_TO_KILL_ENEMY: _AssistRibbonClassFactory(trackAssistCls=_TrackAssistRibbon, radioAssistCls=_RadioAssistRibbon, stunAssistCls=_StunAssistRibbon),
 FEEDBACK_EVENT_ID.PLAYER_ASSIST_TO_STUN_ENEMY: _AssistRibbonClassFactory(trackAssistCls=_TrackAssistRibbon, radioAssistCls=_RadioAssistRibbon, stunAssistCls=_StunAssistRibbon),
 FEEDBACK_EVENT_ID.ENEMY_SECTOR_CAPTURED: _RibbonSingleClassFactory(_EpicEnemySectorCapturedRibbon),
 FEEDBACK_EVENT_ID.DESTRUCTIBLE_DAMAGED: _RibbonSingleClassFactory(_EpicDestructibleDamaged),
 FEEDBACK_EVENT_ID.DESTRUCTIBLE_DESTROYED: _RibbonSingleClassFactory(_EpicDestructibleDestroyed),
 FEEDBACK_EVENT_ID.DESTRUCTIBLES_DEFENDED: _RibbonSingleClassFactory(_EpicDestructiblesDefended),
 FEEDBACK_EVENT_ID.DEFENDER_BONUS: _RibbonSingleClassFactory(_EpicDefenderBonus),
 FEEDBACK_EVENT_ID.SMOKE_ASSIST: _RibbonSingleClassFactory(_EpicAbilityAssist),
 FEEDBACK_EVENT_ID.INSPIRE_ASSIST: _RibbonSingleClassFactory(_EpicAbilityAssist)}

def _isRoleBonus(event):
    return event.getExtra().isRoleAction()


def _createRibbonFromPlayerFeedbackEvent(ribbonID, event):
    etype = event.getType()
    if etype in _FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY:
        factory = _FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY[etype]
        ribbonCls = factory.getRibbonClass(event)
        if ribbonCls is not None:
            return ribbonCls.createFromFeedbackEvent(ribbonID, event)
    _logger.error('Could not find a proper ribbon class associated with the given feedback event %s', event)
    return


class ATTACK_REASON(object):
    SHOT = 'shot'
    FIRE = 'fire'
    RAM = 'ramming'
    WORLD_COLLISION = 'world_collision'
    DEATH_ZONE = 'death_zone'
    DROWNING = 'drowning'
    OVERTURN = 'overturn'
    ARTILLERY_PROTECTION = 'artillery_protection'
    ARTILLERY_SECTOR = 'artillery_sector'
    BOMBERS = 'bombers'
    RECOVERY = 'recovery'
    MINEFIELD_EQ = 'minefield_eq'
    PERSONAL_DEATH_ZONE = 'personal_death_zone'


class _RibbonsCache(object):
    __slots__ = ('__ribbons', '__typeToIDs')

    def __init__(self):
        super(_RibbonsCache, self).__init__()
        self.__ribbons = {}
        self.__typeToIDs = defaultdict(set)

    def clear(self):
        self.__ribbons.clear()
        self.__typeToIDs.clear()

    def get(self, ribbonID, default):
        return self.__ribbons.get(ribbonID, default)

    def pop(self, ribbonID):
        if ribbonID in self:
            ribbon = self.__ribbons.pop(ribbonID)
            self.__typeToIDs[ribbon.getType()].remove(ribbonID)
            return ribbon
        else:
            return None

    def add(self, ribbon):
        self[ribbon.getID()] = ribbon
        self.__typeToIDs[ribbon.getType()].add(ribbon.getID())

    def iterByType(self, ribbonType):
        for ribbonID in self.__typeToIDs[ribbonType]:
            yield self[ribbonID]

    def __contains__(self, ribbonID):
        return self.__ribbons.__contains__(ribbonID)

    def __iter__(self):
        return self.__ribbons.__iter__()

    def __len__(self):
        return self.__ribbons.__len__()

    def __getitem__(self, index):
        return self.__ribbons.__getitem__(index)

    def __setitem__(self, ribbonID, ribbon):
        return self.__ribbons.__setitem__(ribbonID, ribbon)


class RibbonsAggregator(object):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(RibbonsAggregator, self).__init__()
        self.__feedbackProvider = None
        self.__vehicleStateCtrl = None
        self.__cache = _RibbonsCache()
        self.__accumulatedRibbons = _RibbonsCache()
        self.__rules = {}
        self.__idGenerator = SequenceIDGenerator()
        self.onRibbonAdded = Event.Event()
        self.onRibbonUpdated = Event.Event()
        self.__isStarted = False
        self.__isSuspended = False
        self.__isInPostmortemMode = False
        return

    def start(self):
        self.__isStarted = True
        if self.__feedbackProvider is None:
            self.__feedbackProvider = self.sessionProvider.shared.feedback
            if self.__feedbackProvider is not None:
                self.__feedbackProvider.onPlayerFeedbackReceived += self._onPlayerFeedbackReceived
        if self.__vehicleStateCtrl is None:
            self.__vehicleStateCtrl = self.sessionProvider.shared.vehicleState
            if self.__vehicleStateCtrl is not None:
                self.__vehicleStateCtrl.onPostMortemSwitched += self._onPostMortemSwitched
                self.__vehicleStateCtrl.onRespawnBaseMoving += self.__onRespawnBaseMoving
        return

    def suspend(self):
        if self.__isStarted:
            self.__isSuspended = True

    def resume(self):
        if self.__isSuspended:
            self.__isSuspended = False

    def stop(self):
        self.__isStarted = False
        self.__isSuspended = False
        self.clearRibbonsData()
        if self.__feedbackProvider is not None:
            self.__feedbackProvider.onPlayerFeedbackReceived -= self._onPlayerFeedbackReceived
            self.__feedbackProvider = None
        if self.__vehicleStateCtrl is not None:
            self.__vehicleStateCtrl.onPostMortemSwitched -= self._onPostMortemSwitched
            self.__vehicleStateCtrl.onRespawnBaseMoving -= self.__onRespawnBaseMoving
            self.__vehicleStateCtrl = None
        return

    def getRibbon(self, ribbonID):
        return self.__cache.get(ribbonID, None)

    def resetRibbonData(self, ribbonID):
        ribbon = self.__cache.pop(ribbonID)
        if ribbon is not None and ribbon.getType() in _ACCUMULATED_RIBBON_TYPES:
            self.__accumulatedRibbons.add(ribbon)
        return

    def clearRibbonsData(self):
        self.__cache.clear()
        self.__accumulatedRibbons.clear()

    def _onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        self.__isInPostmortemMode = True

    def __onRespawnBaseMoving(self):
        self.__isInPostmortemMode = False

    def _onPlayerFeedbackReceived(self, events):

        def _ribbonsGenerator(events):
            for e in events:
                r = _createRibbonFromPlayerFeedbackEvent(self.__idGenerator.next(), e)
                if r is not None:
                    yield r

            return

        self._aggregateRibbons(_ribbonsGenerator(events))

    def _aggregateRibbons(self, ribbons):
        aggregatedRibbons = {}
        for ribbon in ribbons:
            if self.__isSuspended and ribbon.getType() not in _ACCUMULATED_RIBBON_TYPES:
                continue
            if ribbon.getType() in aggregatedRibbons:
                temporaryRibbons = aggregatedRibbons[ribbon.getType()]
                for temporaryRibbon in temporaryRibbons:
                    if temporaryRibbon.aggregate(ribbon):
                        break
                else:
                    temporaryRibbons.append(ribbon)

            aggregatedRibbons[ribbon.getType()] = [ribbon]

        filteredRibbons = self.__filterRibbons(aggregatedRibbons)
        sortedRibbons = self.__getSortedList(filteredRibbons)
        for ribbon in sortedRibbons:
            etype = ribbon.getType()
            if etype in _NOT_CACHED_RIBBON_TYPES:
                self.__cache.add(ribbon)
                self.onRibbonAdded(ribbon)
            for cachedRibbon in self.__cache.iterByType(etype):
                if cachedRibbon.aggregate(ribbon):
                    if not self.__isSuspended:
                        self.onRibbonUpdated(cachedRibbon)
                    break
            else:
                if etype in _ACCUMULATED_RIBBON_TYPES:
                    for accumulatedRibbon in self.__accumulatedRibbons.iterByType(etype):
                        if accumulatedRibbon.aggregate(ribbon):
                            if not self.__isSuspended:
                                self.__accumulatedRibbons.pop(accumulatedRibbon.getID())
                                self.__cache.add(accumulatedRibbon)
                                self.onRibbonAdded(accumulatedRibbon)
                            break
                    else:
                        if self.__isSuspended:
                            self.__accumulatedRibbons.add(ribbon)
                        else:
                            self.__cache.add(ribbon)
                            self.onRibbonAdded(ribbon)
                if not self.__isSuspended:
                    self.__cache.add(ribbon)
                    self.onRibbonAdded(ribbon)

    def __filterRibbons(self, ribbons):
        if self.__isInPostmortemMode and not avatar_getter.isObserver():
            for rType in _RIBBON_TYPES_EXCLUDED_IN_POSTMORTEM:
                if rType in ribbons:
                    del ribbons[rType]

        if BATTLE_EFFICIENCY_TYPES.DESTRUCTION in ribbons:
            killRibbons = dict(((r.getVehicleID(), r) for r in ribbons[BATTLE_EFFICIENCY_TYPES.DESTRUCTION]))
            damageRibbons = dict(((t, ribbons[t]) for t in _RIBBON_TYPES_AGGREGATED_WITH_KILL_RIBBON if t in ribbons))
            for rType, tmpRibbons in damageRibbons.iteritems():
                filteredRibbons = []
                for tmpRibbon in tmpRibbons:
                    if tmpRibbon.getVehicleID() in killRibbons:
                        killRibbon = killRibbons[tmpRibbon.getVehicleID()]
                        if not killRibbon.aggregate(tmpRibbon):
                            filteredRibbons.append(tmpRibbon)
                    filteredRibbons.append(tmpRibbon)

                ribbons[rType] = filteredRibbons

            excludedRibbons = dict(((t, ribbons[t]) for t in _RIBBON_TYPES_EXCLUDED_IF_KILL_RIBBON if t in ribbons))
            for rType, tmpRibbons in excludedRibbons.iteritems():
                filteredRibbons = [ r for r in tmpRibbons if r.getVehicleID() not in killRibbons ]
                ribbons[rType] = filteredRibbons

        return ribbons

    def __getSortedList(self, ribbons):

        def _sortKey(ribbon):
            return ribbon.getID()

        sortedRibons = []
        if ribbons:
            killRibbons = ribbons.pop(BATTLE_EFFICIENCY_TYPES.DESTRUCTION, None)
            detectionRibbons = ribbons.pop(BATTLE_EFFICIENCY_TYPES.DETECTION, None)
            if detectionRibbons is not None:
                sortedRibons.extend(sorted(detectionRibbons, key=_sortKey))
            remaningRibbons = []
            for newRibbons in ribbons.itervalues():
                remaningRibbons.extend(newRibbons)

            sortedRibons.extend(sorted(remaningRibbons, key=_sortKey))
            if killRibbons is not None:
                sortedRibons.extend(sorted(killRibbons, key=_sortKey))
        return sortedRibons


class RibbonsAggregatorPlayer(RibbonsAggregator):

    def _aggregateRibbons(self, ribbons):
        replayRibbons = []
        for ribbon in ribbons:
            if BattleReplay.g_replayCtrl.isTimeWarpInProgress and ribbon.getType() not in _ACCUMULATED_RIBBON_TYPES:
                continue
            replayRibbons.append(ribbon)

        super(RibbonsAggregatorPlayer, self)._aggregateRibbons(replayRibbons)


def createRibbonsAggregator():
    return RibbonsAggregatorPlayer() if BattleReplay.g_replayCtrl.isPlaying else RibbonsAggregator()
