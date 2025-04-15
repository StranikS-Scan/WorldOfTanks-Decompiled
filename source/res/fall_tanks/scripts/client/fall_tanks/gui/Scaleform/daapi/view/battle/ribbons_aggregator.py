# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/Scaleform/daapi/view/battle/ribbons_aggregator.py
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
from gui.Scaleform.daapi.view.battle.shared.ribbons_aggregator import RibbonsAggregator, _RibbonSingleClassFactory, _EnemyKillRibbon
from gui.Scaleform.daapi.view.battle.shared.ribbons_panel import _killRibbonFormatter
from fall_tanks.gui.Scaleform.genConsts.FALL_TANKS_BATTLE_EFFICIENCY_TYPES import FALL_TANKS_BATTLE_EFFICIENCY_TYPES
_SUPPORTED_RIBBONS = {FALL_TANKS_BATTLE_EFFICIENCY_TYPES.FALL_TANKS_DESTRUCTION}

class _FallTanksEnemyKillRibbon(_EnemyKillRibbon):

    def getFormatter(self):
        return _killRibbonFormatter

    def getType(self):
        return FALL_TANKS_BATTLE_EFFICIENCY_TYPES.FALL_TANKS_DESTRUCTION

    def getExtraValue(self):
        pass


class FallTanksRibbonsAggregator(RibbonsAggregator):
    FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY = {FEEDBACK_EVENT_ID.PLAYER_KILLED_ENEMY: _RibbonSingleClassFactory(_FallTanksEnemyKillRibbon)}
    KILL_RIBBON_BATTLE_EFFICIENCY_TYPE = FALL_TANKS_BATTLE_EFFICIENCY_TYPES.FALL_TANKS_DESTRUCTION

    def _aggregateRibbons(self, ribbons):
        ribbons = [ ribbon for ribbon in ribbons if ribbon is not None and ribbon.getType() in _SUPPORTED_RIBBONS ]
        super(FallTanksRibbonsAggregator, self)._aggregateRibbons(ribbons)
        return

    def _onPlayerFeedbackReceived(self, events):
        events = [ e for e in events if e.getType() == FEEDBACK_EVENT_ID.PLAYER_KILLED_ENEMY ]
        super(FallTanksRibbonsAggregator, self)._onPlayerFeedbackReceived(events)


def createRibbonsAggregator():
    return FallTanksRibbonsAggregator()
