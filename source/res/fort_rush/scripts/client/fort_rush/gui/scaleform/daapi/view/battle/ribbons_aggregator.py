# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/scaleform/daapi/view/battle/ribbons_aggregator.py
from __future__ import absolute_import
from fort_rush.gui.fort_rush_gui_constants import FEEDBACK_EVENT_ID as FEI
from fort_rush.gui.scaleform.genConsts.FORT_RUSH_BATTLE_EFFICIENCY_TYPES import FORT_RUSH_BATTLE_EFFICIENCY_TYPES
from fort_rush_common.battle_feedback import unpackPersonalScoreFeedback
from fort_rush_common.fort_rush_constants import BATTLE_EVENT_TYPE
from gui.Scaleform.daapi.view.battle.shared.ribbons_aggregator import RibbonsAggregator, _BasePointsRibbon, _RibbonSingleClassFactory
from gui.Scaleform.daapi.view.battle.shared.ribbons_panel import _baseRibbonFormatter
from gui.battle_control.controllers.feedback_events import _BATTLE_EVENT_TO_PLAYER_FEEDBACK_EVENT, _PLAYER_FEEDBACK_EXTRA_DATA_CONVERTERS

class _FortRushBaseCaptureHealRibbon(_BasePointsRibbon):
    TYPE = FORT_RUSH_BATTLE_EFFICIENCY_TYPES.FORT_RUSH_BASE_CAPTURE_HEAL

    def getType(self):
        return self.TYPE

    def getFormatter(self):
        return _baseRibbonFormatter


class _FortRushPersonalPointsRibbon(_BasePointsRibbon):

    def __init__(self, ribbonID, actionCtx):
        points, _ = actionCtx
        super(_FortRushPersonalPointsRibbon, self).__init__(ribbonID, points)

    def getType(self):
        return FORT_RUSH_BATTLE_EFFICIENCY_TYPES.FORT_RUSH_POINTS

    def getFormatter(self):
        return _baseRibbonFormatter


class _FortRushRibbonsAggregator(RibbonsAggregator):
    pass


_BATTLE_EVENT_TO_PLAYER_FEEDBACK_EVENT.update({BATTLE_EVENT_TYPE.FORT_RUSH_PERSONAL_SCORE_UPDATE: FEI.FORT_RUSH_PERSONAL_POINTS_CHANGED})
_PLAYER_FEEDBACK_EXTRA_DATA_CONVERTERS.update({FEI.FORT_RUSH_PERSONAL_POINTS_CHANGED: unpackPersonalScoreFeedback})
_FortRushRibbonsAggregator.FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY = dict(_FortRushRibbonsAggregator.FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY)
_FortRushRibbonsAggregator.FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY[FEI.VEHICLE_HEALTH_ADDED] = _RibbonSingleClassFactory(_FortRushBaseCaptureHealRibbon)
_FortRushRibbonsAggregator.FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY[FEI.FORT_RUSH_PERSONAL_POINTS_CHANGED] = _RibbonSingleClassFactory(_FortRushPersonalPointsRibbon)

def createRibbonsAggregator():
    return _FortRushRibbonsAggregator()
