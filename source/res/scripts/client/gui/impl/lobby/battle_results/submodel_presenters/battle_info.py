# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_results/submodel_presenters/battle_info.py
import typing
from gui.battle_results.pbs_helpers.common import getArenaNameStr, getRegularFinishResultResource
from gui.battle_results.presenters.battle_results_sub_presenter import BattleResultsSubPresenter
from gui.battle_results.settings import BATTLE_RESULTS_RECORD as _RECORD
from gui.impl.gen.view_models.views.lobby.battle_results.random.random_battle_info_model import RandomBattleInfoModel
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel
    from gui.battle_results.stats_ctrl import BattleResults

class BattleInfoSubPresenter(BattleResultsSubPresenter):

    @classmethod
    def getViewModelType(cls):
        return RandomBattleInfoModel

    def packBattleResults(self, battleResults):
        reusable, results = battleResults.reusable, battleResults.results
        common = results[_RECORD.COMMON]
        personal = results[_RECORD.PERSONAL]
        teamResult = reusable.getPersonalTeamResult()
        with self.getViewModel().transaction() as model:
            model.setArenaName(getArenaNameStr(reusable))
            model.setArenaGuiType(reusable.common.arenaGuiType)
            model.setBattleStartTime(common['arenaCreateTime'])
            model.setBattleDuration(common['duration'])
            model.setFinishReason(getRegularFinishResultResource(reusable.common.finishReason, teamResult))
            model.setFinishReasonKey(reusable.common.finishReason)
            model.setWinStatus(teamResult)
            model.setModeName(reusable.common.arenaType.getGamePlayName())
            model.setFinishReasonClarification('finishAllPlayersLeft' if reusable.common.finishAllPlayersLeft else '')
            model.setCommendationsReceived(personal[_RECORD.PERSONAL_AVATAR]['commendationsReceived'])
