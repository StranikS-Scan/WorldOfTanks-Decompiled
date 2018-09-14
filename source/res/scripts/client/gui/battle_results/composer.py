# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/composer.py
from constants import ARENA_BONUS_TYPE
from gui.battle_results import templates
from gui.battle_results.components import base

class StatsComposer(object):
    __slots__ = ('_block', '_animation')

    def __init__(self, reusable, common, personal, teams, text, animation=None):
        super(StatsComposer, self).__init__()
        self._block = base.StatsBlock(templates.TOTAL_VO_META)
        if reusable.common.isMultiTeamMode:
            self._block.addNextComponent(templates.MULTI_TEAM_TABS_BLOCK.clone())
        else:
            self._block.addNextComponent(templates.REGULAR_TABS_BLOCK.clone())
        self._block.addNextComponent(text)
        self._block.addNextComponent(templates.VEHICLE_PROGRESS_STATS_BLOCK.clone())
        self._block.addNextComponent(templates.QUESTS_PROGRESS_STATS_BLOCK.clone())
        self._block.addNextComponent(common)
        self._block.addNextComponent(personal)
        self._block.addNextComponent(teams)
        self._animation = animation

    def clear(self):
        self._block.clear()
        if self._animation is not None:
            self._animation.clear()
        return

    def setResults(self, results, reusable):
        self._block.setRecord(results, reusable)
        if self._animation is not None:
            self._animation.setRecord(results, reusable)
        return

    def getVO(self):
        return self._block.getVO()

    def popAnimation(self):
        if self._animation is not None:
            animation = self._animation.getVO()
            self._animation.clear()
            self._animation = None
        else:
            animation = None
        return animation


class RegularStatsComposer(StatsComposer):

    def __init__(self, reusable):
        super(RegularStatsComposer, self).__init__(reusable, templates.REGULAR_COMMON_STATS_BLOCK.clone(), templates.REGULAR_PERSONAL_STATS_BLOCK.clone(), templates.REGULAR_TEAMS_STATS_BLOCK.clone(), templates.REGULAR_TEXT_STATS_BLOCK.clone())


class FalloutStatsComposer(StatsComposer):

    def __init__(self, reusable):
        super(FalloutStatsComposer, self).__init__(reusable, templates.FALLOUT_COMMON_STATS_BLOCK.clone(), templates.REGULAR_PERSONAL_STATS_BLOCK.clone(), templates.REGULAR_TEAMS_STATS_BLOCK.clone(), templates.REGULAR_TEXT_STATS_BLOCK.clone())


class CyberSportStatsComposer(StatsComposer):

    def __init__(self, reusable):
        super(CyberSportStatsComposer, self).__init__(reusable, templates.REGULAR_COMMON_STATS_BLOCK.clone(), templates.REGULAR_PERSONAL_STATS_BLOCK.clone(), templates.REGULAR_TEAMS_STATS_BLOCK.clone(), templates.REGULAR_TEXT_STATS_BLOCK.clone())


class RatedSandboxStatsComposer(RegularStatsComposer):

    def __init__(self, reusable):
        super(RatedSandboxStatsComposer, self).__init__(reusable)
        self._block.addNextComponent(templates.SANDBOX_TEAM_ITEM_STATS_ENABLE.clone())
        self._block.addNextComponent(templates.SANDBOX_PERSONAL_ACCOUNT_DB_ID.clone())


class SandboxStatsComposer(StatsComposer):

    def __init__(self, reusable):
        super(SandboxStatsComposer, self).__init__(reusable, templates.REGULAR_COMMON_STATS_BLOCK.clone(), templates.SANDBOX_PERSONAL_STATS_BLOCK.clone(), templates.REGULAR_TEAMS_STATS_BLOCK.clone(), templates.REGULAR_TEXT_STATS_BLOCK.clone())
        self._block.addNextComponent(templates.SANDBOX_TEAM_ITEM_STATS_ENABLE.clone())
        self._block.addNextComponent(templates.SANDBOX_PERSONAL_ACCOUNT_DB_ID.clone())


class StrongholdBattleStatsComposer(StatsComposer):

    def __init__(self, reusable):
        super(StrongholdBattleStatsComposer, self).__init__(reusable, templates.STRONGHOLD_BATTLE_COMMON_STATS_BLOCK.clone(), templates.REGULAR_PERSONAL_STATS_BLOCK.clone(), templates.REGULAR_TEAMS_STATS_BLOCK.clone(), templates.REGULAR_TEXT_STATS_BLOCK.clone())


class RankedBattlesStatsComposer(StatsComposer):

    def __init__(self, reusable):
        super(RankedBattlesStatsComposer, self).__init__(reusable, templates.RANKED_COMMON_STATS_BLOCK.clone(), templates.REGULAR_PERSONAL_STATS_BLOCK.clone(), templates.RANKED_TEAMS_STATS_BLOCK.clone(), templates.REGULAR_TEXT_STATS_BLOCK.clone())
        self.__resultsTeamsBlock = base.StatsBlock(templates.RANKED_RESULTS_BLOCK)
        self.__resultsTeamsBlock.addNextComponent(templates.RANKED_RESULTS_BLOCK_TITLE.clone())
        self.__resultsTeamsBlock.addNextComponent(templates.RANKED_RESULTS_TEAMS_STATS_BLOCK.clone())

    def clear(self):
        super(RankedBattlesStatsComposer, self).clear()
        self.__resultsTeamsBlock.clear()

    def setResults(self, results, reusable):
        super(RankedBattlesStatsComposer, self).setResults(results, reusable)
        self.__resultsTeamsBlock.setRecord(results, reusable)

    def getResultsTeamsVO(self):
        """
        Returns VO for external RankedBattlesBattleResults view.
        """
        return self.__resultsTeamsBlock.getVO()


def createComposer(reusable):
    """Create composer to build data by type of bonus.
    :param reusable: instance of _ReusableInfo.
    :return: instance of composer.
    """
    bonusType = reusable.common.arenaBonusType
    if bonusType == ARENA_BONUS_TYPE.CYBERSPORT:
        composer = CyberSportStatsComposer(reusable)
    elif bonusType in ARENA_BONUS_TYPE.FALLOUT_RANGE:
        composer = FalloutStatsComposer(reusable)
    elif bonusType == ARENA_BONUS_TYPE.RATED_SANDBOX:
        composer = RatedSandboxStatsComposer(reusable)
    elif bonusType == ARENA_BONUS_TYPE.SANDBOX:
        composer = SandboxStatsComposer(reusable)
    elif bonusType == ARENA_BONUS_TYPE.FORT_BATTLE_2:
        composer = StrongholdBattleStatsComposer(reusable)
    elif bonusType == ARENA_BONUS_TYPE.RANKED:
        composer = RankedBattlesStatsComposer(reusable)
    else:
        composer = RegularStatsComposer(reusable)
    return composer
