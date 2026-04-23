# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/battle_results/composer.py
import typing
from comp7.gui.battle_results.templates import comp7_templates
from comp7.gui.impl.lobby.battle_results.submodel_presenters.battle_info import isDeserter
from constants import ARENA_BONUS_TYPE
from gui.battle_control.battle_constants import WinStatus
from gui.battle_results import templates
from gui.battle_results.composer import StatsComposer
from gui.battle_results.pbs_helpers.common import pushNoBattleResultsDataMessage
from gui.battle_results.settings import PLAYER_TEAM_RESULT
from gui.battle_results.stats_ctrl import BattleResults
from gui.shared.event_dispatcher import showBattleResultsWindow
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel
    BattleResultsModelType = typing.TypeVar('BattleResultsModelType', bound=ViewModel)
    TooltipModelType = typing.TypeVar('TooltipModelType', bound=ViewModel)

class Comp7StatsComposer(StatsComposer):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, reusable):
        super(Comp7StatsComposer, self).__init__(reusable, comp7_templates.COMP7_COMMON_STATS_BLOCK.clone(), comp7_templates.COMP7_PERSONAL_STATS_BLOCK.clone(), comp7_templates.COMP7_TEAMS_STATS_BLOCK.clone(), templates.REGULAR_TEXT_STATS_BLOCK.clone())
        self._battleResults = None
        self._block.addNextComponent(templates.PROGRESSIVE_REWARD_VO.clone())
        self._block.addNextComponent(comp7_templates.EFFICIENCY_TITLE_WITH_SKILLS_VO.clone())
        return

    @staticmethod
    def _getBattlePassBlock():
        return comp7_templates.COMP7_BATTLE_PASS_PROGRESS_STATS_BLOCK

    def onResultsPosted(self, arenaUniqueID):
        if self._battleResults:
            _setBattleWinStatus(self._battleResults.reusable)
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


class TournamentComp7StatsComposer(StatsComposer):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, reusable):
        super(TournamentComp7StatsComposer, self).__init__(reusable, comp7_templates.TOURNAMENT_COMP7_COMMON_STATS_BLOCK.clone(), comp7_templates.TOURNAMENT_COMP7_PERSONAL_STATS_BLOCK.clone(), comp7_templates.COMP7_TEAMS_STATS_BLOCK.clone(), templates.REGULAR_TEXT_STATS_BLOCK.clone())
        self._block.addNextComponent(templates.PROGRESSIVE_REWARD_VO.clone())
        self._block.addNextComponent(comp7_templates.EFFICIENCY_TITLE_WITH_SKILLS_VO.clone())

    @staticmethod
    def _getBattlePassBlock():
        return comp7_templates.COMP7_BATTLE_PASS_PROGRESS_STATS_BLOCK

    def onResultsPosted(self, arenaUniqueID):
        if self._battleResults:
            _setBattleWinStatus(self._battleResults.reusable)
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

    @classmethod
    def representativeArenaBonusType(cls):
        return ARENA_BONUS_TYPE.COMP7


class TrainingComp7StatsComposer(StatsComposer):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, reusable):
        super(TrainingComp7StatsComposer, self).__init__(reusable, comp7_templates.TRAINING_COMP7_COMMON_STATS_BLOCK.clone(), comp7_templates.TRAINING_COMP7_PERSONAL_STATS_BLOCK.clone(), comp7_templates.COMP7_TEAMS_STATS_BLOCK.clone(), templates.REGULAR_TEXT_STATS_BLOCK.clone())
        self._block.addNextComponent(templates.PROGRESSIVE_REWARD_VO.clone())
        self._block.addNextComponent(comp7_templates.EFFICIENCY_TITLE_WITH_SKILLS_VO.clone())

    @staticmethod
    def _getBattlePassBlock():
        return comp7_templates.COMP7_BATTLE_PASS_PROGRESS_STATS_BLOCK

    def onResultsPosted(self, arenaUniqueID):
        if self._battleResults:
            _setBattleWinStatus(self._battleResults.reusable)
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

    @classmethod
    def representativeArenaBonusType(cls):
        return ARENA_BONUS_TYPE.COMP7


@dependency.replace_none_kwargs(sessionProvider=IBattleSessionProvider)
def _setBattleWinStatus(reusable, sessionProvider=None):
    if reusable.getPersonalTeamResult() == PLAYER_TEAM_RESULT.WIN and not isDeserter(reusable):
        winStatus = WinStatus.WIN
    else:
        winStatus = WinStatus.LOSE
    sessionCtx = sessionProvider.getCtx()
    if sessionCtx.extractLastArenaWinStatus() is not None:
        sessionCtx.setLastArenaWinStatus(WinStatus(winStatus))
    return
