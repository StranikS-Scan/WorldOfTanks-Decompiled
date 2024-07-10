# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenters/packers/battle_info.py
from gui.battle_results.pbs_helpers.common import getArenaNameStr, getRegularFinishResultResource
from gui.battle_results.presenters.packers.interfaces import IBattleResultsPacker
from gui.battle_results.settings import BATTLE_RESULTS_RECORD as _RECORD
from gui.impl.gen.view_models.views.lobby.battle_results.battle_info_model import WinStatus

class BattleInfo(IBattleResultsPacker):
    __slots__ = ()

    @classmethod
    def packModel(cls, model, battleResults):
        reusable, results = battleResults.reusable, battleResults.results
        model.setArenaName(getArenaNameStr(reusable))
        common = results[_RECORD.COMMON]
        model.setBattleStartTime(common['arenaCreateTime'])
        model.setBattleDuration(common['duration'])
        teamResult = reusable.getPersonalTeamResult()
        model.setWinStatus(WinStatus(teamResult))
        model.setFinishReason(getRegularFinishResultResource(reusable.common.finishReason, teamResult))
