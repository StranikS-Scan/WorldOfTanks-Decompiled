# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/battle_results/states.py
from __future__ import absolute_import
from functools import partial
from comp7.gui.Scaleform.genConsts.COMP7_HANGAR_ALIASES import COMP7_HANGAR_ALIASES
from constants import ARENA_BONUS_TYPE
from frameworks.state_machine.transitions import TransitionType
from gui.Scaleform.framework.entities.View import ViewKey
from gui.battle_results.settings import PLAYER_TEAM_RESULT
from gui.impl.lobby.battle_results.states import generatePostBattleStateClasses, PostBattleResultsEntryProto, LoadingProto, LoadingWithRetainedCameraProto, PostBattleResultsProto, OverviewTabProto, TeamScoreTabProto, MissionProgressTabProto, FinancialReportTabProto, PBSSceneSetup, shouldHijackPBSEntry
from gui.lobby_state_machine.states import SubScopeSubLayerState
from gui.lobby_state_machine.transitions import HijackTransition
from gui.shared.utils.functions import getArenaImage
from gui.subhangar.subhangar_observer import selectItemByTankSize
from gui.subhangar.subhangar_state_groups import SubhangarStateGroups, SubhangarStateGroupConfig
from helpers import dependency
from skeletons.gui.battle_results import IBattleResultsService
_COMP7_PBS_SUBHANGAR_GROUPS_BY_SIZE = (SubhangarStateGroups.Comp7PostBattleSmall, SubhangarStateGroups.Comp7PostBattleMedium, SubhangarStateGroups.Comp7PostBattleLarge)
_COMP7_BONUS_TYPE_RANGE = (ARENA_BONUS_TYPE.COMP7, ARENA_BONUS_TYPE.TOURNAMENT_COMP7, ARENA_BONUS_TYPE.TRAINING_COMP7)
_TANK_SIZE_LOWER_BOUNDS = (float('-inf'), 5.0, 8.0)

class Comp7PostBattleResultsEntryProto(PostBattleResultsEntryProto):
    STATE_ID = 'comp7/postBattleResultsEntry'
    __battleResults = dependency.descriptor(IBattleResultsService)

    def getSubhangarStateGroupConfig(self):
        arenaUniqueID = self._cachedParams.get('arenaUniqueID', None)
        statsController = self.__battleResults.getStatsCtrl(arenaUniqueID)
        _, reusable = statsController.getResults()
        teamResultType = SubhangarStateGroups.Comp7PostBattleDefeat
        if reusable:
            teamResult = reusable.getPersonalTeamResult()
            if teamResult == PLAYER_TEAM_RESULT.WIN:
                teamResultType = SubhangarStateGroups.Comp7PostBattleVictory
        return SubhangarStateGroupConfig((teamResultType,))


class Comp7LoadingProto(LoadingProto):
    STATE_ID = 'comp7/loading'


class Comp7LoadingWithRetainedCameraProto(LoadingWithRetainedCameraProto):
    STATE_ID = 'comp7/loadingWithRetainedCamera'
    __battleResults = dependency.descriptor(IBattleResultsService)

    def getSubhangarStateGroupConfig(self):
        return SubhangarStateGroupConfig((selectItemByTankSize(_TANK_SIZE_LOWER_BOUNDS, _COMP7_PBS_SUBHANGAR_GROUPS_BY_SIZE), SubhangarStateGroups.Comp7PostBattleCommon))


class Comp7PostBattleResultsProto(PostBattleResultsProto):
    STATE_ID = 'comp7/postBattleResults'
    VIEW_KEY = ViewKey(COMP7_HANGAR_ALIASES.COMP7_BATTLE_RESULTS)
    __battleResults = dependency.descriptor(IBattleResultsService)

    def getSubhangarStateGroupConfig(self):
        _, reusable = self.__battleResults.getStatsCtrl(self._cachedParams.get('arenaUniqueID', None)).getResults()
        geometryName = reusable.common.arenaType.getGeometryName()
        mapImageName = getArenaImage(geometryName, 'screen')
        mapImageName = mapImageName.replace('img://', '')
        return SubhangarStateGroupConfig((selectItemByTankSize(_TANK_SIZE_LOWER_BOUNDS, _COMP7_PBS_SUBHANGAR_GROUPS_BY_SIZE), SubhangarStateGroups.Comp7PostBattleCommon), PBSSceneSetup(mapImageName))


class Comp7OverviewTabProto(OverviewTabProto):
    STATE_ID = 'comp7/overview'


class Comp7TeamScoreTabProto(TeamScoreTabProto):
    STATE_ID = 'comp7/teamScore'


class Comp7MissionProgressTabProto(MissionProgressTabProto):
    STATE_ID = 'comp7/missionProgress'


class Comp7FinancialReportTabProto(FinancialReportTabProto):
    STATE_ID = 'comp7/financialReport'


Comp7PostBattleResultsEntryState, Comp7LoadingState, Comp7LoadingStateWithRetainedCamera, Comp7PostBattleResultsState, Comp7OverviewTab, Comp7TeamScoreTab, Comp7MissionProgressTab, Comp7FinancialReportTab = generatePostBattleStateClasses(SubScopeSubLayerState, entryStateProto=Comp7PostBattleResultsEntryProto, loadingProto=Comp7LoadingProto, loadingWithRetainedCameraProto=Comp7LoadingWithRetainedCameraProto, resultsProto=Comp7PostBattleResultsProto, overviewProto=Comp7OverviewTabProto, teamScoreProto=Comp7TeamScoreTabProto, missionProgressProto=Comp7MissionProgressTabProto, financialReportProto=Comp7FinancialReportTabProto)

def registerStates(lsm):
    lsm.addState(Comp7PostBattleResultsEntryState())


def registerTransitions(lsm):
    comp7PbsEntry = lsm.getStateByCls(Comp7PostBattleResultsEntryState)
    lsm.addNavigationTransitionFromParent(comp7PbsEntry, transitionType=TransitionType.EXTERNAL)
    parent = comp7PbsEntry.getParent()
    comp7PbsEntry.addTransition(HijackTransition(Comp7PostBattleResultsEntryState, partial(shouldHijackPBSEntry, targetStateClass=Comp7PostBattleResultsState), transitionType=TransitionType.EXTERNAL), lsm.getStateByCls(Comp7LoadingStateWithRetainedCamera))
    parent.addTransition(HijackTransition(Comp7PostBattleResultsEntryState, partial(shouldHijackPBSEntry, targetStateClass=Comp7PostBattleResultsState), transitionType=TransitionType.EXTERNAL), lsm.getStateByCls(Comp7LoadingStateWithRetainedCamera))
