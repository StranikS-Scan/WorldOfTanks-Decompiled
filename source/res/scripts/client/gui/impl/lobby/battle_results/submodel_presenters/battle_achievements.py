# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_results/submodel_presenters/battle_achievements.py
import typing
import json
from frameworks.wulf import Array
from frameworks.wulf.view.array import fillViewModelsArray
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.battle_results.pbs_helpers.common import getPersonalAchievements
from gui.impl.backport.backport_tooltip import createBackportTooltipContent
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_results.postbattle_achievement_model import PostbattleAchievementModel
from gui.battle_results.presenters.battle_results_sub_presenter import BattleResultsSubPresenter
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel
    from gui.battle_results.stats_ctrl import BattleResults
    from gui.battle_results.pbs_helpers.common import _AchievementData
AchievementTooltipType = (TOOLTIPS_CONSTANTS.BATTLE_STATS_MARKS_ON_GUN_ACHIEVEMENT, TOOLTIPS_CONSTANTS.MARK_OF_MASTERY, TOOLTIPS_CONSTANTS.BATTLE_STATS_ACHIEVS)

class BattleAchievementsSubPresenter(BattleResultsSubPresenter):

    @classmethod
    def getViewModelType(cls):
        return Array[PostbattleAchievementModel]

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId in AchievementTooltipType:
                tooltipArgs = json.loads(event.getArgument('tooltipArgs'))
                return createBackportTooltipContent(specialAlias=tooltipId, specialArgs=tooltipArgs)
        return super(BattleAchievementsSubPresenter, self).createToolTipContent(event, contentID)

    def packBattleResults(self, battleResults):
        viewModel = self.getViewModel()
        viewModel.clear()
        achievements = getPersonalAchievements(battleResults)
        viewModels = [ self.__setAchievementsResults(achievement) for achievement in achievements ]
        fillViewModelsArray(viewModels, viewModel)
        viewModel.invalidate()

    def __setAchievementsResults(self, achievement):
        achievementModel = PostbattleAchievementModel()
        achievementModel.setName(achievement.name)
        achievementModel.setIsEpic(achievement.isEpic)
        achievementModel.setIconName(achievement.iconName)
        achievementModel.setGroupID(achievement.groupID)
        achievementModel.setTooltipId(achievement.tooltipType)
        achievementModel.setTooltipArgs(achievement.tooltipArgs)
        return achievementModel
