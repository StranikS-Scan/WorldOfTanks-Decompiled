# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/presenters/sub_presenters/battle_achievements.py
import typing
import json
from frameworks.wulf import Array
from frameworks.wulf.view.array import fillViewModelsArray
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.battle_results.pbs_helpers.common import getPersonalAchievements
from gui.impl.backport.backport_tooltip import createBackportTooltipContent
from gui.impl.gen import R
from gui.battle_results.presenters.battle_results_sub_presenter import BattleResultsSubPresenter
from frontline.gui.impl.gen.view_models.views.lobby.views.post_battle_results_view.achievement_model import AchievementModel
from frontline.gui.frontline_presenters_packers import getAchievementResultsModel, getRankAchievementResultsModel
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel
    from gui.battle_results.stats_ctrl import BattleResults
AchievementTooltipType = (TOOLTIPS_CONSTANTS.BATTLE_STATS_MARKS_ON_GUN_ACHIEVEMENT,
 TOOLTIPS_CONSTANTS.MARK_OF_MASTERY,
 TOOLTIPS_CONSTANTS.BATTLE_STATS_ACHIEVS,
 TOOLTIPS_CONSTANTS.FRONTLINE_RANK)

class FrontlineBattleAchievementsSubPresenter(BattleResultsSubPresenter):

    @classmethod
    def getViewModelType(cls):
        return Array[AchievementModel]

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId in AchievementTooltipType:
                tooltipArgs = json.loads(event.getArgument('tooltipArgs'))
                return createBackportTooltipContent(specialAlias=tooltipId, specialArgs=tooltipArgs)
        return super(FrontlineBattleAchievementsSubPresenter, self).createToolTipContent(event, contentID)

    def packBattleResults(self, battleResults):
        viewModel = self.getViewModel()
        viewModel.clear()
        achievements = getPersonalAchievements(battleResults)
        viewModels = [ getAchievementResultsModel(achievement) for achievement in achievements ]
        if battleResults.reusable.personal.avatar is not None:
            playerRank = battleResults.reusable.personal.avatar.extensionInfo.get('playerRank', 0)
            viewModels.insert(0, getRankAchievementResultsModel(playerRank))
        fillViewModelsArray(viewModels, viewModel)
        viewModel.invalidate()
        return
