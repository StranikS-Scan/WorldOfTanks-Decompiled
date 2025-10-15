# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/Scaleform/daapi/view/battle/ribbons_aggregator.py
import logging
import BattleReplay
from constants import ATTACK_REASON
from gui.Scaleform.genConsts.BATTLE_EFFICIENCY_TYPES import BATTLE_EFFICIENCY_TYPES
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
from gui.Scaleform.daapi.view.battle.shared.ribbons_aggregator import RibbonsAggregator, _SingleVehicleReceivedHitRibbon, _RibbonClassFactory, _RibbonSingleClassFactory, _BaseCaptureRibbon, _BaseDefenceRibbon, _BaseCaptureBlocked, _EnemyDetectionRibbon, _EnemiesStunRibbon, _BlockedDamageRibbon, _CriticalHitRibbon, _EnemyKillRibbon, _CriticalRibbonClassFactory, _CausedDamageRibbon, _FireHitRibbon, _RamHitRibbon, _WorldCollisionHitRibbon, _ArtilleryHitRibbon, _BombersHitRibbon, _ArtilleryFireHitRibbon, _BombersFireHitRibbon, _EpicRecoveryRibbon, _DeathZoneRibbon, _ReceivedBerserkerHitRibbon, _SpawnedBotCausedDamageRibbon, _MinefieldDamageRibbon, _ReceivedByDamagingSmokeRibbon, _ReceivedDamageHitRibbon, _ReceivedFireHitRibbon, _ReceivedRamHitRibbon, _ReceivedWorldCollisionHitRibbon, _ArtilleryReceivedDamageHitRibbon, _BombersReceivedDamageHitRibbon, _ArtilleryReceivedFireHitRibbon, _BombersReceivedFireHitRibbon, _ReceivedBySpawnedBotHitRibbon, _ReceivedByMinefieldRibbon, _AssistRibbonClassFactory, _TrackAssistRibbon, _RadioAssistRibbon, _StunAssistRibbon, _EpicEnemySectorCapturedRibbon, _EpicDestructibleDamaged, _EpicDestructibleDestroyed, _EpicDestructiblesDefended, _EpicDefenderBonus, _EpicAbilityAssist, _ACCUMULATED_RIBBON_TYPES
_logger = logging.getLogger(__name__)

class _GuidedMissileDamageHitRibbon(_SingleVehicleReceivedHitRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.DEALT_DMG_BY_CORRODING_SHOT


class _SuperBossAuraReceivedDamageHitRibbon(_SingleVehicleReceivedHitRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.RECEIVED_BY_FIRE_CIRCLE


class _SentinelAttackReceivedDamageHitRibbon(_SingleVehicleReceivedHitRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.RECEIVED_BY_THUNDER_STRIKE


class _DamageRibbonClassFactory(_RibbonClassFactory):
    __slots__ = ('__damageCls', '__fireCls', '__ramCls', '__wcCls', '__artDmgCls', '__bombDmgCls', '__artFireCls', '__bombFireCls', '__recoveryCls', '__deathZoneCls', '__berserker', '__spawnedBotDmgCls', '__damageByMinefield', '__damagedBySmoke', '__damagedByGuidedMissile', '__damagedBySuperBossAura', '__damagedBySentinelAttack')

    def __init__(self, damageCls, fireCls, ramCls, wcCls, artDmgCls, bombDmgCls, artFireCls, bombFireCls, deathZoneCls, recoveryCls, berserker, spawnedBotDmgCls, minefieldDamageCls, damagedBySmoke, damagedByGuidedMissile, damagedBySuperBossAura, damagedBySentinelAttack):
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
        self.__deathZoneCls = deathZoneCls
        self.__berserker = berserker
        self.__spawnedBotDmgCls = spawnedBotDmgCls
        self.__damageByMinefield = minefieldDamageCls
        self.__damagedBySmoke = damagedBySmoke
        self.__damagedByGuidedMissile = damagedByGuidedMissile
        self.__damagedBySuperBossAura = damagedBySuperBossAura
        self.__damagedBySentinelAttack = damagedBySentinelAttack

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
        elif damageExtra.isBombers() or damageExtra.isBomberEq():
            ribbonCls = self.__bombDmgCls
        elif damageExtra.isAttackReason(ATTACK_REASON.RECOVERY):
            ribbonCls = self.__recoveryCls
        elif damageExtra.isDeathZone():
            ribbonCls = self.__deathZoneCls
        elif damageExtra.isBerserker():
            ribbonCls = self.__berserker
        elif damageExtra.isSpawnedBotExplosion() or damageExtra.isSpawnedBotRam():
            ribbonCls = self.__spawnedBotDmgCls
        elif damageExtra.isMineField():
            ribbonCls = self.__damageByMinefield
        elif damageExtra.isDamagingSmoke():
            ribbonCls = self.__damagedBySmoke
        elif damageExtra.isGuidedMissile():
            ribbonCls = self.__damagedByGuidedMissile
        elif damageExtra.isSuperBossAura():
            ribbonCls = self.__damagedBySuperBossAura
        elif damageExtra.isSentinelAttack():
            ribbonCls = self.__damagedBySentinelAttack
        else:
            ribbonCls = self.__ramCls
        if not ribbonCls:
            ribbonCls = self.__ramCls
        return ribbonCls


class PortalRibbonsAggregator(RibbonsAggregator):
    _FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY = {FEEDBACK_EVENT_ID.PLAYER_CAPTURED_BASE: _RibbonSingleClassFactory(_BaseCaptureRibbon),
     FEEDBACK_EVENT_ID.PLAYER_DROPPED_CAPTURE: _RibbonSingleClassFactory(_BaseDefenceRibbon),
     FEEDBACK_EVENT_ID.PLAYER_BLOCKED_CAPTURE: _RibbonSingleClassFactory(_BaseCaptureBlocked),
     FEEDBACK_EVENT_ID.PLAYER_SPOTTED_ENEMY: _RibbonSingleClassFactory(_EnemyDetectionRibbon),
     FEEDBACK_EVENT_ID.PLAYER_STUN_ENEMIES: _RibbonSingleClassFactory(_EnemiesStunRibbon),
     FEEDBACK_EVENT_ID.PLAYER_USED_ARMOR: _RibbonSingleClassFactory(_BlockedDamageRibbon),
     FEEDBACK_EVENT_ID.PLAYER_DAMAGED_DEVICE_ENEMY: _RibbonSingleClassFactory(_CriticalHitRibbon),
     FEEDBACK_EVENT_ID.PLAYER_KILLED_ENEMY: _RibbonSingleClassFactory(_EnemyKillRibbon),
     FEEDBACK_EVENT_ID.ENEMY_DAMAGED_DEVICE_PLAYER: _CriticalRibbonClassFactory(),
     FEEDBACK_EVENT_ID.PLAYER_DAMAGED_HP_ENEMY: _DamageRibbonClassFactory(damageCls=_CausedDamageRibbon, fireCls=_FireHitRibbon, ramCls=_RamHitRibbon, wcCls=_WorldCollisionHitRibbon, artDmgCls=_ArtilleryHitRibbon, bombDmgCls=_BombersHitRibbon, artFireCls=_ArtilleryFireHitRibbon, bombFireCls=_BombersFireHitRibbon, recoveryCls=_EpicRecoveryRibbon, deathZoneCls=_DeathZoneRibbon, berserker=_ReceivedBerserkerHitRibbon, spawnedBotDmgCls=_SpawnedBotCausedDamageRibbon, minefieldDamageCls=_MinefieldDamageRibbon, damagedBySmoke=_ReceivedByDamagingSmokeRibbon, damagedByGuidedMissile=_GuidedMissileDamageHitRibbon, damagedBySuperBossAura=_SuperBossAuraReceivedDamageHitRibbon, damagedBySentinelAttack=_SentinelAttackReceivedDamageHitRibbon),
     FEEDBACK_EVENT_ID.ENEMY_DAMAGED_HP_PLAYER: _DamageRibbonClassFactory(damageCls=_ReceivedDamageHitRibbon, fireCls=_ReceivedFireHitRibbon, ramCls=_ReceivedRamHitRibbon, wcCls=_ReceivedWorldCollisionHitRibbon, artDmgCls=_ArtilleryReceivedDamageHitRibbon, bombDmgCls=_BombersReceivedDamageHitRibbon, artFireCls=_ArtilleryReceivedFireHitRibbon, bombFireCls=_BombersReceivedFireHitRibbon, recoveryCls=_EpicRecoveryRibbon, deathZoneCls=_DeathZoneRibbon, berserker=_ReceivedBerserkerHitRibbon, spawnedBotDmgCls=_ReceivedBySpawnedBotHitRibbon, minefieldDamageCls=_ReceivedByMinefieldRibbon, damagedBySmoke=_ReceivedByDamagingSmokeRibbon, damagedByGuidedMissile=_GuidedMissileDamageHitRibbon, damagedBySuperBossAura=_SuperBossAuraReceivedDamageHitRibbon, damagedBySentinelAttack=_SentinelAttackReceivedDamageHitRibbon),
     FEEDBACK_EVENT_ID.PLAYER_ASSIST_TO_KILL_ENEMY: _AssistRibbonClassFactory(trackAssistCls=_TrackAssistRibbon, radioAssistCls=_RadioAssistRibbon, stunAssistCls=_StunAssistRibbon),
     FEEDBACK_EVENT_ID.PLAYER_ASSIST_TO_STUN_ENEMY: _AssistRibbonClassFactory(trackAssistCls=_TrackAssistRibbon, radioAssistCls=_RadioAssistRibbon, stunAssistCls=_StunAssistRibbon),
     FEEDBACK_EVENT_ID.ENEMY_SECTOR_CAPTURED: _RibbonSingleClassFactory(_EpicEnemySectorCapturedRibbon),
     FEEDBACK_EVENT_ID.DESTRUCTIBLE_DAMAGED: _RibbonSingleClassFactory(_EpicDestructibleDamaged),
     FEEDBACK_EVENT_ID.DESTRUCTIBLE_DESTROYED: _RibbonSingleClassFactory(_EpicDestructibleDestroyed),
     FEEDBACK_EVENT_ID.DESTRUCTIBLES_DEFENDED: _RibbonSingleClassFactory(_EpicDestructiblesDefended),
     FEEDBACK_EVENT_ID.DEFENDER_BONUS: _RibbonSingleClassFactory(_EpicDefenderBonus),
     FEEDBACK_EVENT_ID.SMOKE_ASSIST: _RibbonSingleClassFactory(_EpicAbilityAssist),
     FEEDBACK_EVENT_ID.INSPIRE_ASSIST: _RibbonSingleClassFactory(_EpicAbilityAssist)}
    _FEEDBACK_EVENTS_TO_IGNORE = (FEEDBACK_EVENT_ID.EQUIPMENT_TIMER_EXPIRED,)


class PortalRibbonsAggregatorPlayer(PortalRibbonsAggregator):

    def _onPlayerFeedbackReceived(self, events):
        if BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            self.suspend()
        else:
            self.resume()
        super(PortalRibbonsAggregatorPlayer, self)._onPlayerFeedbackReceived(events)

    def _aggregateRibbons(self, ribbons):
        replayRibbons = []
        for ribbon in ribbons:
            if BattleReplay.g_replayCtrl.isTimeWarpInProgress and ribbon.getType() not in _ACCUMULATED_RIBBON_TYPES:
                continue
            replayRibbons.append(ribbon)

        super(PortalRibbonsAggregatorPlayer, self)._aggregateRibbons(replayRibbons)


def createPortalRibbonsAggregator():
    return PortalRibbonsAggregatorPlayer() if BattleReplay.g_replayCtrl.isPlaying else PortalRibbonsAggregator()
