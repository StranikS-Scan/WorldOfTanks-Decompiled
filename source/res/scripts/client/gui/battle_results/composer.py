# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/composer.py
import typing
from constants import ARENA_BONUS_TYPE
from gui.battle_results import templates
from gui.battle_results.components import base
from gui.battle_results.stats_ctrl import IBattleResultStatsCtrl
from gui.shared import event_dispatcher
from gui.shared.system_factory import registerBattleResultStatsCtrl
from helpers import dependency
from skeletons.gui.game_control import IMapsTrainingController
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel
    BattleResultsModelType = typing.TypeVar('BattleResultsModelType', bound=ViewModel)
    TooltipModelType = typing.TypeVar('TooltipModelType', bound=ViewModel)

class StatsComposer(IBattleResultStatsCtrl):
    __slots__ = ('_block',)

    def __init__(self, reusable, common, personal, teams, text):
        super(StatsComposer, self).__init__()
        self._block = base.StatsBlock(templates.TOTAL_VO_META)
        self._registerTabs(reusable)
        self._block.addNextComponent(text)
        self._block.addNextComponent(templates.VEHICLE_PROGRESS_STATS_BLOCK.clone())
        self._block.addNextComponent(self._getBattlePassBlock().clone())
        self._block.addNextComponent(templates.QUESTS_PROGRESS_STATS_BLOCK.clone())
        self._block.addNextComponent(templates.DOG_TAGS_PROGRESS_STATS_BLOCK.clone())
        self._block.addNextComponent(templates.PRESTIGE_PROGRESS_VO.clone())
        self._block.addNextComponent(common)
        self._block.addNextComponent(personal)
        self._block.addNextComponent(teams)

    def clear(self):
        self._block.clear()

    def setResults(self, results, reusable):
        self._block.setRecord(results, reusable)

    def getVO(self):
        return self._block.getVO()

    @staticmethod
    def onShowResults(arenaUniqueID):
        return event_dispatcher.showBattleResultsWindow(arenaUniqueID)

    @staticmethod
    def onResultsPosted(arenaUniqueID):
        event_dispatcher.notifyBattleResultsPosted(arenaUniqueID)

    def _registerTabs(self, reusable):
        self._block.addNextComponent(templates.REGULAR_TABS_BLOCK.clone())

    @staticmethod
    def _getBattlePassBlock():
        return templates.BATTLE_PASS_PROGRESS_STATS_BLOCK


class RegularStatsComposer(StatsComposer):

    def __init__(self, reusable):
        super(RegularStatsComposer, self).__init__(reusable, templates.REGULAR_COMMON_STATS_BLOCK.clone(), templates.REGULAR_PERSONAL_STATS_BLOCK.clone(), templates.REGULAR_TEAMS_STATS_BLOCK.clone(), templates.REGULAR_TEXT_STATS_BLOCK.clone())
        self._block.addNextComponent(templates.PROGRESSIVE_REWARD_VO.clone())


class EpicStatsComposer(StatsComposer):

    def __init__(self, reusable):
        super(EpicStatsComposer, self).__init__(reusable, templates.EPIC_COMMON_STATS_BLOCK.clone(), templates.EPIC_PERSONAL_STATS_BLOCK.clone(), templates.EPIC_TEAMS_STATS_BLOCK.clone(), templates.REGULAR_TEXT_STATS_BLOCK.clone())

    def _registerTabs(self, reusable):
        self._block.addNextComponent(templates.EPIC_TABS_BLOCK.clone())


class CyberSportStatsComposer(StatsComposer):

    def __init__(self, reusable):
        super(CyberSportStatsComposer, self).__init__(reusable, templates.REGULAR_COMMON_STATS_BLOCK.clone(), templates.REGULAR_PERSONAL_STATS_BLOCK.clone(), templates.REGULAR_TEAMS_STATS_BLOCK.clone(), templates.REGULAR_TEXT_STATS_BLOCK.clone())


class StrongholdBattleStatsComposer(StatsComposer):

    def __init__(self, reusable):
        super(StrongholdBattleStatsComposer, self).__init__(reusable, templates.STRONGHOLD_BATTLE_COMMON_STATS_BLOCK.clone(), templates.STRONGHOLD_PERSONAL_STATS_BLOCK.clone(), templates.STRONGHOLD_TEAMS_STATS_BLOCK.clone(), templates.REGULAR_TEXT_STATS_BLOCK.clone())


class StrongholdSortieBattleStatsComposer(StatsComposer):

    def __init__(self, reusable):
        super(StrongholdSortieBattleStatsComposer, self).__init__(reusable, templates.REGULAR_COMMON_STATS_BLOCK.clone(), templates.STRONGHOLD_PERSONAL_STATS_BLOCK.clone(), templates.STRONGHOLD_TEAMS_STATS_BLOCK.clone(), templates.REGULAR_TEXT_STATS_BLOCK.clone())


class RankedBattlesStatsComposer(StatsComposer):

    def __init__(self, reusable):
        super(RankedBattlesStatsComposer, self).__init__(reusable, templates.RANKED_COMMON_STATS_BLOCK.clone(), templates.RANKED_PERSONAL_STATS_BLOCK.clone(), templates.RANKED_TEAMS_STATS_BLOCK.clone(), templates.REGULAR_TEXT_STATS_BLOCK.clone())
        self.__resultsTeamsBlock = base.StatsBlock(templates.RANKED_RESULTS_BLOCK)
        self.__resultsTeamsBlock.addNextComponent(templates.RANKED_RESULTS_TEAMS_STATS_BLOCK.clone())
        self.__resultsTeamsBlock.addNextComponent(templates.RANKED_ENABLE_ANIMATION_BLOCK.clone())
        self.__resultsTeamsBlock.addNextComponent(templates.RANKED_SHOW_WIDGET_BLOCK.clone())
        self.__resultsTeamsBlock.addNextComponent(templates.RANKED_RESULTS_STATUS_BLOCK.clone())
        self.__resultsTeamsBlock.addNextComponent(templates.RANKED_RESULTS_STATE_BLOCK.clone())

    def clear(self):
        super(RankedBattlesStatsComposer, self).clear()
        self.__resultsTeamsBlock.clear()

    def setResults(self, results, reusable):
        super(RankedBattlesStatsComposer, self).setResults(results, reusable)
        self.__resultsTeamsBlock.setRecord(results, reusable)

    def getResultsTeamsVO(self):
        return self.__resultsTeamsBlock.getVO()


class MapsTrainingStatsComposer(IBattleResultStatsCtrl):
    _fromNotifications = set()
    mapsTrainingController = dependency.descriptor(IMapsTrainingController)

    def __init__(self, _):
        super(MapsTrainingStatsComposer, self).__init__()
        self._block = templates.MAPS_TRAINING_RESULTS_BLOCK.clone()

    def clear(self):
        self._block.clear()

    def setResults(self, results, reusable):
        self.mapsTrainingController.requestInitialDataFromServer(lambda : self._block.setRecord(results, reusable))

    def getVO(self):
        return self._block.getVO()

    @staticmethod
    def onShowResults(arenaUniqueID):
        MapsTrainingStatsComposer._fromNotifications.add(arenaUniqueID)

    @staticmethod
    def onResultsPosted(arenaUniqueID):
        isFromNotifications = arenaUniqueID in MapsTrainingStatsComposer._fromNotifications
        event_dispatcher.showMapsTrainingResultsWindow(arenaUniqueID, isFromNotifications)
        if isFromNotifications:
            MapsTrainingStatsComposer._fromNotifications.remove(arenaUniqueID)


class Comp7StatsComposer(StatsComposer):

    def __init__(self, reusable):
        super(Comp7StatsComposer, self).__init__(reusable, templates.COMP7_COMMON_STATS_BLOCK.clone(), templates.COMP7_PERSONAL_STATS_BLOCK.clone(), templates.COMP7_TEAMS_STATS_BLOCK.clone(), templates.REGULAR_TEXT_STATS_BLOCK.clone())
        self._block.addNextComponent(templates.PROGRESSIVE_REWARD_VO.clone())
        self._block.addNextComponent(templates.EFFICIENCY_TITLE_WITH_SKILLS_VO.clone())

    @staticmethod
    def _getBattlePassBlock():
        return templates.COMP7_BATTLE_PASS_PROGRESS_STATS_BLOCK


class TournamentComp7StatsComposer(StatsComposer):

    def __init__(self, reusable):
        super(TournamentComp7StatsComposer, self).__init__(reusable, templates.TOURNAMENT_COMP7_COMMON_STATS_BLOCK.clone(), templates.TOURNAMENT_COMP7_PERSONAL_STATS_BLOCK.clone(), templates.COMP7_TEAMS_STATS_BLOCK.clone(), templates.REGULAR_TEXT_STATS_BLOCK.clone())
        self._block.addNextComponent(templates.PROGRESSIVE_REWARD_VO.clone())
        self._block.addNextComponent(templates.EFFICIENCY_TITLE_WITH_SKILLS_VO.clone())

    @staticmethod
    def _getBattlePassBlock():
        return templates.COMP7_BATTLE_PASS_PROGRESS_STATS_BLOCK


class TrainingComp7StatsComposer(StatsComposer):

    def __init__(self, reusable):
        super(TrainingComp7StatsComposer, self).__init__(reusable, templates.TRAINING_COMP7_COMMON_STATS_BLOCK.clone(), templates.TRAINING_COMP7_PERSONAL_STATS_BLOCK.clone(), templates.COMP7_TEAMS_STATS_BLOCK.clone(), templates.REGULAR_TEXT_STATS_BLOCK.clone())
        self._block.addNextComponent(templates.PROGRESSIVE_REWARD_VO.clone())
        self._block.addNextComponent(templates.EFFICIENCY_TITLE_WITH_SKILLS_VO.clone())

    @staticmethod
    def _getBattlePassBlock():
        return templates.COMP7_BATTLE_PASS_PROGRESS_STATS_BLOCK


registerBattleResultStatsCtrl(ARENA_BONUS_TYPE.EPIC_BATTLE, EpicStatsComposer)
registerBattleResultStatsCtrl(ARENA_BONUS_TYPE.CYBERSPORT, CyberSportStatsComposer)
registerBattleResultStatsCtrl(ARENA_BONUS_TYPE.FORT_BATTLE_2, StrongholdBattleStatsComposer)
registerBattleResultStatsCtrl(ARENA_BONUS_TYPE.SORTIE_2, StrongholdSortieBattleStatsComposer)
registerBattleResultStatsCtrl(ARENA_BONUS_TYPE.RANKED, RankedBattlesStatsComposer)
registerBattleResultStatsCtrl(ARENA_BONUS_TYPE.MAPS_TRAINING, MapsTrainingStatsComposer)
registerBattleResultStatsCtrl(ARENA_BONUS_TYPE.COMP7, Comp7StatsComposer)
registerBattleResultStatsCtrl(ARENA_BONUS_TYPE.TOURNAMENT_COMP7, TournamentComp7StatsComposer)
registerBattleResultStatsCtrl(ARENA_BONUS_TYPE.TRAINING_COMP7, TrainingComp7StatsComposer)
