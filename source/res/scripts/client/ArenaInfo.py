# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ArenaInfo.py
import BigWorld
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from debug_utils import LOG_DEBUG_DEV

class ArenaInfo(BigWorld.Entity):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def set_repairCounters(self, _):
        LOG_DEBUG_DEV('RACE: ArenaInfo: set_repairCounters :: ', self.repairCounters)
        BigWorld.player().onRepairCountersEvent(self.repairCounters)

    def set_repairNodePosition(self, _):
        LOG_DEBUG_DEV('RACE: ArenaInfo: set_repairNodePosition :: ', self.repairNodePosition)
        BigWorld.player().onRepairNodePositionEvent(self.repairNodePosition)

    def set_raceList(self, _):
        LOG_DEBUG_DEV('RACE: ArenaInfo: set_raceList :: ', self.raceList)
        self.updateRaceListStats()
        for rPos, entityID in self.raceList:
            LOG_DEBUG_DEV('RACE: {} : {} '.format(rPos, entityID))

    def set_finishTimeList(self, _):
        LOG_DEBUG_DEV('RACE: ArenaInfo: set_finishTimeList :: ', self.finishTimeList)
        self.updateRaceFinishTimeStats()

    def onCheckpoint(self, vehicleID, checkpointName):
        LOG_DEBUG_DEV('RACE: ArenaInfo: onCheckpoint :: ', vehicleID, checkpointName)
        BigWorld.player().onCheckpointEvent(vehicleID, checkpointName)

    def onEnterWorld(self, prereqs):
        BigWorld.player().arena.registerArenaInfo(self)

    def onLeaveWorld(self):
        BigWorld.player().arena.unregisterArenaInfo(self)

    def updateRaceListStats(self):
        LOG_DEBUG_DEV('RACE: ArenaInfo: updateRaceListStats :: ', self.raceList)
        ctrl = self.__sessionProvider.dynamic.eventRacePosition
        if ctrl is not None:
            ctrl.onRacePositionsUpdate(self.raceList)
        arena = BigWorld.player().arena
        if not arena:
            return
        else:
            gameModeStats = dict(((vehicleID, {'playerRacePosition': pos}) for pos, vehicleID in self.raceList))
            arena.onGameModeSpecifcStats(False, gameModeStats, True)
            return

    def updateRaceFinishTimeStats(self):
        LOG_DEBUG_DEV('RACE: ArenaInfo: updateRaceFinishTimeStats :: ', self.finishTimeList)
        arena = BigWorld.player().arena
        if not arena:
            return
        gameModeStats = dict(((item['vehicleID'], {'playerRaceFinishTime': item['finishTime']}) for item in self.finishTimeList))
        arena.onGameModeSpecifcStats(False, gameModeStats, True)
