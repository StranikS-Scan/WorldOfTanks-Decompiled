# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/battle_control/controllers/vehicles_count_ctrl.py
from constants import ARENA_BONUS_TYPE
from debug_utils import LOG_ERROR, LOG_WARNING
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.arena_info.interfaces import IVehicleCountController
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class IVehicleCountListener(object):

    def setTotalCount(self, vehicles, teams):
        pass

    def setVehicles(self, count, vehicles, teamsCount):
        pass

    def setFrags(self, frags, isPlayerVehicle):
        pass

    def setPlayerVehicleAlive(self, isAlive):
        pass

    def setLives(self, lives):
        pass


class VehicleCountController(IVehicleCountController):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(VehicleCountController, self).__init__()
        self.__vehicles = {}
        self.__totalCount = 0
        self.__friendCount = 0
        self.__enemiesCount = 0
        self.__enemiesTeamCount = 0
        self.__teamCount = 0
        self.__isStarted = False
        self.__frags = 0
        self.__isAlive = True
        self.__attachedVehicleID = None
        self.__isSquadMode = None
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.VEHICLES_COUNT_CTRL

    def startControl(self, *args):
        bonusType = self.__sessionProvider.arenaVisitor.getArenaBonusType()
        self.__isSquadMode = bonusType in ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD_RANGE
        componentSystem = self.__sessionProvider.arenaVisitor.getComponentSystem()
        componentSystem.battleRoyaleComponent.onBattleRoyaleDefeatedTeamsUpdate += self._onDefeatedTeamsUpdated

    def stopControl(self):
        componentSystem = self.__sessionProvider.arenaVisitor.getComponentSystem()
        componentSystem.battleRoyaleComponent.onBattleRoyaleDefeatedTeamsUpdate -= self._onDefeatedTeamsUpdated

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
        self.__vehicles.clear()
        for vInfo in arenaDP.getVehiclesInfoIterator():
            if not vInfo.isObserver():
                self.__updateVehicleInfo(vInfo, arenaDP)
            if vInfo.vehicleID == arenaDP.getPlayerVehicleID():
                self.__isAlive = vInfo.isAlive()

        for view in self._viewComponents:
            view.setPlayerVehicleAlive(self.__isAlive)

        self.__updateData()

    def invalidateVehicleStatus(self, flags, vInfoVO, arenaDP):
        if self.__updateVehicleInfo(vInfoVO, arenaDP):
            self.__updateData()
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

    def updateVehiclesInfo(self, updated, arenaDP):
        statusUpdated = False
        for _, vInfo in updated:
            statusUpdated = self.__updateVehicleInfo(vInfo, arenaDP) or statusUpdated

        if statusUpdated:
            self.__updateData()

    def updateLives(self, lives):
        for view in self._viewComponents:
            view.setLives(lives)

    def _onDefeatedTeamsUpdated(self, *args):
        self.invalidateVehiclesInfo(self.__sessionProvider.getArenaDP())

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
        if vInfoVO.isAlive() and vInfoVO.isPlayer():
            self.__updateVehicleInfo(vInfoVO, arenaDP)
            self.__updateData()

    def getEnemiesCount(self):
        return self.__enemiesCount

    def getTotalCount(self):
        return self.__totalCount

    def getFriendCount(self):
        return self.__friendCount

    def getTeamCount(self):
        return self.__teamCount

    def getEnemiesTeamCount(self):
        return self.__enemiesTeamCount

    def __updateVehicleInfo(self, vInfoVO, arenaDP):
        if not vInfoVO.isPlayer():
            return False
        classType, _, _ = vInfoVO.getTypeInfo()
        team = arenaDP.getVehicleInfo().team
        defeatedTeams = set(self.__sessionProvider.arenaVisitor.getComponentSystem().battleRoyaleComponent.defeatedTeams)
        vehicleInfo = [not vInfoVO.isAlive(),
         classType,
         team != vInfoVO.team,
         vInfoVO.team,
         vInfoVO.isPlayer() and not self.__isSquadMode and vInfoVO.team not in defeatedTeams]
        if classType not in self.__vehicles:
            self.__vehicles[classType] = {}
        if self.__vehicles[classType].get(vInfoVO.vehicleID) != vehicleInfo:
            self.__vehicles[classType][vInfoVO.vehicleID] = vehicleInfo
            return True
        return False

    def __updateAliveStatus(self, vInfoVO):
        classType, _, _ = vInfoVO.getTypeInfo()
        vehByClassType = self.__vehicles.get(classType)
        isDead = not vInfoVO.isAlive()
        if vehByClassType and vInfoVO.vehicleID in vehByClassType:
            if vehByClassType[vInfoVO.vehicleID][0] != isDead:
                vehByClassType[vInfoVO.vehicleID][0] = isDead
                return True
            return False
        return False

    def invalidateArenaInfo(self):
        self.__updateData()
        arenaDP = self.__sessionProvider.getArenaDP()
        self.invalidateVehiclesStats(arenaDP)
        self.__isStarted = True

    def __setViewData(self, view):
        if self.__isStarted:
            view.setFrags(self.__frags, self.__attachedVehicleID == self.__sessionProvider.getArenaDP().getPlayerVehicleID())
            view.setTotalCount(self.__totalCount, self.__enemiesTeamCount + 1)
            view.setVehicles(self.__enemiesCount, self.__vehicles, self.__enemiesTeamCount)
            view.setPlayerVehicleAlive(self.__isAlive)

    def __updateData(self):
        self.__calculateVehicleCount()
        for view in self._viewComponents:
            view.setTotalCount(self.__totalCount, self.__enemiesTeamCount + 1)
            view.setVehicles(self.__enemiesCount, self.__vehicles, self.__enemiesTeamCount)

    def __updateFrags(self, arenaDP):
        self.__frags = arenaDP.getVehicleStats(self.__attachedVehicleID).frags
        playerVehicleID = arenaDP.getPlayerVehicleID()
        for view in self._viewComponents:
            view.setFrags(self.__frags, self.__attachedVehicleID == playerVehicleID)

    def __updateFriends(self):
        arenaDP = self.__sessionProvider.getArenaDP()
        for _, v in self.__vehicles.items():
            for data in v.itervalues():
                if data[3] == arenaDP.getVehicleInfo().team:
                    data[2] = False

    def __calculateVehicleCount(self):
        self.__enemiesCount = 0
        self.__enemiesTeamCount = 0
        self.__friendCount = 0
        self.__totalCount = 0
        teams = set()
        for _, v in self.__vehicles.items():
            for data in v.itervalues():
                isDead, _, isEnemy, team, isRespawn = data
                if not isDead or isRespawn:
                    if isEnemy:
                        self.__enemiesCount += 1
                    else:
                        self.__friendCount += 1
                    self.__totalCount += 1
                    teams.add(team)

        self.__friendCount -= 1
        self.__teamCount = len(teams)
        self.__enemiesTeamCount = self.__teamCount - 1
