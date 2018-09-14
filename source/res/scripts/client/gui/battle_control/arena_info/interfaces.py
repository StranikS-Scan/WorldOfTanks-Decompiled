# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/arena_info/interfaces.py
from gui.battle_control.arena_info.settings import ARENA_LISTENER_SCOPE as _SCOPE
from gui.battle_control.controllers.interfaces import IBattleController

class IArenaController(IBattleController):
    """Interface of GUI controller to displays information of vehicles in
    each team on arena.
    """
    __slots__ = ('__weakref__',)

    def getControllerID(self):
        pass

    def getCtrlScope(self):
        raise NotImplementedError('Routine "getCtrlScope" must be implemented')

    def startControl(self, battleCtx, arenaVisitor):
        """Starts and sets battle context.
        :param battleCtx: instance of BattleContext.
        :param arenaVisitor: instance of _ClientArenaVisitor.
        """
        pass

    def stopControl(self):
        pass


class IArenaLoadController(IArenaController):
    __slots__ = ()

    def getCtrlScope(self):
        return _SCOPE.LOAD

    def spaceLoadStarted(self):
        """Arena space loading started."""
        pass

    def spaceLoadCompleted(self):
        """Arena space loading completed."""
        pass

    def updateSpaceLoadProgress(self, progress):
        """Arena space loading progress has been changed
        @param progress: [float] progress value
        :param progress:
        """
        pass

    def arenaLoadCompleted(self):
        """Arena space loading completed and influx draw enabled. This event
        means arena is ready to be shown.
        """
        pass


class IContactsController(IArenaController):
    __slots__ = ()

    def getCtrlScope(self):
        return _SCOPE.CONTACTS

    def invalidateUsersTags(self):
        """New list of chat rosters has been received."""
        pass

    def invalidateUserTags(self, user):
        """Chat rosters has been changed.
        :param user: instance of UserEntity.
        """
        pass


class IArenaVehiclesController(IArenaLoadController, IContactsController):
    __slots__ = ()

    def getCtrlScope(self):
        return _SCOPE.VEHICLES | _SCOPE.LOAD | _SCOPE.CONTACTS

    def invalidateArenaInfo(self):
        """Starts to invalidate information of arena."""
        pass

    def invalidateVehiclesInfo(self, arenaDP):
        """New list of vehicles has been received.
        :param arenaDP: instance of ArenaDataProvider.
        """
        pass

    def invalidateVehiclesStats(self, arenaDP):
        """New statistics data related to vehicles has been received.
        :param arenaDP: instance of ArenaDataProvider.
        """
        pass

    def updateVehiclesStats(self, updated, arenaDP):
        """Statistics of vehicle has been updated on arena.
        Updates required player's panel, frags panel.
        :param updated: [(flags, VehicleArenaStatsVO), ...].
        :param arenaDP: instance of ArenaDataProvider.
        """
        pass

    def addVehicleInfo(self, vo, arenaDP):
        """New vehicle added to arena.
        :param vo: instance of VehicleArenaInfoVO that has been added.
        :param arenaDP: instance of ArenaDataProvider.
        """
        pass

    def updateVehiclesInfo(self, updated, arenaDP):
        """Vehicle has been updated on arena.
        :param updated: container of VOs which have been changed, where first element belongs to updated vehicle
        :param arenaDP: instance of ArenaDataProvider.
        """
        pass

    def invalidateVehicleStatus(self, flags, vo, arenaDP):
        """Status of vehicle (isReady, isAlive, ...) has been updated on arena.
        :param flags: bitmask containing values from INVALIDATE_OP.
        :param vo: instance of VehicleArenaInfoVO for that status is updated.
        :param arenaDP: instance of ArenaDataProvider.
        """
        pass

    def invalidatePlayerStatus(self, flags, vo, arenaDP):
        """Status of player (isTeamKiller, ...) has been updated on arena.
        :param flags: bitmask containing values from INVALIDATE_OP.
        :param vo: instance of VehicleArenaInfoVO for that status updated.
        :param arenaDP: instance of ArenaDataProvider.
        """
        pass


class ITeamsBasesController(IArenaController):
    __slots__ = ()

    def getCtrlScope(self):
        return _SCOPE.TEAMS_BASES

    def invalidateTeamBasePoints(self, baseTeam, baseID, points, timeLeft, invadersCnt, capturingStopped):
        """
        Adds/Updates indicator for base that is capturing in UI.
        :param baseTeam: number of base's team.
        :param baseID: integer containing unique ID of base.
        :param points: integer containing value of points (0 ... 100).
        :param timeLeft: time left until base will be captured
        :param invadersCnt: count of invaders
        :param capturingStopped: is capture stopped.
        :return:
        """
        pass

    def invalidateTeamBaseCaptured(self, baseTeam, baseID):
        """Team base has been captured.
        :param baseTeam: number of base's team.
        :param baseID: integer containing unique ID of base.
        """
        pass

    def removeTeamsBases(self):
        """Removes all teams bases."""
        pass


class IArenaPeriodController(IArenaController):
    __slots__ = ()

    def getCtrlScope(self):
        return _SCOPE.PERIOD

    def setPeriodInfo(self, period, endTime, length, additionalInfo, soundID):
        """Sets current time metrics that takes from the ClientArena.
        :param period: integer containing one of the ARENA_PERIOD.* values.
        :param endTime: float containing server time of the period end.
        :param length: float containing period length.
        :param additionalInfo: arena additional info, @see ClientArena.
        :param soundID: string containing path to the sound of countdown timer.
        """
        pass

    def invalidatePeriodInfo(self, period, endTime, length, additionalInfo):
        """Time metrics has been updated by server.
        :param period: integer containing one of the ARENA_PERIOD.* values.
        :param endTime: float containing server time of the period end.
        :param length: float containing period length.
        :param additionalInfo: PeriodAdditionalInfo
        """
        pass


class IArenaRespawnController(IArenaController):
    __slots__ = ()

    def getCtrlScope(self):
        return _SCOPE.RESPAWN

    def updateSpaceLoadProgress(self, progress):
        """Arena space loading progress has been changed.
        :param progress: [float] progress value.
        """
        pass

    def arenaLoadCompleted(self):
        """Arena space loading completed and influx draw enabled. This event
        means arena is ready to be shown.
        """
        pass

    def updateRespawnVehicles(self, vehsList):
        """Arena received list of vehicles, available for respawns.
        :param vehsList: list of vehicles.
        """
        pass

    def updateRespawnCooldowns(self, cooldowns):
        """Arena received list of cooldowns for respawns.
        :param cooldowns: list of cooldowns
        """
        pass

    def updateRespawnInfo(self, respawnInfo):
        """Arena received respawn info.
        :param respawnInfo:
        """
        pass

    def updateRespawnRessurectedInfo(self, respawnInfo):
        """Arena received respawn ressurected info.
        :param respawnInfo:
        """
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


class IContactsAndPersonalInvitationsController(IContactsController, IPersonalInvitationsController):
    __slots__ = ()

    def getCtrlScope(self):
        return _SCOPE.CONTACTS | _SCOPE.INVITATIONS
