# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/epic_respawn_ctrl.py
import BigWorld
from debug_utils import LOG_ERROR, LOG_DEBUG
from gui.battle_control import avatar_getter
from gui.battle_control.controllers.respawn_ctrl import RespawnsController, IRespawnView
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
EB_MIN_RESPAWN_LANE_IDX = 1
EB_MAX_RESPAWN_LANE_IDX = 4

class IEpicRespawnView(IRespawnView):

    def setSelectedLane(self, laneId):
        pass

    def setSelectedPoint(self, pointId):
        pass

    def setRespawnInfo(self, respawnInfo):
        pass

    def setLaneState(self, laneID, enabled, blockedText):
        pass


class EpicRespawnsController(RespawnsController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def startControl(self):
        super(EpicRespawnsController, self).startControl()
        playerDataComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'playerDataComponent', None)
        if playerDataComp is not None:
            playerDataComp.onPlayerRespawnLaneUpdated += self.__onPlayerRespawnLaneUpdated
            playerDataComp.onPlayerGroupsChanged += self.__onPlayerGroupsChanged
        else:
            LOG_ERROR('Expected PlayerDataComponent not present!')
        return

    def stopControl(self):
        super(EpicRespawnsController, self).stopControl()
        playerDataComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'playerDataComponent', None)
        if playerDataComp is not None:
            playerDataComp.onPlayerRespawnLaneUpdated -= self.__onPlayerRespawnLaneUpdated
            playerDataComp.onPlayerGroupsChanged -= self.__onPlayerGroupsChanged
        return

    def updateVehicleLimits(self, limits):
        super(EpicRespawnsController, self).updateVehicleLimits(limits)
        self.__onPlayerGroupsChanged(None)
        return

    def updateRespawnInfo(self, respawnInfo):
        super(EpicRespawnsController, self).updateRespawnInfo(respawnInfo)
        self.__onRespawnInfoUpdated(self.respawnInfo)

    @staticmethod
    def requestLaneForRespawn(laneID):
        BigWorld.player().base.respawnController_requestRespawnGroupChange(laneID)

    @staticmethod
    def requestPointForRespawn(respawnZone):
        BigWorld.player().base.respawnController_chooseRespawnZone(respawnZone)

    def _show(self):
        super(EpicRespawnsController, self)._show()
        playerDataComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'playerDataComponent', None)
        if playerDataComp is not None:
            self.__onRespawnInfoUpdated(self.respawnInfo)
            self.__onPlayerRespawnLaneUpdated(playerDataComp.respawnLane)
            self.__onPlayerGroupsChanged(None)
        return

    def __onPlayerRespawnLaneUpdated(self, laneID):
        for viewCmp in self._viewComponents:
            viewCmp.setSelectedLane(laneID)

        self.__onPlayerGroupsChanged(None)
        return

    def __onRespawnInfoUpdated(self, respawnInfo):
        if not self.isRespawnVisible():
            return
        else:
            for viewCmp in self._viewComponents:
                viewCmp.setRespawnInfo(respawnInfo)

            self.__onPlayerGroupsChanged(None)
            return

    def __onPlayerGroupsChanged(self, _):
        if not self.isRespawnVisible():
            return
        else:
            arena = avatar_getter.getArena()
            if arena is None:
                return
            playerDataComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'playerDataComponent', None)
            if playerDataComp is None:
                LOG_ERROR('Expected PlayerDataComponent not present!')
                return
            vehicleLimits = self.getLimits()
            limit = arena.arenaType.playerGroupLimit
            selectedVehicleID = 0
            availableLanes = [ lane for lane in range(EB_MIN_RESPAWN_LANE_IDX, EB_MAX_RESPAWN_LANE_IDX) if playerDataComp.getPlayersForTeamAndGroup(avatar_getter.getPlayerTeam(), lane) < limit ]
            if self.respawnInfo:
                selectedVehicleID = self.respawnInfo.vehicleID
            for lane in range(EB_MIN_RESPAWN_LANE_IDX, EB_MAX_RESPAWN_LANE_IDX):
                if playerDataComp.respawnLane == lane:
                    isEnoughPlace = True
                else:
                    isEnoughPlace = playerDataComp.getPlayersForTeamAndGroup(avatar_getter.getPlayerTeam(), lane) < limit
                isVehicleBlocked = lane in vehicleLimits and selectedVehicleID in vehicleLimits[lane]
                isAvailableForPlayer = (isEnoughPlace or playerDataComp.respawnLane == lane and not availableLanes) and not isVehicleBlocked
                reasonText = ''
                if not isEnoughPlace:
                    reasonText = backport.text(R.strings.epic_battle.deploymentMap.lanePlayerLimitReached())
                elif isVehicleBlocked:
                    reasonText = backport.text(R.strings.epic_battle.deploymentMap.spgLimitReached())
                if not isEnoughPlace or isVehicleBlocked:
                    LOG_DEBUG('lane %d is blocked for %d ', lane, selectedVehicleID, isVehicleBlocked, 0 if lane not in vehicleLimits else vehicleLimits[lane])
                for viewCmp in self._viewComponents:
                    viewCmp.setLaneState(lane, isAvailableForPlayer, reasonText)

            return
