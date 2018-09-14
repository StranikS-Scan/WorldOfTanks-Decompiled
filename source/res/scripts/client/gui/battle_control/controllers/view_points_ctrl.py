# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/view_points_ctrl.py
import weakref
import BigWorld
import functools
from debug_utils import LOG_DEBUG
from gui.battle_control.arena_info.interfaces import IViewPointsController
from gui.battle_control.arena_info.vos_collections import VehicleInfoSortKey, VehiclesItemsCollection
from gui.battle_control.arena_info.vos_collections import AllyItemsCollection, SquadmanVehicleInfoSortKey
from gui.battle_control.arena_info.vos_collections import AliveItemsCollection
from gui.battle_control.battle_constants import BATTLE_CTRL_ID

class ViewPointsController(IViewPointsController):
    """
    View points controller that track its changes and allows switching
    """
    __slots__ = ('__points', '__arenaDP', '__currentViewPointID', '__currentVehicleID')

    def __init__(self, setup):
        super(ViewPointsController, self).__init__()
        self.__points = None
        self.__arenaDP = weakref.proxy(setup.arenaDP)
        self.__currentViewPointID = None
        self.__currentVehicleID = None
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.VIEW_POINTS

    def startControl(self, battleCtx, arenaVisitor):
        self.__points = arenaVisitor.getArenaViewPoints()

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
        """
        Switch to next or previous vehicle or view point.
        The order of items to switch is next:
        - current players (zero point)
        - squadmen (if available)
        - allies
        - enemies (if observer)
        - view points (if presented)
        
        After full circle we're going back to the start.
        
        :param isNext: switch order
        """
        playerVehicleID = self.__arenaDP.getPlayerVehicleID()
        if self.__arenaDP.isSquadMan(playerVehicleID):
            prebattleID = self.__arenaDP.getVehicleInfo(playerVehicleID).prebattleID
            sortKey = functools.partial(SquadmanVehicleInfoSortKey, prebattleID)
        else:
            sortKey = VehicleInfoSortKey
        canSwitchToHimself = True
        if self.__arenaDP.isPlayerObserver():
            canSwitchToHimself = False
            vehiclesCollection = VehiclesItemsCollection(sortKey=sortKey)
        else:
            vehiclesCollection = AllyItemsCollection(sortKey=sortKey)
        vehicles = AliveItemsCollection(vehiclesCollection).iterator(self.__arenaDP)
        items = map(lambda (vInfo, _): (False, vInfo.vehicleID), vehicles)
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
        elif canSwitchToHimself:
            return self.__doSelect(False, playerVehicleID)
        else:
            return self.__doSwitch(True, items, currentItem)
            return

    def __doSwitch(self, switchToNext, items, currentItem):
        """
        Itreates trough given items list and tries to find current, then select next one
        :param switchToNext: should we switch to first item right from the start
        :param items: list of items as (isViewPoint, ID)
        :param currentItem: currently selected item, same like (isViewPoint, ID)
        :return: was something selected
        """
        for item in items:
            if switchToNext:
                if self.__doSelect(*item):
                    return True
            if item == currentItem:
                switchToNext = True

        return False

    def __doSelect(self, isViewpoint, vehOrPointId):
        """
        Selects given item at server
        :param isViewpoint: is this a view point
        :param vehOrPointId: item ID
        """
        if isViewpoint:
            self.__currentViewPointID = vehOrPointId
            self.__currentVehicleID = None
        else:
            if vehOrPointId == self.__currentVehicleID:
                LOG_DEBUG('Skip switch to current vehicle!')
                return True
            if vehOrPointId != self.__arenaDP.getPlayerVehicleID() and not self.__arenaDP.getVehicleInfo(vehOrPointId).isAlive():
                LOG_DEBUG('Skip switch to dead vehicle!')
                return False
            self.__currentViewPointID = None
            self.__currentVehicleID = vehOrPointId
        BigWorld.player().positionControl.switchViewpoint(isViewpoint, vehOrPointId)
        return True
