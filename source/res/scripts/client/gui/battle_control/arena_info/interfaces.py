# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/arena_info/interfaces.py
from gui.battle_control.arena_info.settings import ARENA_LISTENER_SCOPE as _SCOPE
from gui.battle_control.controllers.interfaces import IBattleController

class IArenaController(IBattleController):
    __slots__ = ('__weakref__',)

    def getControllerID(self):
        pass

    def getCtrlScope(self):
        raise NotImplementedError('Routine "getCtrlScope" must be implemented')

    def startControl(self, battleCtx, arenaVisitor):
        pass

    def stopControl(self):
        pass


class IArenaLoadController(IArenaController):
    __slots__ = ()

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


class IContactsController(IArenaController):
    __slots__ = ()

    def getCtrlScope(self):
        return _SCOPE.CONTACTS

    def invalidateUsersTags(self):
        pass

    def invalidateUserTags(self, user):
        pass


class IArenaVehiclesController(IArenaLoadController, IContactsController):
    __slots__ = ()

    def getCtrlScope(self):
        return _SCOPE.VEHICLES | _SCOPE.LOAD | _SCOPE.CONTACTS

    def invalidateArenaInfo(self):
        pass

    def invalidateVehiclesInfo(self, arenaDP):
        pass

    def invalidateVehiclesStats(self, arenaDP):
        pass

    def updateVehiclesStats(self, updated, arenaDP):
        pass

    def addVehicleInfo(self, vo, arenaDP):
        pass

    def updateVehiclesInfo(self, updated, arenaDP):
        pass

    def invalidateVehicleStatus(self, flags, vo, arenaDP):
        pass

    def invalidatePlayerStatus(self, flags, vo, arenaDP):
        pass

    def invalidateFogOfWarHiddenVehiclesFlag(self, flag):
        pass


class ITeamsBasesController(IArenaController):
    __slots__ = ()

    def getCtrlScope(self):
        return _SCOPE.TEAMS_BASES

    def invalidateTeamBasePoints(self, baseTeam, baseID, points, timeLeft, invadersCnt, capturingStopped):
        pass

    def invalidateTeamBaseCaptured(self, baseTeam, baseID):
        pass

    def removeTeamsBases(self):
        pass


class IArenaPeriodController(IArenaController):
    __slots__ = ()

    def getCtrlScope(self):
        return _SCOPE.PERIOD

    def setPeriodInfo(self, period, endTime, length, additionalInfo, soundID):
        pass

    def invalidatePeriodInfo(self, period, endTime, length, additionalInfo):
        pass


class IPersonalInvitationsController(IArenaController):
    __slots__ = ()

    def getCtrlScope(self):
        return _SCOPE.INVITATIONS

    def invalidateInvitationsStatuses(self, vos, arenaDP):
        pass


class IVehiclesAndPersonalInvitationsController(IArenaVehiclesController, IPersonalInvitationsController):
    __slots__ = ()

    def getCtrlScope(self):
        return _SCOPE.VEHICLES | _SCOPE.INVITATIONS | _SCOPE.CONTACTS


class IVehiclesAndPositionsController(IArenaVehiclesController):
    __slots__ = ()

    def getCtrlScope(self):
        return _SCOPE.VEHICLES | _SCOPE.POSITIONS

    def updatePositions(self, iterator):
        pass


class IBattleFieldController(IArenaVehiclesController):
    __slots__ = ()

    def setVehicleHealth(self, vehicleID, newHealth):
        pass

    def setVehicleVisible(self, vehicleID, health):
        pass


class IContactsAndPersonalInvitationsController(IContactsController, IPersonalInvitationsController):
    __slots__ = ()

    def getCtrlScope(self):
        return _SCOPE.CONTACTS | _SCOPE.INVITATIONS


class IViewPointsController(IArenaLoadController):
    __slots__ = ()

    def getCtrlScope(self):
        return _SCOPE.LOAD | _SCOPE.VIEW_POINTS

    def updateViewPoints(self, viewPoints):
        pass

    def updateAttachedVehicle(self, vehicleID):
        pass
