# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/vehicles_count_ctrl.py
from debug_utils import LOG_ERROR, LOG_WARNING
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.arena_info.interfaces import IVehicleCountController
from gui.battle_control.avatar_getter import getPlayerTeam
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class IVehicleCountListener(object):

    def setTotalCount(self, vehicles, teams):
        pass

    def setEnemiesCount(self, vehicles, teams):
        pass

    def setFrags(self, frags, isPlayerVehicle):
        pass

    def setPlayerVehicleAlive(self, isAlive):
        pass


class VehicleCountController(IVehicleCountController):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(VehicleCountController, self).__init__()
        self.__vehicleTeams = {}
        self.__isStarted = False
        self.__enemiesCount = 0
        self.__enemyTeamsCount = 0
        self.__totalCount = 0
        self.__totalTeamsCount = 0
        self.__frags = 0
        self.__isAlive = True
        self.__attachedVehicleID = None
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.VEHICLES_COUNT_CTRL

    def startControl(self, *args):
        pass

    def stopControl(self):
        pass

    def setViewComponents(self, *components):
        self._viewComponents = list(components)
        for view in self._viewComponents:
            self.__setViewData(view)

    def addRuntimeView(self, view):
        if view in self._viewComponents:
            LOG_ERROR('View is already added! {}'.format(view))
        else:
            self.__setViewData(view)
            self._viewComponents.append(view)

    def removeRuntimeView(self, view):
        if view in self._viewComponents:
            self._viewComponents.remove(view)
        else:
            LOG_WARNING('View has not been found! {}'.format(view))

    def invalidateVehiclesInfo(self, arenaDP):
        self.__vehicleTeams.clear()
        for vInfo in arenaDP.getVehiclesInfoIterator():
            if not vInfo.isObserver() and vInfo.isAlive():
                self.__vehicleTeams[vInfo.vehicleID] = vInfo.team
            if vInfo.vehicleID == arenaDP.getPlayerVehicleID():
                self.__isAlive = vInfo.isAlive()

        for view in self._viewComponents:
            view.setPlayerVehicleAlive(self.__isAlive)

        self.__updateTeamsCount()

    def invalidateVehicleStatus(self, flags, vInfoVO, arenaDP):
        if not vInfoVO.isAlive() and vInfoVO.vehicleID in self.__vehicleTeams:
            del self.__vehicleTeams[vInfoVO.vehicleID]
            self.__updateTeamsCount()
        if vInfoVO.vehicleID == arenaDP.getPlayerVehicleID():
            self.__isAlive = vInfoVO.isAlive()
            for view in self._viewComponents:
                view.setPlayerVehicleAlive(self.__isAlive)

    def updateVehiclesStats(self, updated, arenaDP):
        for _, vStats in updated:
            if vStats.vehicleID == self.__attachedVehicleID:
                playerVehicleID = arenaDP.getPlayerVehicleID()
                for view in self._viewComponents:
                    view.setFrags(vStats.frags, self.__attachedVehicleID == playerVehicleID)

                self.__frags = vStats.frags

    def updateAttachedVehicle(self, vehicleID):
        self.__attachedVehicleID = vehicleID
        arenaDP = self.__sessionProvider.getArenaDP()
        self.__updateFrags(arenaDP)
        if vehicleID == arenaDP.getPlayerVehicleID():
            self.__isAlive = arenaDP.getVehicleInfo().isAlive()
            for view in self._viewComponents:
                view.setPlayerVehicleAlive(self.__isAlive)

    def invalidateVehiclesStats(self, arenaDP):
        self.__updateFrags(arenaDP)

    def addVehicleInfo(self, vInfoVO, arenaDP):
        if not vInfoVO.isObserver() and vInfoVO.isAlive():
            self.__vehicleTeams[vInfoVO.vehicleID] = vInfoVO.team
            self.__updateTeamsCount()

    def invalidateArenaInfo(self):
        self.__updateTeamsCount()
        arenaDP = self.__sessionProvider.getArenaDP()
        self.invalidateVehiclesStats(arenaDP)
        self.__isStarted = True

    def __setViewData(self, view):
        if self.__isStarted:
            view.setFrags(self.__frags, self.__attachedVehicleID == self.__sessionProvider.getArenaDP().getPlayerVehicleID())
            view.setTotalCount(self.__totalCount, self.__totalTeamsCount)
            view.setEnemiesCount(self.__enemiesCount, self.__enemyTeamsCount)
            view.setPlayerVehicleAlive(self.__isAlive)

    def __updateTeamsCount(self):
        self.__totalCount = len(set(self.__vehicleTeams.keys()))
        teamSize = self.__vehicleTeams.values().count(getPlayerTeam())
        self.__enemiesCount = self.__totalCount - teamSize
        self.__totalTeamsCount = len(set(self.__vehicleTeams.values()))
        self.__enemyTeamsCount = self.__totalTeamsCount - 1 if teamSize > 0 else self.__totalTeamsCount
        for view in self._viewComponents:
            view.setTotalCount(self.__totalCount, self.__totalTeamsCount)
            view.setEnemiesCount(self.__enemiesCount, self.__enemyTeamsCount)

    def __updateFrags(self, arenaDP):
        self.__frags = arenaDP.getVehicleStats(self.__attachedVehicleID).frags
        playerVehicleID = arenaDP.getPlayerVehicleID()
        for view in self._viewComponents:
            view.setFrags(self.__frags, self.__attachedVehicleID == playerVehicleID)
