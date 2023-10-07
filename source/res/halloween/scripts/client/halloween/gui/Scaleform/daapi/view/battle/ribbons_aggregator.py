# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/battle/ribbons_aggregator.py
import BattleReplay
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
from gui.Scaleform.genConsts.BATTLE_EFFICIENCY_TYPES import BATTLE_EFFICIENCY_TYPES
from gui.Scaleform.daapi.view.battle.shared.ribbons_aggregator import RibbonsAggregatorPlayer, RibbonsAggregator, _FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY, _RibbonSingleClassFactory, _Ribbon
from gui.battle_control.controllers.feedback_events import _BATTLE_EVENT_TO_PLAYER_FEEDBACK_EVENT, _PLAYER_FEEDBACK_EXTRA_DATA_CONVERTERS
from BattleFeedbackCommon import BATTLE_EVENT_TYPE
from halloween_common.hw_battle_feedback import HWGameplayActionID, unpackGameplayActionFeedback
_GAMEPLAY_ACTION_TO_BATTLE_EFFICIENCY = {HWGameplayActionID.VEHICLE_REPAIR: BATTLE_EFFICIENCY_TYPES.HALLOWEEN_REPAIR,
 HWGameplayActionID.VEHICLE_HEALTH_RESTORE: BATTLE_EFFICIENCY_TYPES.HALLOWEEN_HEALTH_RESTORE}

class _RibbonGameplayAction(_Ribbon):
    __slots__ = ('_actionValue', '_actionID', '_vehicleID', '_effType')

    def __init__(self, ribbonID, actionCtx):
        super(_RibbonGameplayAction, self).__init__(ribbonID)
        self._vehicleID, self._actionValue, self._actionID = actionCtx
        self._effType = _GAMEPLAY_ACTION_TO_BATTLE_EFFICIENCY[self.actionID]

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
    def efficiencyType(self):
        return self._effType

    def getType(self):
        return self.efficiencyType

    def _canAggregate(self, ribbon):
        return isinstance(ribbon, self.__class__) and ribbon.actionID == self.actionID

    def _aggregate(self, ribbon):
        self._actionValue += ribbon.actionValue


_BATTLE_EVENT_TO_PLAYER_FEEDBACK_EVENT.update({BATTLE_EVENT_TYPE.HW_GAMEPLAY_ACTION: FEEDBACK_EVENT_ID.HW_GAMEPLAY_ACTION})
_PLAYER_FEEDBACK_EXTRA_DATA_CONVERTERS.update({FEEDBACK_EVENT_ID.HW_GAMEPLAY_ACTION: unpackGameplayActionFeedback})
_FEEDBACK_EVENT_TO_RIBBON_CLS_FACTORY.update({FEEDBACK_EVENT_ID.HW_GAMEPLAY_ACTION: _RibbonSingleClassFactory(_RibbonGameplayAction)})

class HalloweenRibbonsAggregatorPlayer(RibbonsAggregatorPlayer):

    def _onPlayerFeedbackReceived(self, events):
        if BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            self.suspend()
        super(HalloweenRibbonsAggregatorPlayer.__base__, self)._onPlayerFeedbackReceived(events)


def createRibbonsAggregator():
    return HalloweenRibbonsAggregatorPlayer() if BattleReplay.g_replayCtrl.isPlaying else RibbonsAggregator()
