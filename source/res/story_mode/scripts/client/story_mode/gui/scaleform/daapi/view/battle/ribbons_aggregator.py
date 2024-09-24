# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/battle/ribbons_aggregator.py
import BattleReplay
from constants import VEHICLE_BUNKER_TURRET_TAG, ATTACK_REASON
from gui.Scaleform.daapi.view.battle.shared.ribbons_aggregator import RibbonsAggregator, _ACCUMULATED_RIBBON_TYPES, _FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY as _DEFAULT_RIBBON_FACTORIES, _Ribbon, _RibbonSingleClassFactory, _RibbonClassFactory, _DamageRibbonClassFactory, _ReceivedDamageHitRibbon, _ReceivedFireHitRibbon, _ReceivedRamHitRibbon, _ReceivedWorldCollisionHitRibbon, _ArtilleryReceivedDamageHitRibbon, _BombersReceivedDamageHitRibbon, _ArtilleryReceivedFireHitRibbon, _BombersReceivedFireHitRibbon, _EpicRecoveryRibbon, _DeathZoneRibbon, _ReceivedBerserkerHitRibbon, _ReceivedBySpawnedBotHitRibbon, _ReceivedByMinefieldRibbon, _ReceivedByDamagingSmokeRibbon, _ReceivedByDamagingCorrodingShotRibbon, _ReceivedByFireCircleRibbon, _ReceivedByClingBranderRibbon, _ReceivedByDamagingThunderStrikeRibbon, _FortArtilleryReceivedDamageHitRibbon, _ReceivedByAirStrikeRibbon, _ReceivedByArtilleryRibbon, _StaticDeathZoneRibbon, _MinefieldZoneRibbon, _BattleshipRibbon, DAMAGE_SOURCE, _ReceivedFireDamageZoneRibbon
from gui.Scaleform.genConsts.BATTLE_EFFICIENCY_TYPES import BATTLE_EFFICIENCY_TYPES
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
from gui.impl import backport
from gui.impl.gen import R
_SM_FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY = {}
_SM_FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY.update(_DEFAULT_RIBBON_FACTORIES)

def _bunkerRibbonFormatter(ribbon, _, updater):
    updater(ribbonID=ribbon.getID(), ribbonType=ribbon.getType(), leftFieldStr=ribbon.getExtraValue(), vehName=backport.text(R.strings.sm_battle.bunker()), vehType=VEHICLE_BUNKER_TURRET_TAG)


class _BunkerRibbon(_Ribbon):
    __slots__ = ('_damagePoints',)

    def __init__(self, ribbonID, damagePoints):
        super(_BunkerRibbon, self).__init__(ribbonID)
        self._damagePoints = damagePoints

    @classmethod
    def createFromFeedbackEvent(cls, ribbonID, event):
        return cls(ribbonID, event.getExtra())

    def getExtraValue(self):
        return self._damagePoints

    def _canAggregate(self, ribbon):
        return True

    def _aggregate(self, ribbon):
        self._damagePoints += ribbon.getExtraValue()

    def getFormatter(self):
        return _bunkerRibbonFormatter

    @property
    def isShowActionSource(self):
        return False

    @staticmethod
    def getVehicleID():
        pass


class StoryModeReceivedArtilleryDamageRibbon(_ReceivedByArtilleryRibbon):
    __slots__ = ()

    def getDamageSource(self):
        return DAMAGE_SOURCE.HIDE


class BunkerDamagedRibbon(_BunkerRibbon):
    __slots__ = ()

    def __init__(self, ribbonID, extra):
        super(BunkerDamagedRibbon, self).__init__(ribbonID, extra.getDamage())

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.DAMAGE


class BunkerBattleshipDamagedRibbon(BunkerDamagedRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.DAMAGE_BY_BATTLESHIP


class BunkerDestroyerDamagedRibbon(BunkerDamagedRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.DAMAGE_BY_DESTROYER


class BunkerDestroyedRibbon(_BunkerRibbon):
    __slots__ = ()

    def getType(self):
        return BATTLE_EFFICIENCY_TYPES.DESTRUCTION

    def _canAggregate(self, ribbon):
        return False


class _BunkerDamagedRibbonClassFactory(_RibbonClassFactory):
    __slots__ = ('__damageCls', '__damageByBattleship', '__damageByDestroyer')

    def __init__(self, damageCls, artilleryDamageCls, damageByDestroyerCls):
        super(_BunkerDamagedRibbonClassFactory, self).__init__()
        self.__damageCls = damageCls
        self.__damageByBattleship = artilleryDamageCls
        self.__damageByDestroyer = damageByDestroyerCls

    def getRibbonClass(self, event):
        if event.getExtra().isAttackReason(ATTACK_REASON.BATTLESHIP):
            return self.__damageByBattleship
        return self.__damageByDestroyer if event.getExtra().isAttackReason(ATTACK_REASON.DESTROYER) else self.__damageCls


_SM_FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY.update({FEEDBACK_EVENT_ID.DESTRUCTIBLE_DAMAGED: _BunkerDamagedRibbonClassFactory(BunkerDamagedRibbon, BunkerBattleshipDamagedRibbon, BunkerDestroyerDamagedRibbon),
 FEEDBACK_EVENT_ID.DESTRUCTIBLE_DESTROYED: _RibbonSingleClassFactory(BunkerDestroyedRibbon),
 FEEDBACK_EVENT_ID.ENEMY_DAMAGED_HP_PLAYER: _DamageRibbonClassFactory(damageCls=_ReceivedDamageHitRibbon, fireCls=_ReceivedFireHitRibbon, ramCls=_ReceivedRamHitRibbon, wcCls=_ReceivedWorldCollisionHitRibbon, artDmgCls=_ArtilleryReceivedDamageHitRibbon, bombDmgCls=_BombersReceivedDamageHitRibbon, artFireCls=_ArtilleryReceivedFireHitRibbon, bombFireCls=_BombersReceivedFireHitRibbon, recoveryCls=_EpicRecoveryRibbon, deathZoneCls=_DeathZoneRibbon, berserker=_ReceivedBerserkerHitRibbon, spawnedBotDmgCls=_ReceivedBySpawnedBotHitRibbon, minefieldDamageCls=_ReceivedByMinefieldRibbon, damagedBySmoke=_ReceivedByDamagingSmokeRibbon, dmgByCorrodingShot=_ReceivedByDamagingCorrodingShotRibbon, dmgByFireCircle=_ReceivedByFireCircleRibbon, dmgByClingBrander=_ReceivedByClingBranderRibbon, dmgByThunderStrike=_ReceivedByDamagingThunderStrikeRibbon, damagedByFortArtillery=_FortArtilleryReceivedDamageHitRibbon, airStrikeDamageCls=_ReceivedByAirStrikeRibbon, artilleryDamageCls=StoryModeReceivedArtilleryDamageRibbon, staticDeathZoneCls=_StaticDeathZoneRibbon, minefieldZoneCls=_MinefieldZoneRibbon, damagedByBattleshipCls=_BattleshipRibbon, damagedByDestroyerCls=_BattleshipRibbon, fireDamageZoneCls=_ReceivedFireDamageZoneRibbon)})

class StoryModeRibbonsAggregator(RibbonsAggregator):
    FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY = _SM_FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY


class StoryModeRibbonsAggregatorPlayer(StoryModeRibbonsAggregator):

    def _onPlayerFeedbackReceived(self, events):
        if BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            self.suspend()
        super(StoryModeRibbonsAggregatorPlayer, self)._onPlayerFeedbackReceived(events)

    def _aggregateRibbons(self, ribbons):
        replayRibbons = []
        for ribbon in ribbons:
            if BattleReplay.g_replayCtrl.isTimeWarpInProgress and ribbon.getType() not in _ACCUMULATED_RIBBON_TYPES:
                continue
            replayRibbons.append(ribbon)

        super(StoryModeRibbonsAggregatorPlayer, self)._aggregateRibbons(replayRibbons)


def createRibbonsAggregator():
    return StoryModeRibbonsAggregatorPlayer() if BattleReplay.g_replayCtrl.isPlaying else StoryModeRibbonsAggregator()
