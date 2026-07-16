# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/battle_results/submodel_presenters/battle_info.py
from __future__ import absolute_import
import typing
from comp7_light.gui.impl.gen.view_models.views.lobby.battle_results.comp7_light_battle_info_model import Comp7LightBattleInfoModel
from comp7_core.gui.battle_results.components.comp7_core_components import checkIfDeserter
from fairplay_violation_types import FairplayViolations
from gui.impl.lobby.battle_results.submodel_presenters.battle_info import BattleInfoSubPresenter
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel
    from gui.battle_results.stats_ctrl import BattleResults

class Comp7LightBattleInfoSubPresenter(BattleInfoSubPresenter):

    @classmethod
    def getViewModelType(cls):
        return Comp7LightBattleInfoModel

    def packBattleResults(self, battleResults):
        super(Comp7LightBattleInfoSubPresenter, self).packBattleResults(battleResults)
        reusable = battleResults.reusable
        winStatus = reusable.getPersonalTeamResult()
        with self.getViewModel().transaction() as model:
            model.setWinStatus(winStatus)
            model.setIsLeave(checkIfDeserter(reusable, FairplayViolations.COMP7_LIGHT_DESERTER))
