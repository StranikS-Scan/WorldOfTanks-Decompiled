# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/battle/team_score_sub_view.py
from __future__ import absolute_import
import typing
from future.utils import viewitems
from helpers import dependency
from helpers.events_handler import EventsHandler
from fort_rush.gui.impl.gen.view_models.views.battle.views.fort_rush_hud_base_capture_indicator_model import FortRushBaseCaptureTeam
from fort_rush.gui.shared.events import CapturePointEvent
from fort_rush.gui.shared.team_utils import getTeamValue
from fort_rush_common.component_helpers import getScoreComponent
from gui.battle_control import avatar_getter
from gui.shared import EVENT_BUS_SCOPE, EventPriority
from skeletons.gui.battle_session import IBattleSessionProvider

class TeamScoreSubView(EventsHandler):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, hudVMRef):
        super(TeamScoreSubView, self).__init__()
        self.__hudViewModelRef = hudVMRef
        self.__teamCaptures = None
        self.__pointOwners = None
        self.__scoreComponent = None
        return

    def init(self):
        arenaDP = self.__sessionProvider.getArenaDP()
        if arenaDP is None:
            return
        else:
            self.__teamCaptures = {getTeamValue(teamID):set() for teamID in arenaDP.getTeamsOnArena()}
            self.__pointOwners = {}
            self.__scoreComponent = getScoreComponent()
            self._subscribe()
            return

    def dispose(self):
        self._unsubscribe()
        self.__hudViewModelRef = None
        self.__teamCaptures = None
        self.__pointOwners = None
        self.__scoreComponent = None
        return

    def _getListeners(self):
        return [(CapturePointEvent.INIT_CAPTURABLE_POINT,
          self.__onInitCapturablePoint,
          EVENT_BUS_SCOPE.BATTLE,
          EventPriority.HIGH), (CapturePointEvent.CAPTURABLE_POINT_UPDATE,
          self.__onCapturePointUpdate,
          EVENT_BUS_SCOPE.BATTLE,
          EventPriority.HIGH)]

    def _getEvents(self):
        events = []
        if self.__scoreComponent is not None:
            events.append((self.__scoreComponent.onTeamsScoreUpdated, self.__onTeamsScoreUpdated))
        return events

    def __onTeamsScoreUpdated(self, updatedScore):
        allyTeam = avatar_getter.getObserverTeam()
        with self.__hudViewModelRef.transaction() as vm:
            for team, score in viewitems(updatedScore):
                if team == allyTeam:
                    vm.setAllyScore(score)
                vm.setEnemyScore(score)

    def __onInitCapturablePoint(self, event):
        name = event.capturablePointName
        self.__pointOwners.setdefault(name, FortRushBaseCaptureTeam.NEUTRAL)
        self.__hudViewModelRef.setBaseCount(len(self.__pointOwners))

    def __onCapturePointUpdate(self, event):
        name = event.capturablePointName
        ownersTeam = getTeamValue(event.ownersTeam)
        prevOwnersTeam = self.__pointOwners.get(name, FortRushBaseCaptureTeam.NEUTRAL)
        self.__pointOwners[name] = ownersTeam
        if prevOwnersTeam not in (ownersTeam, FortRushBaseCaptureTeam.NEUTRAL):
            prevCaptures = self.__teamCaptures.get(prevOwnersTeam, set())
            prevCaptures.discard(name)
            self.__teamCaptures[prevOwnersTeam] = prevCaptures
            self.__notifyFE(prevOwnersTeam, len(prevCaptures))
        if ownersTeam == FortRushBaseCaptureTeam.NEUTRAL:
            return
        if ownersTeam not in self.__teamCaptures:
            return
        captures = self.__teamCaptures[ownersTeam]
        if name in captures:
            return
        captures.add(name)
        self.__notifyFE(ownersTeam, len(captures))

    def __notifyFE(self, team, count):
        if self.__scoreComponent is None:
            self.__scoreComponent = getScoreComponent()
        if not self.__hudViewModelRef.getScoreCap():
            self.__hudViewModelRef.setScoreCap(self.__scoreComponent.scoreCap)
        if team == FortRushBaseCaptureTeam.ENEMY:
            self.__hudViewModelRef.setEnemyCapturedBases(count)
            self.__hudViewModelRef.setPendingEnemyScore(self.__scoreComponent.pointsPerZonesOwned[count])
        elif team == FortRushBaseCaptureTeam.ALLY:
            self.__hudViewModelRef.setAllyCapturedBases(count)
            self.__hudViewModelRef.setPendingAllyScore(self.__scoreComponent.pointsPerZonesOwned[count])
        return
