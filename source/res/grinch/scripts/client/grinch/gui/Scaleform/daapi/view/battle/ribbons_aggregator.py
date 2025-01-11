# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/Scaleform/daapi/view/battle/ribbons_aggregator.py
import BattleReplay
from gui.Scaleform.daapi.view.battle.shared.ribbons_aggregator import RibbonsAggregator, _ACCUMULATED_RIBBON_TYPES, _FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY as _DEFAULT_RIBBON_FACTORIES, _RIBBON_TYPES_AGGREGATED_WITH_KILL_RIBBON as _DEFAULT_RIBBONS_AGGREGATED_WITH_KILL, _SingleVehicleDamageRibbon, _RibbonClassFactory, _RibbonSingleClassFactory, _BasePointsRibbon, DAMAGE_SOURCE
from grinch_common.grinch_constants import ATTACK_REASON
from grinch.gui.Scaleform.genConsts.GRINCH_BATTLE_EFFICIENCY_TYPES import GRINCH_BATTLE_EFFICIENCY_TYPES
from gui.Scaleform.daapi.view.battle.shared.ribbons_panel import _singleVehRibbonFormatter, _getVehicleData, _formatCounter, _baseRibbonFormatter
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
from gui.impl import backport

class _PresentsDeliveryRibbon(_BasePointsRibbon):
    __slots__ = ()

    def getType(self):
        return GRINCH_BATTLE_EFFICIENCY_TYPES.PRESENTS_DELIVERY

    def getFormatter(self):
        return _baseRibbonFormatter


_GRINCH_FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY = {}
_GRINCH_FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY.update(_DEFAULT_RIBBON_FACTORIES)
_GRINCH_FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY.update({FEEDBACK_EVENT_ID.PLAYER_DROPPED_CAPTURE: _RibbonSingleClassFactory(_PresentsDeliveryRibbon)})
_GRINCH_RIBBON_TYPES_AGGREGATED_WITH_KILL_RIBBON = [GRINCH_BATTLE_EFFICIENCY_TYPES.TURRET_DEALT_DAMAGE]
_GRINCH_RIBBON_TYPES_AGGREGATED_WITH_KILL_RIBBON.extend(_DEFAULT_RIBBONS_AGGREGATED_WITH_KILL)

def registerRibbonsFactory(eventID):

    def decorator(cls):
        _GRINCH_FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY[eventID] = cls()
        return cls

    return decorator


def _destroyedTurretsRibbonFormatter(ribbon, arenaDP, updater):
    vehicleName, vehicleClassTag = _getVehicleData(arenaDP, ribbon.getVehicleID())
    updater(ribbonID=ribbon.getID(), ribbonType=ribbon.getType(), vehName=vehicleName, vehType=vehicleClassTag, leftFieldStr=_formatCounter(ribbon.getExtraValue()))


def _singleVehFormatterWithNoDmgSource(ribbon, arenaDP, updater):
    updater(ribbonID=ribbon.getID(), ribbonType=ribbon.getType(), vehName='', vehType=DAMAGE_SOURCE.HIDE, leftFieldStr=backport.getIntegralFormat(ribbon.getExtraValue()))


class _AbstractGrinchRibbonsFactory(_RibbonClassFactory):
    ATTACK_REASONS = None

    def getRibbonClass(self, event):
        result = self._getRibbonClass(event.getExtra().getAttackReasonID(), event.getExtra().getSecondaryAttackReasonID())
        return result or self._DEFAULT_FACTORY.getRibbonClass(event)

    @classmethod
    def registerAttackReasonRibbon(cls, reason, secondaryReason=None):

        def decorator(ribbonCls):
            key = (ATTACK_REASON.getIndex(reason), ATTACK_REASON.getIndex(secondaryReason)) if secondaryReason else ATTACK_REASON.getIndex(reason)
            cls.ATTACK_REASONS[key] = ribbonCls
            return ribbonCls

        return decorator

    @classmethod
    def _getRibbonClass(cls, reasonID, secondaryReasonID):
        registry = cls.ATTACK_REASONS
        return registry.get((reasonID, secondaryReasonID), None) or registry.get(reasonID, None)


@registerRibbonsFactory(FEEDBACK_EVENT_ID.PLAYER_DAMAGED_HP_ENEMY)
class GrinchDamageRibbonsFactory(_AbstractGrinchRibbonsFactory):
    ATTACK_REASONS = {}
    _DEFAULT_FACTORY = _DEFAULT_RIBBON_FACTORIES[FEEDBACK_EVENT_ID.PLAYER_DAMAGED_HP_ENEMY]


@registerRibbonsFactory(FEEDBACK_EVENT_ID.ENEMY_DAMAGED_HP_PLAYER)
class GrinchReceivedDamageRibbonsFactory(_AbstractGrinchRibbonsFactory):
    ATTACK_REASONS = {}
    _DEFAULT_FACTORY = _DEFAULT_RIBBON_FACTORIES[FEEDBACK_EVENT_ID.ENEMY_DAMAGED_HP_PLAYER]


@GrinchDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.REDIRECTED_DAMAGE)
class _TurretDamageRibbon(_SingleVehicleDamageRibbon):
    __slots__ = ()

    def getType(self):
        return GRINCH_BATTLE_EFFICIENCY_TYPES.TURRET_DEALT_DAMAGE

    def getFormatter(self):
        return _singleVehRibbonFormatter


@GrinchReceivedDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.SLAVE_BOT_DAMAGED)
class _TurretDestroyedRibbon(_SingleVehicleDamageRibbon):
    __slots__ = ()

    def getType(self):
        return GRINCH_BATTLE_EFFICIENCY_TYPES.TURRET_DESTROYED

    def getFormatter(self):
        return _destroyedTurretsRibbonFormatter


@GrinchDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.BLIZZARD_ABILITY)
class _BlizzardDamageRibbon(_SingleVehicleDamageRibbon):
    __slots__ = ()

    def getType(self):
        return GRINCH_BATTLE_EFFICIENCY_TYPES.BLIZZARD_CAUSED_DAMAGE

    def getFormatter(self):
        return _singleVehRibbonFormatter


@GrinchReceivedDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.RAGE)
class _RageReceivedDamageRibbon(_SingleVehicleDamageRibbon):
    __slots__ = ()

    def getType(self):
        return GRINCH_BATTLE_EFFICIENCY_TYPES.RAGE

    def getFormatter(self):
        return _singleVehFormatterWithNoDmgSource


@GrinchReceivedDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.BLIZZARD_ABILITY)
class _BlizzardReceivedDamageRibbon(_SingleVehicleDamageRibbon):
    __slots__ = ()

    def getType(self):
        return GRINCH_BATTLE_EFFICIENCY_TYPES.DAMAGED_BY_BLIZZARD

    def getFormatter(self):
        return _singleVehRibbonFormatter


@GrinchReceivedDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.SNOWSTORM)
class _SnowstormDamageRibbon(_SingleVehicleDamageRibbon):
    __slots__ = ()

    def getType(self):
        return GRINCH_BATTLE_EFFICIENCY_TYPES.DAMAGED_BY_SNOWSTORM

    def getFormatter(self):
        return _singleVehRibbonFormatter


@GrinchDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.BASE_DEFENDER_BONUS)
class _BaseDefenderBonusRibbon(_SingleVehicleDamageRibbon):
    __slots__ = ()

    def getType(self):
        return GRINCH_BATTLE_EFFICIENCY_TYPES.BASE_DEFENDER_BONUS

    def getFormatter(self):
        return _singleVehRibbonFormatter


@GrinchDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.ABILITY_ASSIST_FLARE)
class _AbilityAssistFlareRibbon(_SingleVehicleDamageRibbon):
    __slots__ = ()

    def getType(self):
        return GRINCH_BATTLE_EFFICIENCY_TYPES.ABILITY_ASSIST_FLARE

    def getFormatter(self):
        return _singleVehRibbonFormatter


@GrinchDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.ABILITY_ASSIST_BLIZZARD)
class _AbilityAssistBlizzardRibbon(_SingleVehicleDamageRibbon):
    __slots__ = ()

    def getType(self):
        return GRINCH_BATTLE_EFFICIENCY_TYPES.ABILITY_ASSIST_BLIZZARD

    def getFormatter(self):
        return _singleVehRibbonFormatter


@GrinchDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.ABILITY_ASSIST_BUFF)
class _AbilityAssistBuffRibbon(_SingleVehicleDamageRibbon):
    __slots__ = ()

    def getType(self):
        return GRINCH_BATTLE_EFFICIENCY_TYPES.ABILITY_ASSIST_BUFF

    def getFormatter(self):
        return _singleVehRibbonFormatter


class GrinchRibbonsAggregator(RibbonsAggregator):
    FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY = _GRINCH_FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY
    RIBBON_TYPES_AGGREGATED_WITH_KILL_RIBBON = _GRINCH_RIBBON_TYPES_AGGREGATED_WITH_KILL_RIBBON


class GrinchRibbonsAggregatorPlayer(GrinchRibbonsAggregator):

    def _onPlayerFeedbackReceived(self, events):
        if BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            self.suspend()
        super(GrinchRibbonsAggregatorPlayer, self)._onPlayerFeedbackReceived(events)

    def _aggregateRibbons(self, ribbons):
        replayRibbons = []
        for ribbon in ribbons:
            if BattleReplay.g_replayCtrl.isTimeWarpInProgress and ribbon.getType() not in _ACCUMULATED_RIBBON_TYPES:
                continue
            replayRibbons.append(ribbon)

        super(GrinchRibbonsAggregatorPlayer, self)._aggregateRibbons(replayRibbons)


def createRibbonsAggregator():
    return GrinchRibbonsAggregatorPlayer() if BattleReplay.g_replayCtrl.isPlaying else GrinchRibbonsAggregator()
