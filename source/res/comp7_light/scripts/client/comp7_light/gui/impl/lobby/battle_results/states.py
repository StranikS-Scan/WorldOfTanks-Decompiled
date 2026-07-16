# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/battle_results/states.py
from __future__ import absolute_import
from functools import partial
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
from comp7_light.gui.Scaleform.genConsts.COMP7_LIGHT_HANGAR_ALIASES import COMP7_LIGHT_HANGAR_ALIASES
from skeletons.gui.battle_results import IBattleResultsService
_TANK_SIZE_LOWER_BOUNDS = (float('-inf'), 5.0, 8.0)
_PBS_SUBHANGAR_GROUPS_BY_SIZE = (SubhangarStateGroups.PostBattleSmall, SubhangarStateGroups.PostBattleMedium, SubhangarStateGroups.PostBattleLarge)

class Comp7LightPostBattleResultsEntryProto(PostBattleResultsEntryProto):
    STATE_ID = 'comp7Light/postBattleResultsEntry'
    __battleResults = dependency.descriptor(IBattleResultsService)

    def getSubhangarStateGroupConfig(self):
        arenaUniqueID = self._cachedParams.get('arenaUniqueID', None)
        statsController = self.__battleResults.getStatsCtrl(arenaUniqueID)
        _, reusable = statsController.getResults()
        teamResultType = SubhangarStateGroups.PostBattleDefeat
        if reusable:
            teamResult = reusable.getPersonalTeamResult()
            if teamResult == PLAYER_TEAM_RESULT.WIN:
                teamResultType = SubhangarStateGroups.PostBattleVictory
        return SubhangarStateGroupConfig((teamResultType,))


class Comp7LightLoadingProto(LoadingProto):
    STATE_ID = 'comp7Light/loading'


class Comp7LightLoadingWithRetainedCameraProto(LoadingWithRetainedCameraProto):
    STATE_ID = 'comp7Light/loadingWithRetainedCamera'

    def getSubhangarStateGroupConfig(self):
        return SubhangarStateGroupConfig((selectItemByTankSize(_TANK_SIZE_LOWER_BOUNDS, _PBS_SUBHANGAR_GROUPS_BY_SIZE), SubhangarStateGroups.PostBattleCommon))


class Comp7LightPostBattleResultsProto(PostBattleResultsProto):
    STATE_ID = 'comp7Light/postBattleResults'
    VIEW_KEY = ViewKey(COMP7_LIGHT_HANGAR_ALIASES.COMP7_LIGHT_BATTLE_RESULTS)
    __battleResults = dependency.descriptor(IBattleResultsService)

    def getSubhangarStateGroupConfig(self):
        _, reusable = self.__battleResults.getStatsCtrl(self._cachedParams.get('arenaUniqueID', None)).getResults()
        sceneSetup = None
        if reusable:
            geometryName = reusable.common.arenaType.getGeometryName()
            mapImageName = getArenaImage(geometryName, 'screen')
            mapImageName = mapImageName.replace('img://', '')
            sceneSetup = PBSSceneSetup(mapImageName)
        return SubhangarStateGroupConfig((selectItemByTankSize(_TANK_SIZE_LOWER_BOUNDS, _PBS_SUBHANGAR_GROUPS_BY_SIZE), SubhangarStateGroups.PostBattleCommon), sceneSetup)


class Comp7LightOverviewTabProto(OverviewTabProto):
    STATE_ID = 'comp7Light/overview'


class Comp7LightTeamScoreTabProto(TeamScoreTabProto):
    STATE_ID = 'comp7Light/teamScore'


class Comp7LightMissionProgressTabProto(MissionProgressTabProto):
    STATE_ID = 'comp7Light/missionProgress'

    def registerTransitions(self):
        from comp7_light.gui.impl.lobby.hangar.states import Comp7LightProgressionState
        super(Comp7LightMissionProgressTabProto, self).registerTransitions()
        lsm = self.getMachine()
        self.addNavigationTransition(lsm.getStateByCls(Comp7LightProgressionState), record=True)


class Comp7LightFinancialReportTabProto(FinancialReportTabProto):
    STATE_ID = 'comp7Light/financialReport'


Comp7LightPostBattleResultsEntryState, Comp7LightLoadingState, Comp7LightLoadingStateWithRetainedCamera, Comp7LightPostBattleResultsState, Comp7LightOverviewTab, Comp7LightTeamScoreTab, Comp7LightMissionProgressTab, Comp7LightFinancialReportTab = generatePostBattleStateClasses(SubScopeSubLayerState, entryStateProto=Comp7LightPostBattleResultsEntryProto, loadingProto=Comp7LightLoadingProto, loadingWithRetainedCameraProto=Comp7LightLoadingWithRetainedCameraProto, resultsProto=Comp7LightPostBattleResultsProto, overviewProto=Comp7LightOverviewTabProto, teamScoreProto=Comp7LightTeamScoreTabProto, missionProgressProto=Comp7LightMissionProgressTabProto, financialReportProto=Comp7LightFinancialReportTabProto)

def registerStates(lsm):
    lsm.addState(Comp7LightPostBattleResultsEntryState())


def registerTransitions(lsm):
    comp7LightPbsEntry = lsm.getStateByCls(Comp7LightPostBattleResultsEntryState)
    lsm.addNavigationTransitionFromParent(comp7LightPbsEntry, transitionType=TransitionType.EXTERNAL)
    parent = comp7LightPbsEntry.getParent()
    comp7LightPbsEntry.addTransition(HijackTransition(Comp7LightPostBattleResultsEntryState, partial(shouldHijackPBSEntry, targetStateClass=Comp7LightPostBattleResultsState), transitionType=TransitionType.EXTERNAL), lsm.getStateByCls(Comp7LightLoadingStateWithRetainedCamera))
    parent.addTransition(HijackTransition(Comp7LightPostBattleResultsEntryState, partial(shouldHijackPBSEntry, targetStateClass=Comp7LightPostBattleResultsState), transitionType=TransitionType.EXTERNAL), lsm.getStateByCls(Comp7LightLoadingStateWithRetainedCamera))
