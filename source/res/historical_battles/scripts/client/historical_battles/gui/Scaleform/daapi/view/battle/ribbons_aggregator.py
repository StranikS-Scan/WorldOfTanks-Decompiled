# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/ribbons_aggregator.py
from collections import defaultdict
import logging
import BattleReplay
from constants import ROLE_TYPE, ATTACK_REASON
from gui.Scaleform.genConsts.BATTLE_EFFICIENCY_TYPES import BATTLE_EFFICIENCY_TYPES
from historical_battles_common.hb_constants_extension import BATTLE_EVENT_TYPE
from historical_battles.gui.battle_control.hb_battle_constants import FEEDBACK_EVENT_ID
from gui.Scaleform.daapi.view.battle.shared.ribbons_aggregator import RibbonsAggregator
from HBBattleFeedbackComponent import HBBattleFeedbackComponent
_logger = logging.getLogger(__name__)
HB_ACTION_NAME_TO_EFFICIENCY_TYPES = {BATTLE_EVENT_TYPE.HEAL_VEHICLE_APPLIED_ACTION: BATTLE_EFFICIENCY_TYPES.HEAL_VEHICLE_APPLIED,
 BATTLE_EVENT_TYPE.TOTAL_VEHICLES_HEAL_APPLIED_ACTION: BATTLE_EFFICIENCY_TYPES.TOTAL_VEHICLES_HEAL_APPLIED,
 BATTLE_EVENT_TYPE.HEAL_SELF_VEHICLE_APPLIED_ACTION: BATTLE_EFFICIENCY_TYPES.HEAL_SELF_VEHICLE_APPLIED}

class DAMAGE_SOURCE:
    PLAYER = 'player'
    ARTILLERY = 'artillery'
    BOMBERS = 'airstrike'


class _Ribbon(object):
    __slots__ = ('_id', '_isAggregating')

    def __init__(self, ribbonID):
        super(_Ribbon, self).__init__()
        self._id = ribbonID
        self._isAggregating = True

    @classmethod
    def createFromFeedbackEvent(cls, ribbonID, event):
        raise NotImplementedError

    def getType(self):
        raise NotImplementedError

    def isRoleBonus(self):
        return False

    def getID(self):
        return self._id

    def aggregate(self, ribbon):
        if self._canAggregate(ribbon):
            self._aggregate(ribbon)
            return True
        return False

    @property
    def isAggregating(self):
        return self._isAggregating

    def _aggregate(self, ribbon):
        self._isAggregating = False

    def _canAggregate(self, ribbon):
        return self.getType() == ribbon.getType()


class _RoleRibbon(_Ribbon):
    __slots__ = ('_isRoleBonus', '_role')

    def __init__(self, ribbonID, isRoleBonus, role):
        super(_RoleRibbon, self).__init__(ribbonID)
        self._isRoleBonus = isRoleBonus
        self._role = role

    @classmethod
    def createFromFeedbackEvent(cls, ribbonID, event):
        raise NotImplementedError

    def isRoleBonus(self):
        return self._isRoleBonus

    def role(self):
        return self._role


class _BasePointsRibbon(_Ribbon):
    __slots__ = ('_points',)

    def __init__(self, ribbonID, points):
        super(_BasePointsRibbon, self).__init__(ribbonID)
        self._points = points

    @classmethod
    def createFromFeedbackEvent(cls, ribbonID, event):
        return cls(ribbonID, event.getExtra())

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


class _SingleVehicleRibbon(_RoleRibbon):
    __slots__ = ('_extraValue', '_targetVehID')

    def __init__(self, ribbonID, vehID, isRoleBonus, role, extraValue):
        super(_SingleVehicleRibbon, self).__init__(ribbonID, isRoleBonus, role)
        self._extraValue = extraValue
        self._targetVehID = vehID

    @classmethod
    def createFromFeedbackEvent(cls, ribbonID, event):
        return cls(ribbonID, event.getTargetID(), _isRoleBonus(event), event.getRole(), cls._extractExtraValue(event))

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
    __slots__ = ()

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
        return cls(ribbonID, event.getTargetID(), False, event.getRole(), cls._extractExtraValue(event))

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
        return BATTLE_EFFICIENCY_TYPES.ARTILLERY


class _ArtilleryRocketHitRibbon(_SingleVehicleDamageRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.DAMAGE_BY_ARTILLERY_ROCKET


class _ArtilleryMortarHitRibbon(_SingleVehicleDamageRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.DAMAGE_BY_ARTILLERY_MORTAR


class _BombersHitRibbon(_SingleVehicleDamageRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.BOMBERS


class _BombercasHitRibbon(_SingleVehicleDamageRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.DAMAGE_BY_BOMBERCAS


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


class _SpawnedBotCausedDamageRibbon(_SingleVehicleDamageRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.SPAWNED_BOT_DMG


class _MinefieldDamageRibbon(_SingleVehicleDamageRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.DAMAGE_BY_HB_MINEFIELD


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
    __slots__ = ()

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

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.RECEIVED_BOMBERS_DAMAGE

    def getDamageSource(self):
        return DAMAGE_SOURCE.PLAYER


class _ReceivedFireHitRibbon(_SingleVehicleReceivedHitRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.RECEIVED_BURN


class _ReceivedBerserkerHitRibbon(_SingleVehicleReceivedHitRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.BERSERKER


class _ReceivedBySpawnedBotHitRibbon(_SingleVehicleReceivedHitRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.RECEIVED_DMG_BY_SPAWNED_BOT


class _ReceivedByMinefieldRibbon(_SingleVehicleReceivedHitRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.RECEIVED_BY_MINEFIELD


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


class _MultiTargetsRibbon(_RoleRibbon):
    __slots__ = ('_targetsAmount',)

    def __init__(self, ribbonID, isRoleBonus, role, extraValue):
        super(_MultiTargetsRibbon, self).__init__(ribbonID, isRoleBonus, role)
        self._targetsAmount = self._extractTargetsAmount(extraValue)

    @classmethod
    def _extractExtraValue(cls, event):
        return event.getExtra()

    @classmethod
    def _extractTargetsAmount(cls, _):
        raise NotImplementedError

    def getTargetsAmount(self):
        return self._targetsAmount

    def _canAggregate(self, ribbon):
        return super(_MultiTargetsRibbon, self)._canAggregate(ribbon) and self.isRoleBonus() == ribbon.isRoleBonus()

    def _aggregate(self, ribbon):
        self._targetsAmount += ribbon.getTargetsAmount()


class _EnemiesStunRibbon(_MultiTargetsRibbon):
    __slots__ = ()

    @classmethod
    def createFromFeedbackEvent(cls, ribbonID, event):
        return cls(ribbonID, _isRoleBonus(event), event.getRole(), cls._extractExtraValue(event))

    @classmethod
    def _extractTargetsAmount(cls, extraValue):
        return extraValue.getTargetsAmount()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.STUN


class _ReceivedDamageByUnknownSourceRibbon(_RoleRibbon):
    __slots__ = ('__extraValue',)

    def __init__(self, ribbonID, extra):
        super(_ReceivedDamageByUnknownSourceRibbon, self).__init__(ribbonID, False, ROLE_TYPE.NOT_DEFINED)
        self.__extraValue = extra

    def getDamageSource(self):
        pass

    def setExtraValue(self, value):
        self.__extraValue = value

    def getExtraValue(self):
        return self.__extraValue

    @classmethod
    def createFromFeedbackEvent(cls, ribbonID, event):
        return cls(ribbonID, event.getExtra().getDamage())


class _ReceivedByDamagingSmokeRibbon(_ReceivedDamageByUnknownSourceRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.RECEIVED_BY_SMOKE


class _DeathZoneRibbon(_SingleVehicleReceivedHitRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.HB_DEATH_ZONE

    def getDamageSource(self):
        pass

    def _aggregate(self, ribbon):
        self.setExtraValue(ribbon.getExtraValue())


class _PersonalDeathZoneRibbon(_SingleVehicleReceivedHitRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.HB_PERSONAL_DEATH_ZONE

    def _aggregate(self, ribbon):
        self.setExtraValue(ribbon.getExtraValue())


class _MultiVehicleRibbon(_MultiTargetsRibbon):
    __slots__ = ('_vehicles',)

    def __init__(self, ribbonID, vehID, isRoleBonus, role, extraValue):
        super(_MultiVehicleRibbon, self).__init__(ribbonID, isRoleBonus, role, extraValue)
        self._vehicles = defaultdict(int)
        self._vehicles[vehID] = extraValue

    @classmethod
    def createFromFeedbackEvent(cls, ribbonID, event):
        return cls(ribbonID, event.getTargetID(), _isRoleBonus(event), event.getRole(), cls._extractExtraValue(event))

    def getVehIDs(self):
        return self._vehicles.keys()

    def getExtraValue(self, vehID):
        return self._vehicles[vehID]

    def getTotalExtraValue(self):
        return sum(self._vehicles.itervalues())

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
    __slots__ = ('__damageCls', '__fireCls', '__ramCls', '__wcCls', '__artDmgCls', '__artRocketDmgCls', '__artMortarDmgCls', '__bombDmgCls', '__bombercasDmgCls', '__artFireCls', '__bombFireCls', '__recoveryCls', '__deathZoneCls', '__personalDeathZoneCls', '__berserker', '__spawnedBotDmgCls', '__damageByMinefield', '__damagedBySmoke')

    def __init__(self, damageCls, fireCls, ramCls, wcCls, artDmgCls, artRocketDmgCls, artMortarDmgCls, bombDmgCls, bombercasDmgCls, artFireCls, bombFireCls, deathZoneCls, personalDeathZoneCls, recoveryCls, berserker, spawnedBotDmgCls, minefieldDamageCls, damagedBySmoke):
        super(_DamageRibbonClassFactory, self).__init__()
        self.__damageCls = damageCls
        self.__fireCls = fireCls
        self.__ramCls = ramCls
        self.__wcCls = wcCls
        self.__artDmgCls = artDmgCls
        self.__artRocketDmgCls = artRocketDmgCls
        self.__artMortarDmgCls = artMortarDmgCls
        self.__artFireCls = artFireCls
        self.__bombDmgCls = bombDmgCls
        self.__bombercasDmgCls = bombercasDmgCls
        self.__bombFireCls = bombFireCls
        self.__recoveryCls = recoveryCls
        self.__deathZoneCls = deathZoneCls
        self.__personalDeathZoneCls = personalDeathZoneCls
        self.__berserker = berserker
        self.__spawnedBotDmgCls = spawnedBotDmgCls
        self.__damageByMinefield = minefieldDamageCls
        self.__damagedBySmoke = damagedBySmoke

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
            ribbonCls = self.__artDmgCls
        elif damageExtra.isArtilleryRocket():
            ribbonCls = self.__artRocketDmgCls
        elif damageExtra.isArtilleryMortar():
            ribbonCls = self.__artMortarDmgCls
        elif damageExtra.isBombers() or damageExtra.isBomberEq():
            ribbonCls = self.__bombDmgCls
        elif damageExtra.isBombercas():
            ribbonCls = self.__bombercasDmgCls
        elif damageExtra.isAttackReason(ATTACK_REASON.RECOVERY):
            ribbonCls = self.__recoveryCls
        elif damageExtra.isDeathZone():
            ribbonCls = self.__deathZoneCls
        elif damageExtra.isPersonalDeathZone():
            ribbonCls = self.__personalDeathZoneCls
        elif damageExtra.isBerserker():
            ribbonCls = self.__berserker
        elif damageExtra.isSpawnedBotExplosion() or damageExtra.isSpawnedBotRam():
            ribbonCls = self.__spawnedBotDmgCls
        elif damageExtra.isMineField():
            ribbonCls = self.__damageByMinefield
        elif damageExtra.isDamagingSmoke():
            ribbonCls = self.__damagedBySmoke
        else:
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
        if event.getBattleEventType() == BATTLE_EVENT_TYPE.TRACK_ASSIST:
            return self.__trackAssistCls
        elif event.getBattleEventType() == BATTLE_EVENT_TYPE.RADIO_ASSIST:
            return self.__radioAssistCls
        else:
            return self.__stunAssistCls if event.getBattleEventType() == BATTLE_EVENT_TYPE.STUN_ASSIST else None


class _EpicBaseRibbon(_Ribbon):
    __slots__ = ()

    @classmethod
    def createFromFeedbackEvent(cls, ribbonID, event):
        return cls(ribbonID)

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
        return cls(ribbonID, event.getTargetID(), False, event.getRole(), cls._extractExtraValue(event))

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


class _RibbonEventActionAppliedLogs(_Ribbon):
    __slots__ = ('actionValue', 'actionID', '_effType', 'victimID')

    def __init__(self, ribbonID, actionCtx):
        super(_RibbonEventActionAppliedLogs, self).__init__(ribbonID)
        self.victimID, self.actionValue, self.actionID = actionCtx
        self._effType = HB_ACTION_NAME_TO_EFFICIENCY_TYPES.get(self.actionID)
        HBBattleFeedbackComponent.onVehicleHeal(self.actionID)

    @classmethod
    def createFromFeedbackEvent(cls, ribbonID, event):
        return cls(ribbonID, event.getExtra())

    def getType(self):
        return self._effType

    def _canAggregate(self, ribbon):
        return False


_ACCUMULATED_RIBBON_TYPES = (BATTLE_EFFICIENCY_TYPES.CAPTURE, BATTLE_EFFICIENCY_TYPES.BASE_CAPTURE_BLOCKED)

def _isRoleBonus(event):
    return getattr(event.getExtra(), 'isRoleAction', lambda : False)()


class HBRibbonsAggregator(RibbonsAggregator):
    _FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY = {FEEDBACK_EVENT_ID.PLAYER_CAPTURED_BASE: _RibbonSingleClassFactory(_BaseCaptureRibbon),
     FEEDBACK_EVENT_ID.PLAYER_DROPPED_CAPTURE: _RibbonSingleClassFactory(_BaseDefenceRibbon),
     FEEDBACK_EVENT_ID.PLAYER_BLOCKED_CAPTURE: _RibbonSingleClassFactory(_BaseCaptureBlocked),
     FEEDBACK_EVENT_ID.PLAYER_SPOTTED_ENEMY: _RibbonSingleClassFactory(_EnemyDetectionRibbon),
     FEEDBACK_EVENT_ID.PLAYER_STUN_ENEMIES: _RibbonSingleClassFactory(_EnemiesStunRibbon),
     FEEDBACK_EVENT_ID.PLAYER_USED_ARMOR: _RibbonSingleClassFactory(_BlockedDamageRibbon),
     FEEDBACK_EVENT_ID.PLAYER_DAMAGED_DEVICE_ENEMY: _RibbonSingleClassFactory(_CriticalHitRibbon),
     FEEDBACK_EVENT_ID.PLAYER_KILLED_ENEMY: _RibbonSingleClassFactory(_EnemyKillRibbon),
     FEEDBACK_EVENT_ID.ENEMY_DAMAGED_DEVICE_PLAYER: _CriticalRibbonClassFactory(),
     FEEDBACK_EVENT_ID.PLAYER_DAMAGED_HP_ENEMY: _DamageRibbonClassFactory(damageCls=_CausedDamageRibbon, fireCls=_FireHitRibbon, ramCls=_RamHitRibbon, wcCls=_WorldCollisionHitRibbon, artDmgCls=_ArtilleryHitRibbon, bombDmgCls=_BombersHitRibbon, bombercasDmgCls=_BombercasHitRibbon, artFireCls=_ArtilleryFireHitRibbon, bombFireCls=_BombersFireHitRibbon, recoveryCls=_EpicRecoveryRibbon, deathZoneCls=_DeathZoneRibbon, personalDeathZoneCls=_PersonalDeathZoneRibbon, artRocketDmgCls=_ArtilleryRocketHitRibbon, artMortarDmgCls=_ArtilleryMortarHitRibbon, berserker=_ReceivedBerserkerHitRibbon, spawnedBotDmgCls=_SpawnedBotCausedDamageRibbon, minefieldDamageCls=_MinefieldDamageRibbon, damagedBySmoke=_ReceivedByDamagingSmokeRibbon),
     FEEDBACK_EVENT_ID.ENEMY_DAMAGED_HP_PLAYER: _DamageRibbonClassFactory(damageCls=_ReceivedDamageHitRibbon, fireCls=_ReceivedFireHitRibbon, ramCls=_ReceivedRamHitRibbon, wcCls=_ReceivedWorldCollisionHitRibbon, artDmgCls=_ArtilleryReceivedDamageHitRibbon, bombDmgCls=_BombersReceivedDamageHitRibbon, bombercasDmgCls=_BombercasHitRibbon, artFireCls=_ArtilleryReceivedFireHitRibbon, bombFireCls=_BombersReceivedFireHitRibbon, recoveryCls=_EpicRecoveryRibbon, deathZoneCls=_DeathZoneRibbon, personalDeathZoneCls=_PersonalDeathZoneRibbon, artRocketDmgCls=_ArtilleryRocketHitRibbon, artMortarDmgCls=_ArtilleryMortarHitRibbon, berserker=_ReceivedBerserkerHitRibbon, spawnedBotDmgCls=_ReceivedBySpawnedBotHitRibbon, minefieldDamageCls=_ReceivedByMinefieldRibbon, damagedBySmoke=_ReceivedByDamagingSmokeRibbon),
     FEEDBACK_EVENT_ID.PLAYER_ASSIST_TO_KILL_ENEMY: _AssistRibbonClassFactory(trackAssistCls=_TrackAssistRibbon, radioAssistCls=_RadioAssistRibbon, stunAssistCls=_StunAssistRibbon),
     FEEDBACK_EVENT_ID.PLAYER_ASSIST_TO_STUN_ENEMY: _AssistRibbonClassFactory(trackAssistCls=_TrackAssistRibbon, radioAssistCls=_RadioAssistRibbon, stunAssistCls=_StunAssistRibbon),
     FEEDBACK_EVENT_ID.ENEMY_SECTOR_CAPTURED: _RibbonSingleClassFactory(_EpicEnemySectorCapturedRibbon),
     FEEDBACK_EVENT_ID.DESTRUCTIBLE_DAMAGED: _RibbonSingleClassFactory(_EpicDestructibleDamaged),
     FEEDBACK_EVENT_ID.DESTRUCTIBLE_DESTROYED: _RibbonSingleClassFactory(_EpicDestructibleDestroyed),
     FEEDBACK_EVENT_ID.DESTRUCTIBLES_DEFENDED: _RibbonSingleClassFactory(_EpicDestructiblesDefended),
     FEEDBACK_EVENT_ID.DEFENDER_BONUS: _RibbonSingleClassFactory(_EpicDefenderBonus),
     FEEDBACK_EVENT_ID.SMOKE_ASSIST: _RibbonSingleClassFactory(_EpicAbilityAssist),
     FEEDBACK_EVENT_ID.INSPIRE_ASSIST: _RibbonSingleClassFactory(_EpicAbilityAssist),
     FEEDBACK_EVENT_ID.HB_ACTION_APPLIED: _RibbonSingleClassFactory(_RibbonEventActionAppliedLogs)}
    _FEEDBACK_EVENTS_TO_IGNORE = (FEEDBACK_EVENT_ID.EQUIPMENT_TIMER_EXPIRED,)


class HBRibbonsAggregatorPlayer(HBRibbonsAggregator):

    def _onPlayerFeedbackReceived(self, events):
        if BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            self.suspend()
        else:
            self.resume()
        super(HBRibbonsAggregatorPlayer, self)._onPlayerFeedbackReceived(events)

    def _aggregateRibbons(self, ribbons):
        replayRibbons = []
        for ribbon in ribbons:
            if BattleReplay.g_replayCtrl.isTimeWarpInProgress and ribbon.getType() not in _ACCUMULATED_RIBBON_TYPES:
                continue
            replayRibbons.append(ribbon)

        super(HBRibbonsAggregatorPlayer, self)._aggregateRibbons(replayRibbons)


def createHBRibbonsAggregator():
    return HBRibbonsAggregatorPlayer() if BattleReplay.g_replayCtrl.isPlaying else HBRibbonsAggregator()
