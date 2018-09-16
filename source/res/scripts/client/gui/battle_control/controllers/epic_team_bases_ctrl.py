# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/epic_team_bases_ctrl.py
import BigWorld
import BattleReplay
from debug_utils import LOG_ERROR
from epic_constants import EPIC_BATTLE_TEAM_ID
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from team_bases_ctrl import BattleTeamsBasesController, makeClientTeamBaseID

class EpicBattleTeamsBasesController(BattleTeamsBasesController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(EpicBattleTeamsBasesController, self).__init__()
        self.__capturedBasesDict = {}
        self.__currentBaseID = None
        self.__currentBaseTeam = EPIC_BATTLE_TEAM_ID.TEAM_DEFENDER
        return

    def startControl(self, battleCtx, arenaVisitor):
        super(EpicBattleTeamsBasesController, self).startControl(battleCtx, arenaVisitor)
        componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
        playerDataComp = getattr(componentSystem, 'playerDataComponent', None)
        if playerDataComp is not None:
            playerDataComp.onPlayerPhysicalLaneUpdated += self.__onPlayerPhysicalLaneUpdated
        else:
            LOG_ERROR('Expected PlayerDataComponent not present!')
        sectorBaseComp = getattr(componentSystem, 'sectorBaseComponent', None)
        if sectorBaseComp is not None:
            sectorBaseComp.onSectorBaseCaptured += self.__onSectorBaseCaptured
            sectorBaseComp.onSectorBasePointsUpdate += self.__onSectorBasePointsUpdate
        else:
            LOG_ERROR('Expected SectorBaseComponent not present!')
        return

    def stopControl(self):
        componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
        playerDataComp = getattr(componentSystem, 'playerDataComponent', None)
        if playerDataComp is not None:
            playerDataComp.onPlayerPhysicalLaneUpdated -= self.__onPlayerPhysicalLaneUpdated
        sectorBaseComp = getattr(componentSystem, 'sectorBaseComponent', None)
        if sectorBaseComp is not None:
            sectorBaseComp.onSectorBaseCaptured -= self.__onSectorBaseCaptured
            sectorBaseComp.onSectorBasePointsUpdate -= self.__onSectorBasePointsUpdate
        super(EpicBattleTeamsBasesController, self).stopControl()
        return

    def _teamBaseLeft(self, points, invadersCnt):
        return not points and invadersCnt < 1

    def _updatePoints(self, clientID):
        if not self._containsClientID(clientID):
            return
        points, timeLeftTimeStamp, invadersCnt, stopped = self._getPoints(clientID)
        if stopped:
            return
        timeLeft = timeLeftTimeStamp - BigWorld.serverTime()
        rate = self._getProgressRate()
        if self._viewComponents and self._getSnapDictForClientID(clientID) != (points, rate, timeLeft) and points > 0:
            self._setSnapForClientID(clientID, points, rate, timeLeft)
            for viewCmp in self._viewComponents:
                viewCmp.updateTeamBasePoints(clientID, points, rate, timeLeft, invadersCnt)

    def __invalidateTeamBasePoints(self, baseID, points, timeLeft, invadersCnt, capturingStopped):
        self.__currentBaseID = None
        if points > 0:
            self.__currentBaseID = baseID
        super(EpicBattleTeamsBasesController, self).invalidateTeamBasePoints(self.__currentBaseTeam, baseID, points, timeLeft, invadersCnt, capturingStopped)
        return

    def _addCapturingTeamBase(self, clientID, playerTeam, points, timeLeft, invadersCnt, capturingStopped):
        timeLeftTimeStamp = timeLeft - BigWorld.serverTime()
        for viewCmp in self._viewComponents:
            viewCmp.addCapturingTeamBase(clientID, playerTeam, points, self._getProgressRate(), timeLeftTimeStamp, invadersCnt, capturingStopped)

    def __invalidateTeamBaseCaptured(self, baseID):
        if not self.__isInMyLane(baseID):
            return
        else:
            self.__currentBaseID = None
            super(EpicBattleTeamsBasesController, self).invalidateTeamBaseCaptured(self.__currentBaseTeam, baseID)
            clientID = makeClientTeamBaseID(self.__currentBaseTeam, baseID)
            for viewCmp in self._viewComponents:
                viewCmp.removeTeamBase(clientID)

            self._removeBarEntry(clientID, self.__currentBaseTeam)
            return

    def __onPlayerPhysicalLaneUpdated(self, laneID):
        if not self.__currentBaseID:
            return
        else:
            componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
            sectorBaseComp = getattr(componentSystem, 'sectorBaseComponent', None)
            if sectorBaseComp is None:
                LOG_ERROR('Expected SectorBaseComponent not present!')
                return
            baseLane = sectorBaseComp.getSectorForSectorBase(self.__currentBaseID).playerGroup
            if baseLane != laneID:
                clientID = makeClientTeamBaseID(self.__currentBaseTeam, self.__currentBaseID)
                for viewCmp in self._viewComponents:
                    viewCmp.removeTeamBase(clientID)

                self.__currentBaseID = None
                self._removeBarEntry(clientID, self.__currentBaseTeam)
            return

    def __isInMyLane(self, baseID):
        componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
        sectorBaseComp = getattr(componentSystem, 'sectorBaseComponent', None)
        if sectorBaseComp is None:
            LOG_ERROR('Expected SectorBaseComponent not present!')
            return
        else:
            playerData = getattr(componentSystem, 'playerDataComponent', None)
            if playerData is None:
                LOG_ERROR('Expected PlayerDataComponent not present!')
                return
            baseLane = sectorBaseComp.getSectorForSectorBase(baseID).playerGroup
            return False if baseLane != playerData.physicalLane else True

    def __onSectorBaseCaptured(self, baseId, isPlayerTeam):
        self.__capturedBasesDict[baseId] = True
        self.__invalidateTeamBaseCaptured(baseId)

    def __onSectorBasePointsUpdate(self, baseId, isPlayerTeam, points, capturingStopped, invadersCount, expectedCaptureTime):
        if not self.__isInMyLane(baseId) or baseId in self.__capturedBasesDict or expectedCaptureTime < 0:
            return
        truePoints = points * 100
        self.__invalidateTeamBasePoints(baseId, truePoints, expectedCaptureTime, invadersCount, capturingStopped)


class EpicBattleTeamsBasesPlayer(EpicBattleTeamsBasesController):

    def _getProgressRate(self):
        rate = BattleReplay.g_replayCtrl.playbackSpeed
        if rate is None:
            rate = super(EpicBattleTeamsBasesPlayer, self)._getProgressRate()
        return rate


def createEpicTeamsBasesCtrl(setup):
    if setup.isReplayPlaying:
        ctrl = EpicBattleTeamsBasesPlayer()
    else:
        ctrl = EpicBattleTeamsBasesController()
    return ctrl
