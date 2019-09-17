# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/event_repair_ctrl.py
import Math
import BigWorld
from Event import Event
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.arena_info.interfaces import IBattleController
from helpers import isPlayerAvatar
from debug_utils import LOG_DEBUG_DEV
from constants import RACE_CHECKPOINTS

class EventRepairController(IBattleController):

    def __init__(self):
        super(EventRepairController, self).__init__()
        self.onRepairCountersUpdated = Event()
        self.onRepairBaseAdded = Event()
        self.onShowRepair = Event()
        self.onRepairCheckpoint = Event()
        self.onPlayerRepaired = Event()
        self.onOtherRepaired = Event()
        LOG_DEBUG_DEV('EventRepairController: _init_()')
        self.__repairCheckpointId = 0

    def getControllerID(self):
        return BATTLE_CTRL_ID.EVENT_REPAIR

    @staticmethod
    def hasBasePosition():
        player = BigWorld.player()
        return player.arena.arenaInfo.repairNodePosition != Math.Vector3() if player and player.arena.arenaInfo else False

    @staticmethod
    def getBasePosition():
        player = BigWorld.player()
        return player.arena.arenaInfo.repairNodePosition if player and player.arena.arenaInfo else 0

    @staticmethod
    def getCounters():
        player = BigWorld.player()
        return player.arena.arenaInfo.repairCounters if player and player.arena.arenaInfo else (0, 0)

    @staticmethod
    def shouldShowRepair():
        player = BigWorld.player()
        if player.arena.arenaType.race is None:
            return False
        else:
            raceConfig = player.arena.arenaType.race
            checkpointsNames = raceConfig['checkpoints']
            checkpointsSequence = raceConfig['sequence']
            lastCheckpointId = player.vehicle.lastCheckpointID if player.vehicle is not None else 0
            start = checkpointsNames.keys()[checkpointsNames.values().index(RACE_CHECKPOINTS.SHOW_REPAIR)]
            stop = checkpointsNames.keys()[checkpointsNames.values().index(RACE_CHECKPOINTS.REPAIR)]
            showCheckpoints = checkpointsSequence[checkpointsSequence.index(start):checkpointsSequence.index(stop)]
            return lastCheckpointId in showCheckpoints

    def startControl(self, *args):
        LOG_DEBUG_DEV('RACE: EventRepairController: arenaLoadCompleted()')
        player = BigWorld.player()
        if isPlayerAvatar():
            player.onCheckpointEvent += self.__onCheckpoint
            player.onRepairNodePositionEvent += self.__onRepairNodePosition
            player.onRepairCountersEvent += self.__onRepairCountersUpdate
        if player.arena.arenaType.race is not None:
            raceConfig = player.arena.arenaType.race
            checkpointsNames = raceConfig['checkpoints']
            repairIdx = checkpointsNames.values().index(RACE_CHECKPOINTS.REPAIR)
            self.__repairCheckpointId = checkpointsNames.keys()[repairIdx]
        return

    def stopControl(self):
        player = BigWorld.player()
        if isPlayerAvatar() and player.isEnabledRace:
            player.onCheckpointEvent -= self.__onCheckpoint
            player.onRepairNodePositionEvent -= self.__onRepairNodePosition
            player.onRepairCountersEvent -= self.__onRepairCountersUpdate

    def vehicleRepaired(self, vehicleID, amount, repaired):
        if vehicleID == BigWorld.player().playerVehicleID:
            self.onPlayerRepaired(amount, repaired)
        else:
            self.onOtherRepaired(vehicleID, amount, repaired)

    def isRepairActiveForVehicle(self, vehicle):
        return False if vehicle is None else vehicle.lastCheckpointID != self.__repairCheckpointId

    def __onCheckpoint(self, vehicleID, name):
        player = BigWorld.player()
        vId = player.vehicle.id if player.vehicle else 0
        if vehicleID != vId:
            return
        if name == RACE_CHECKPOINTS.SHOW_REPAIR:
            if player.arena.arenaInfo:
                self.onShowRepair(player.arena.arenaInfo.repairNodePosition, player.arena.arenaInfo.repairCounters)
        elif name == RACE_CHECKPOINTS.REPAIR:
            self.onRepairCheckpoint()

    def __onRepairNodePosition(self, position):
        self.onRepairBaseAdded(position)

    def __onRepairCountersUpdate(self, counters):
        self.onRepairCountersUpdated(counters)
