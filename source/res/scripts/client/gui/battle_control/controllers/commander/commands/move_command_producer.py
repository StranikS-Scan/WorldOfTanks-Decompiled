# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/commander/commands/move_command_producer.py
import math
from enum import Enum
import BattleReplay
import GUI
import Math
import BigWorld
from RTSShared import RTSCommandQueuePosition
from AvatarInputHandler import cameras
from gui.battle_control.controllers.commander.commands import vehicle_formation
from gui.battle_control.controllers.commander.common import MappedKeys, getPointOnTerrain, center
from gui.battle_control.controllers.commander.cursor import getMousePositionOnTerrain
from gui.battle_control.controllers.commander.interfaces import IMoveCommandProducer
from gui.battle_control.controllers.commander.markers import TerrainOrderMarker
from helpers.CallbackDelayer import CallbackDelayer
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

def _checkAppendWaypoint():
    return MappedKeys.isModifierDown(MappedKeys.MOD_APPEND_ORDER)


class _ControlModeID(Enum):
    INACTIVE, MOVE, ORIENTATE = range(3)


class MoveCommandProducer(IMoveCommandProducer, CallbackDelayer):
    __FORMATION_ROW_COUNT_SCREEN_CHANGE_STEP = 0.09
    __MOUSE_SCREEN_DISTANCE_TO_START_ORIENTATING = 0.0025000000000000005
    __START_ORIENTATING_DELAY = 0.0
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(MoveCommandProducer, self).__init__()
        self.__controlModeID = _ControlModeID.INACTIVE
        self.__controlPoint = None
        self.__vehicleIDs = []
        self.__vehicleModels = {}
        self.__isAppend = False
        self.__position = None
        self.__direction = None
        self.__formationIndex = None
        self.__reverse = False
        self.__canOrientating = False
        self.__formationPositions = []
        self.__markers = {}
        return

    @staticmethod
    def isAppendModeActive():
        enable = MoveCommandProducer.guiSessionProvider.dynamic.rtsCommander.isAppendModeEnabled
        return _checkAppendWaypoint() and enable

    @property
    def isActive(self):
        return self.__controlModeID is not _ControlModeID.INACTIVE

    def reset(self):
        self.disableOrientating()
        self.__controlPoint = None
        self.__vehicleIDs = []
        self.__isAppend = False
        self.__formationIndex = None
        self.__reverse = False
        self.__formationPositions = []
        self.stopCallback(self.__enableOrientating)
        self.stopCallback(self.__rebuildPositions)
        self.__setControlModeID(_ControlModeID.INACTIVE)
        while self.__markers:
            _, marker = self.__markers.popitem()
            marker.fini()

        return

    def update(self):
        if not BattleReplay.g_replayCtrl.isPlaying:
            if self.__controlModeID == _ControlModeID.MOVE:
                self.__updateMoving()
            elif self.__controlModeID == _ControlModeID.ORIENTATE:
                self.__updateOrientating()

    def moveSelected(self, worldPos, vehicles):
        if not vehicles:
            return
        else:
            position = getPointOnTerrain(worldPos)
            if position is None:
                return
            isAppend = self.isAppendModeActive()
            positions = vehicle_formation.build([ v.id for v in vehicles ], position, self.__getDirection(position, vehicles, isAppend))
            return (positions, isAppend)

    def finishMovingOrOrienting(self):
        return (self.__formationPositions,
         self.__markers,
         self.__controlPoint,
         self.isAppendModeActive(),
         self.__vehicleIDs)

    def activateMoving(self, vehicles, position, append, controlPoint, vehicleModels):
        self.__vehicleIDs = [ veh.id for veh in vehicles ]
        self.__vehicleModels = vehicleModels
        self.__controlPoint = controlPoint
        self.__isAppend = append
        self.__position = position
        self.setDirection(self.__getDirection(position, vehicles, self.isAppendModeActive()))
        self.setFormationIndex(1)
        self.__setControlModeID(_ControlModeID.MOVE)

    def startMoving(self, vehicles, vehicleModels, controlPoint=None):
        if self.isActive:
            return False
        elif not vehicles:
            return True
        else:
            position = getMousePositionOnTerrain()
            if position is None:
                return True
            self.activateMoving(vehicles, position, self.isAppendModeActive(), controlPoint, vehicleModels)
            self.disableOrientating()
            self.delayCallback(self.__START_ORIENTATING_DELAY, self.__enableOrientating)
            return True

    def startOrientating(self):
        if self.__controlModeID is not _ControlModeID.MOVE and not BattleReplay.g_replayCtrl.isPlaying:
            return
        self.__setControlModeID(_ControlModeID.ORIENTATE)

    def stopOrientating(self):
        self.stopCallback(self.__enableOrientating)

    def stopRebuildingPositions(self):
        self.stopCallback(self.__rebuildPositions)

    def setDirection(self, direction):
        if self.__direction != direction:
            self.__direction = direction
            self.delayCallback(0.0, self.__rebuildPositions)

    def setFormationIndex(self, formationIndex):
        if formationIndex != self.__formationIndex:
            self.__formationIndex = formationIndex
            self.delayCallback(0.0, self.__rebuildPositions)

    def __updateMoving(self):
        if self.__controlModeID is not _ControlModeID.MOVE or not self.__canOrientating:
            return
        else:
            startMouseScreenPosition = self.__getStartMouseScreenPosition()
            if startMouseScreenPosition is None:
                return
            mousePosition = Math.Vector2(GUI.mcursor().position)
            if startMouseScreenPosition.distSqrTo(mousePosition) >= self.__MOUSE_SCREEN_DISTANCE_TO_START_ORIENTATING:
                self.startOrientating()
            return

    def __enableOrientating(self):
        if self.__controlModeID is not _ControlModeID.MOVE:
            return
        self.__canOrientating = True
        self.__updateMoving()

    def disableOrientating(self):
        self.__canOrientating = False
        self.stopCallback(self.__enableOrientating)

    def __updateOrientating(self):
        if self.__controlModeID is not _ControlModeID.ORIENTATE or not self.__canOrientating:
            return
        else:
            startMouseScreenPosition = self.__getStartMouseScreenPosition()
            if startMouseScreenPosition is None:
                return
            dist = Math.Vector2(GUI.mcursor().position).distSqrTo(startMouseScreenPosition)
            if dist < self.__MOUSE_SCREEN_DISTANCE_TO_START_ORIENTATING:
                return
            mousePosition = getMousePositionOnTerrain()
            if mousePosition is None:
                return
            self.setDirection(mousePosition - self.__position)
            self.setFormationIndex(math.ceil(dist / self.__FORMATION_ROW_COUNT_SCREEN_CHANGE_STEP))
            return

    def __rebuildPositions(self):
        reverse = self.__reverse
        if self.__controlModeID == _ControlModeID.MOVE and BigWorld.isKeyDown(MappedKeys.getKey(MappedKeys.KEY_REV_MOVE)) and self.guiSessionProvider.dynamic.rtsCommander.vehicles.isRetreatEnabled:
            reverse = True
        self.__formationPositions = vehicle_formation.getVehiclesPositions(self.__vehicleIDs, self.__position, self.__direction, reverse, self.__formationIndex)
        self.__updateMarkers()

    def __updateMarkers(self):
        for vehicleID, position, heading in self.__formationPositions:
            if vehicleID in self.__markers:
                self.__markers[vehicleID].update(position, heading)
            newMarker = TerrainOrderMarker(vehicleID, None, position, heading, self.__vehicleModels.get(vehicleID, None))
            newMarker.setCommandQueuePosition(RTSCommandQueuePosition.PREVIEW)
            self.__markers[vehicleID] = newMarker
            proxyVehicle = self.guiSessionProvider.dynamic.rtsCommander.vehicles.get(vehicleID)
            if proxyVehicle.lastCommandInQueue:
                proxyVehicle.lastCommandInQueue.onPreviewAppeared()

        return

    def __setControlModeID(self, ctrlModeID):
        prevActive = self.isActive
        self.__controlModeID = ctrlModeID
        if prevActive == self.isActive:
            return
        else:
            enabled = not self.isActive
            for vID in self.__vehicleIDs:
                marker = self.__markers.get(vID)
                if marker is not None:
                    marker.setEnabled(enabled)

            return

    def __getDirection(self, endPosition, vehicles, isAppend):
        positions = []
        for vehicle in vehicles:
            positions.append(vehicle.lastPosition if isAppend and vehicle.lastPosition is not None else vehicle.position)

        return endPosition - center(positions)

    def __getStartMouseScreenPosition(self):
        if self.__position is None:
            return
        else:
            startMouseScreenPosition = cameras.projectPoint(self.__position)
            return Math.Vector2(startMouseScreenPosition.x, startMouseScreenPosition.y)
