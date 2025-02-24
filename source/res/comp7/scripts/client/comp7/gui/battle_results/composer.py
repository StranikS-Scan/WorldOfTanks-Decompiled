# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/battle_results/composer.py
import typing
from comp7.gui.battle_results.templates import comp7_templates
from gui.battle_results import templates
from gui.battle_results.composer import StatsComposer
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel
    BattleResultsModelType = typing.TypeVar('BattleResultsModelType', bound=ViewModel)
    TooltipModelType = typing.TypeVar('TooltipModelType', bound=ViewModel)

class Comp7StatsComposer(StatsComposer):

    def __init__(self, reusable):
        super(Comp7StatsComposer, self).__init__(reusable, comp7_templates.COMP7_COMMON_STATS_BLOCK.clone(), comp7_templates.COMP7_PERSONAL_STATS_BLOCK.clone(), comp7_templates.COMP7_TEAMS_STATS_BLOCK.clone(), templates.REGULAR_TEXT_STATS_BLOCK.clone())
        self._block.addNextComponent(templates.PROGRESSIVE_REWARD_VO.clone())
        self._block.addNextComponent(comp7_templates.EFFICIENCY_TITLE_WITH_SKILLS_VO.clone())

    @staticmethod
    def _getBattlePassBlock():
        return comp7_templates.COMP7_BATTLE_PASS_PROGRESS_STATS_BLOCK


class TournamentComp7StatsComposer(StatsComposer):

    def __init__(self, reusable):
        super(TournamentComp7StatsComposer, self).__init__(reusable, comp7_templates.TOURNAMENT_COMP7_COMMON_STATS_BLOCK.clone(), comp7_templates.TOURNAMENT_COMP7_PERSONAL_STATS_BLOCK.clone(), comp7_templates.COMP7_TEAMS_STATS_BLOCK.clone(), templates.REGULAR_TEXT_STATS_BLOCK.clone())
        self._block.addNextComponent(templates.PROGRESSIVE_REWARD_VO.clone())
        self._block.addNextComponent(comp7_templates.EFFICIENCY_TITLE_WITH_SKILLS_VO.clone())

    @staticmethod
    def _getBattlePassBlock():
        return comp7_templates.COMP7_BATTLE_PASS_PROGRESS_STATS_BLOCK


class TrainingComp7StatsComposer(StatsComposer):

    def __init__(self, reusable):
        super(TrainingComp7StatsComposer, self).__init__(reusable, comp7_templates.TRAINING_COMP7_COMMON_STATS_BLOCK.clone(), comp7_templates.TRAINING_COMP7_PERSONAL_STATS_BLOCK.clone(), comp7_templates.COMP7_TEAMS_STATS_BLOCK.clone(), templates.REGULAR_TEXT_STATS_BLOCK.clone())
        self._block.addNextComponent(templates.PROGRESSIVE_REWARD_VO.clone())
        self._block.addNextComponent(comp7_templates.EFFICIENCY_TITLE_WITH_SKILLS_VO.clone())

    @staticmethod
    def _getBattlePassBlock():
        return comp7_templates.COMP7_BATTLE_PASS_PROGRESS_STATS_BLOCK
