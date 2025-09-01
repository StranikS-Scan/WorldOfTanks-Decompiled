# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/ribbons_aggregator.py
import BattleReplay
from gui.Scaleform.daapi.view.battle.shared.ribbons_aggregator import RibbonsAggregator, _RibbonClassFactory, _ACCUMULATED_RIBBON_TYPES, _FEEDBACK_EVENTS_TO_IGNORE as _DEFAULT_EVENTS_TO_IGNORE, _FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY as _DEFAULT_RIBBON_FACTORIES, _RIBBON_TYPES_AGGREGATED_WITH_KILL_RIBBON as _DEFAULT_RIBBONS_AGGREGATED_WITH_KILL, _SingleVehicleReceivedHitRibbon
from gui.Scaleform.daapi.view.battle.shared.ribbons_panel import _singleVehRibbonFormatter
from white_tiger.gui.white_tiger_gui_constants import FEEDBACK_EVENT_ID
from constants import ATTACK_REASON
from white_tiger_common.wt_constants import ATTACK_REASON as WT_ATTACK_REASON
from white_tiger.gui.Scaleform.genConsts.WHITE_TIGER_BATTLE_EFFICIENCY_TYPES import WHITE_TIGER_BATTLE_EFFICIENCY_TYPES
_WT_FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY = {}
_WT_FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY.update(_DEFAULT_RIBBON_FACTORIES)
_WT_FEEDBACK_EVENTS_TO_IGNORE = _DEFAULT_EVENTS_TO_IGNORE
_WT_RIBBON_TYPES_AGGREGATED_WITH_KILL_RIBBON = []
_WT_RIBBON_TYPES_AGGREGATED_WITH_KILL_RIBBON.extend(_DEFAULT_RIBBONS_AGGREGATED_WITH_KILL)
_WT_RIBBON_TYPES_COPY_TO = {}

def registerRibbonsFactory(eventID):

    def decorator(cls):
        _WT_FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY[eventID] = cls()
        return cls

    return decorator


class WTRibbonsAggregator(RibbonsAggregator):
    FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY = _WT_FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY
    FEEDBACK_EVENTS_TO_IGNORE = _WT_FEEDBACK_EVENTS_TO_IGNORE
    RIBBON_TYPES_AGGREGATED_WITH_KILL_RIBBON = _WT_RIBBON_TYPES_AGGREGATED_WITH_KILL_RIBBON
    RIBBON_TYPES_COPY_TO = _WT_RIBBON_TYPES_COPY_TO

    def _aggregateRibbons(self, ribbons):
        copyMergedRibbons = []
        for destEffType, sourceClasses in self.RIBBON_TYPES_COPY_TO.iteritems():
            sourceRibbons = [ r for r in ribbons if r is not None and r.__class__ in sourceClasses ]
            destRibbons = [ r for r in ribbons if r is not None and r.getType() == destEffType ]
            for r in destRibbons:
                for other in sourceRibbons:
                    if r.aggregate(other) and getattr(other, 'hwIsMergeCopy', False):
                        copyMergedRibbons.append(other)

        return super(WTRibbonsAggregator, self)._aggregateRibbons([ r for r in ribbons if r not in copyMergedRibbons ])


class WTRibbonsAggregatorPlayer(WTRibbonsAggregator):

    def _onPlayerFeedbackReceived(self, events):
        if BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            self.suspend()
        super(WTRibbonsAggregatorPlayer, self)._onPlayerFeedbackReceived(events)

    def _aggregateRibbons(self, ribbons):
        replayRibbons = []
        for ribbon in ribbons:
            if ribbon is None or BattleReplay.g_replayCtrl.isTimeWarpInProgress and ribbon.getType() not in _ACCUMULATED_RIBBON_TYPES:
                continue
            replayRibbons.append(ribbon)

        super(WTRibbonsAggregatorPlayer, self)._aggregateRibbons(replayRibbons)
        return


def createRibbonsAggregator():
    return WTRibbonsAggregatorPlayer() if BattleReplay.g_replayCtrl.isPlaying else WTRibbonsAggregator()


class _WTAbstractDamageRibbonsFactory(_RibbonClassFactory):
    ATTACK_REASONS = None

    def getRibbonClass(self, event):
        result = self._getWTRibbonClass(event.getExtra().getAttackReasonID(), event.getExtra().getSecondaryAttackReasonID())
        return result or self._DEFAULT_FACTORY.getRibbonClass(event)

    @classmethod
    def registerAttackReasonRibbon(cls, reason, secondaryReason=None):

        def decorator(ribbonCls):
            key = (ATTACK_REASON.getIndex(reason), ATTACK_REASON.getIndex(secondaryReason)) if secondaryReason else ATTACK_REASON.getIndex(reason)
            cls.ATTACK_REASONS[key] = ribbonCls
            return ribbonCls

        return decorator

    @classmethod
    def _getWTRibbonClass(cls, reasonID, secondaryReasonID):
        registry = cls.ATTACK_REASONS
        return registry.get((reasonID, secondaryReasonID), None) or registry.get(reasonID, None)


@registerRibbonsFactory(FEEDBACK_EVENT_ID.PLAYER_DAMAGED_HP_ENEMY)
class WTDamageRibbonsFactory(_WTAbstractDamageRibbonsFactory):
    ATTACK_REASONS = {}
    _DEFAULT_FACTORY = _DEFAULT_RIBBON_FACTORIES[FEEDBACK_EVENT_ID.PLAYER_DAMAGED_HP_ENEMY]


@registerRibbonsFactory(FEEDBACK_EVENT_ID.ENEMY_DAMAGED_HP_PLAYER)
class WTReceiveDamageRibbonsFactory(_WTAbstractDamageRibbonsFactory):
    ATTACK_REASONS = {}
    _DEFAULT_FACTORY = _DEFAULT_RIBBON_FACTORIES[FEEDBACK_EVENT_ID.ENEMY_DAMAGED_HP_PLAYER]


@WTDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.ULTIMATE)
class _CausedByHyperion(_SingleVehicleReceivedHitRibbon):
    __slots__ = ()

    def getType(self):
        return WHITE_TIGER_BATTLE_EFFICIENCY_TYPES.HYPERION

    def getFormatter(self):
        return _singleVehRibbonFormatter


@WTReceiveDamageRibbonsFactory.registerAttackReasonRibbon(ATTACK_REASON.ULTIMATE)
class _ReceivedByHyperion(_SingleVehicleReceivedHitRibbon):
    __slots__ = ()
    TYPE = WHITE_TIGER_BATTLE_EFFICIENCY_TYPES.HYPERION

    def getType(self):
        return self.TYPE

    def getFormatter(self):
        return _singleVehRibbonFormatter


@WTDamageRibbonsFactory.registerAttackReasonRibbon(WT_ATTACK_REASON.WHITE_TIGER_CIRCUIT_OVERLOAD)
class _CausedByCircuitOverload(_SingleVehicleReceivedHitRibbon):
    __slots__ = ()

    def getType(self):
        return WHITE_TIGER_BATTLE_EFFICIENCY_TYPES.CIRCUIT_OVERLOAD

    def getFormatter(self):
        return _singleVehRibbonFormatter


@WTReceiveDamageRibbonsFactory.registerAttackReasonRibbon(WT_ATTACK_REASON.WHITE_TIGER_CIRCUIT_OVERLOAD)
class _ReceivedByCircuitOverload(_SingleVehicleReceivedHitRibbon):
    __slots__ = ()
    TYPE = WHITE_TIGER_BATTLE_EFFICIENCY_TYPES.CIRCUIT_OVERLOAD

    def getType(self):
        return self.TYPE

    def getFormatter(self):
        return _singleVehRibbonFormatter
