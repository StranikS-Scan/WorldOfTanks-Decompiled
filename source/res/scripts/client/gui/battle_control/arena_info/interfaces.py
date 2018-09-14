# Embedded file name: scripts/client/gui/battle_control/arena_info/interfaces.py
from gui.battle_control.arena_info.settings import ARENA_LISTENER_SCOPE as _SCOPE

class IArenaController(object):
    __slots__ = ('__weakref__',)

    def getCtrlScope(self):
        raise NotImplementedError, 'Routine "getCtrlScope" must be implemented'

    def clear(self):
        pass

    def setBattleCtx(self, battleCtx):
        pass

    def setUI(self, *args):
        pass

    def clearUI(self):
        pass


class IArenaLoadController(IArenaController):

    def getCtrlScope(self):
        return _SCOPE.LOAD

    def spaceLoadStarted(self):
        pass

    def spaceLoadCompleted(self):
        pass

    def updateSpaceLoadProgress(self, progress):
        pass

    def arenaLoadCompleted(self):
        pass


class IArenaVehiclesController(IArenaLoadController):

    def getCtrlScope(self):
        return _SCOPE.VEHICLES | _SCOPE.LOAD

    def invalidateArenaInfo(self):
        pass

    def invalidateVehiclesInfo(self, arenaDP):
        pass

    def invalidateStats(self, arenaDP):
        pass

    def addVehicleInfo(self, vo, arenaDP):
        pass

    def invalidateVehicleInfo(self, flags, vo, arenaDP):
        pass

    def invalidateVehicleStatus(self, flags, vo, arenaDP):
        pass

    def invalidateVehicleStats(self, flags, vo, arenaDP):
        pass

    def invalidatePlayerStatus(self, flags, vo, arenaDP):
        pass

    def invalidateUsersTags(self):
        pass

    def invalidateUserTags(self, user):
        pass

    def invalidateVehicleInteractiveStats(self):
        pass


class ITeamsBasesController(IArenaController):

    def getCtrlScope(self):
        return _SCOPE.TEAMS_BASES

    def invalidateTeamBasePoints(self, baseTeam, baseID, points, capturingStopped):
        pass

    def invalidateTeamBaseCaptured(self, baseTeam, baseID):
        pass

    def removeTeamsBases(self):
        pass


class IArenaPeriodController(IArenaController):

    def getCtrlScope(self):
        return _SCOPE.PERIOD

    def setPeriodInfo(self, period, endTime, length, soundID):
        pass

    def invalidatePeriodInfo(self, period, endTime, length):
        pass


class IArenaRespawnController(IArenaController):

    def getCtrlScope(self):
        return _SCOPE.RESPAWN

    def updateSpaceLoadProgress(self, progress):
        pass

    def arenaLoadCompleted(self):
        pass

    def updateRespawnVehicles(self, vehsList):
        pass

    def updateRespawnCooldowns(self, cooldowns):
        pass

    def updateRespawnInfo(self, respawnInfo):
        pass

    def updateRespawnRessurectedInfo(self, respawnInfo):
        pass
