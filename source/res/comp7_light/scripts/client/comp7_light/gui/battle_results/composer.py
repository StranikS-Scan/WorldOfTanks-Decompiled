# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/battle_results/composer.py
import typing
from comp7_light.gui.battle_results.templates import comp7_light_templates
from gui.battle_results import templates
from gui.battle_results.composer import StatsComposer
from gui.battle_results.pbs_helpers.common import pushNoBattleResultsDataMessage
from gui.battle_results.stats_ctrl import BattleResults
from gui.shared.event_dispatcher import showBattleResultsWindow
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel
    from gui.battle_results.reusable import _ReusableInfo
    BattleResultsModelType = typing.TypeVar('BattleResultsModelType', bound=ViewModel)
    TooltipModelType = typing.TypeVar('TooltipModelType', bound=ViewModel)

class Comp7LightStatsComposer(StatsComposer):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, reusable):
        super(Comp7LightStatsComposer, self).__init__(reusable, comp7_light_templates.COMP7_LIGHT_COMMON_STATS_BLOCK.clone(), comp7_light_templates.COMP7_LIGHT_PERSONAL_STATS_BLOCK.clone(), comp7_light_templates.COMP7_LIGHT_TEAMS_STATS_BLOCK.clone(), templates.REGULAR_TEXT_STATS_BLOCK.clone())
        self._battleResults = None
        self._block.addNextComponent(templates.PROGRESSIVE_REWARD_VO.clone())
        self._block.addNextComponent(comp7_light_templates.EFFICIENCY_TITLE_WITH_SKILLS_VO.clone())
        return

    @staticmethod
    def _getBattlePassBlock():
        return comp7_light_templates.COMP7_LIGHT_BATTLE_PASS_PROGRESS_STATS_BLOCK

    def onResultsPosted(self, arenaUniqueID):
        if self._battleResults:
            bonusType = self._battleResults.reusable.bonusType
            showBattleResultsWindow(arenaUniqueID, bonusType)
            return
        pushNoBattleResultsDataMessage()

    @staticmethod
    def onShowResults(arenaUniqueID):
        pass

    def setResults(self, results, reusable):
        self._battleResults = BattleResults(results, reusable)

    def getResults(self):
        return self._battleResults
