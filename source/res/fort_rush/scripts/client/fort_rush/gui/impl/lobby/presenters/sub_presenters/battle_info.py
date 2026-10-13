# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/lobby/presenters/sub_presenters/battle_info.py
from __future__ import absolute_import
import typing
from fort_rush.gui.battle_results.pbs_helpers import makeFortRushFinishResultLabel
from fort_rush.gui.impl.gen.view_models.views.lobby.post_battle_results_view.battle_info_model import BattleInfoModel
from gui.battle_results.pbs_helpers.common import getArenaNameStr
from gui.battle_results.presenters.battle_results_sub_presenter import BattleResultsSubPresenter
from gui.battle_results.settings import BATTLE_RESULTS_RECORD as _RECORD
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel
    from gui.battle_results.stats_ctrl import BattleResults

class FortRushBattleInfoSubPresenter(BattleResultsSubPresenter):

    @classmethod
    def getViewModelType(cls):
        return BattleInfoModel

    def packBattleResults(self, battleResults):
        reusable, results = battleResults.reusable, battleResults.results
        common = results[_RECORD.COMMON]
        teamResult = reusable.getPersonalTeamResult()
        with self.getViewModel().transaction() as model:
            model.setArenaName(getArenaNameStr(reusable))
            model.setBattleStartTime(common['arenaCreateTime'])
            model.setBattleDuration(common['duration'])
            model.setFinishReason(makeFortRushFinishResultLabel(reusable.common.finishReason, teamResult))
            model.setWinStatus(teamResult)
            model.setFinishReasonClarification('finishAllPlayersLeft' if reusable.common.finishAllPlayersLeft else '')
