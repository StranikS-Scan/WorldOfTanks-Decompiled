# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/battle_results/submodel_presenters/battle_info.py
from __future__ import absolute_import
import typing
from comp7.gui.impl.gen.view_models.views.lobby.battle_results.comp7_battle_info_model import Comp7BattleInfoModel
from comp7_core_constants import FINISH_REASON
from fairplay_violation_types import FairplayViolations
from gui.impl.gen import R
from gui.impl.lobby.battle_results.submodel_presenters.battle_info import BattleInfoSubPresenter
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel
    from gui.battle_results.stats_ctrl import BattleResults

def isDeserter(reusable):
    if not reusable.personal.avatar.hasPenalties():
        return False
    penaltyName, _ = reusable.personal.avatar.getPenaltyDetails()
    return penaltyName == FairplayViolations.COMP7_DESERTER


class Comp7BattleInfoSubPresenter(BattleInfoSubPresenter):

    @classmethod
    def getViewModelType(cls):
        return Comp7BattleInfoModel

    def packBattleResults(self, battleResults):
        super(Comp7BattleInfoSubPresenter, self).packBattleResults(battleResults)
        reusable = battleResults.reusable
        reason = battleResults.reusable.common.finishReason
        hasComplexKey = reason in FINISH_REASON.DRAW_RESOLVED_REASONS or reason == FINISH_REASON.EXTERMINATION
        winStatus = reusable.getPersonalTeamResult()
        reasonKey = 'c_{}{}'.format(reason, winStatus if hasComplexKey else '')
        finishReason = R.strings.battle_results.finish.reason.dyn(reasonKey)()
        with self.getViewModel().transaction() as model:
            model.setWinStatus(winStatus)
            model.setIsLeave(isDeserter(reusable))
            model.setFinishReason(finishReason)
