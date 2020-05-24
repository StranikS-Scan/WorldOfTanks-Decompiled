# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/view_points_ctrl.py
import weakref
import functools
import BigWorld
from debug_utils import LOG_DEBUG
from gui.battle_control.arena_info.interfaces import IViewPointsController
from gui.battle_control.arena_info.vos_collections import VehicleInfoSortKey, VehiclesItemsCollection
from gui.battle_control.arena_info.vos_collections import AllyItemsCollection, SquadmanVehicleInfoSortKey
from gui.battle_control.arena_info.vos_collections import AliveItemsCollection
from gui.battle_control.arena_info.vos_collections import SpawnGroupVehicleInfoSortKey
from gui.battle_control.arena_info.vos_collections import SquadmanSpawnGroupVehicleInfoSortKey
from gui.battle_control.arena_info.vos_collections import RankedVehicleInfoSortKey
from gui.battle_control.battle_constants import BATTLE_CTRL_ID

class ViewPointsController(IViewPointsController):
    __slots__ = ('__points', '__arenaDP', '__currentViewPointID', '__currentVehicleID', '__normalSortKey', '__squadManSortKey')

    def __init__(self, setup):
        super(ViewPointsController, self).__init__()
        self.__points = None
        self.__arenaDP = weakref.proxy(setup.arenaDP)
        self.__currentViewPointID = None
        self.__currentVehicleID = None
        self.__normalSortKey = VehicleInfoSortKey
        self.__squadManSortKey = SquadmanVehicleInfoSortKey
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.VIEW_POINTS

    def startControl(self, battleCtx, arenaVisitor):
        self.__points = arenaVisitor.getArenaViewPoints()
        self.__defineSortKeys(arenaVisitor)

    def stopControl(self):
        self.__points = None
        self.__arenaDP = None
        return

    def updateViewPoints(self, viewPoints):
        self.__points = viewPoints

    def updateAttachedVehicle(self, vehicleID):
        self.__currentVehicleID = vehicleID

    def selectVehicle(self, vehicleID):
        if vehicleID is None:
            vehicleID = self.__arenaDP.getPlayerVehicleID()
        self.__doSelect(False, vehicleID)
        return

    def selectViewPoint(self, pointID):
        self.__doSelect(True, pointID)

    def switch(self, isNext=True):
        playerVehicleID = self.__arenaDP.getPlayerVehicleID()
        if self.__arenaDP.isSquadMan(playerVehicleID):
            prebattleID = self.__arenaDP.getVehicleInfo(playerVehicleID).prebattleID
            sortKey = functools.partial(self.__squadManSortKey, prebattleID)
        else:
            sortKey = self.__normalSortKey
        if self.__arenaDP.isPlayerObserver():
            vehiclesCollection = VehiclesItemsCollection(sortKey=sortKey)
        else:
            vehiclesCollection = AllyItemsCollection(sortKey=sortKey)
        vehicles = AliveItemsCollection(vehiclesCollection).iterator(self.__arenaDP)
        items = [ (False, vInfo.vehicleID) for vInfo, _ in vehicles ]
        for index, _ in enumerate(self.__points):
            items.append((True, index))

        if not isNext:
            items.reverse()
        switchToNext = False
        if self.__currentViewPointID is not None:
            currentItem = (True, self.__currentViewPointID)
        else:
            currentItem = (False, self.__currentVehicleID)
            if self.__currentVehicleID == playerVehicleID:
                switchToNext = True
        if self.__doSwitch(switchToNext, items, currentItem):
            return True
        else:
            return True if self.__doSelect(False, playerVehicleID) else self.__doSwitch(True, items, currentItem)

    def __doSwitch(self, switchToNext, items, currentItem):
        for item in items:
            if switchToNext:
                if self.__doSelect(*item):
                    return True
            if item == currentItem:
                switchToNext = True

        return False

    def __doSelect(self, isViewpoint, vehOrPointId):
        if isViewpoint:
            if vehOrPointId == self.__currentViewPointID:
                LOG_DEBUG('Skip switch to current view point!')
                return True
            self.__currentViewPointID = vehOrPointId
            self.__currentVehicleID = None
            BigWorld.player().positionControl.switchViewpoint(True, vehOrPointId)
            return True
        else:
            vehicleInfo = self.__arenaDP.getVehicleInfo(vehOrPointId)
            if vehicleInfo.isObserver():
                LOG_DEBUG('Skip switch to observer vehicle!')
                return False
            if vehOrPointId == self.__currentVehicleID:
                LOG_DEBUG('Skip switch to current vehicle!')
                return True
            if vehOrPointId != self.__arenaDP.getPlayerVehicleID() and not vehicleInfo.isAlive():
                LOG_DEBUG('Skip switch to dead vehicle!')
                return False
            if not self.__arenaDP.isAllyTeam(vehicleInfo.team) and not self.__arenaDP.isPlayerObserver():
                LOG_DEBUG('Skip switch to enemy vehicle!')
                return False
            self.__currentViewPointID = None
            self.__currentVehicleID = vehOrPointId
            BigWorld.player().positionControl.switchViewpoint(False, vehOrPointId)
            return True

    def __defineSortKeys(self, arenaVisitor):
        if arenaVisitor.getArenaType().numPlayerGroups > 0 and arenaVisitor.gui.isEpicRandomBattle():
            self.__normalSortKey = SpawnGroupVehicleInfoSortKey
            self.__squadManSortKey = SquadmanSpawnGroupVehicleInfoSortKey
        elif arenaVisitor.gui.isRankedBattle():
            self.__normalSortKey = RankedVehicleInfoSortKey
