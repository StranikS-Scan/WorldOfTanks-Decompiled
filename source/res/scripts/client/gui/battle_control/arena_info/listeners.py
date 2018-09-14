# Embedded file name: scripts/client/gui/battle_control/arena_info/listeners.py
import weakref
import operator
import BigWorld
from constants import ARENA_PERIOD
from debug_utils import LOG_DEBUG, LOG_NOTE, LOG_ERROR
from gui.battle_control.arena_info.settings import ARENA_LISTENER_SCOPE as _SCOPE
from messenger.m_constants import USER_ACTION_ID, USER_TAG
from messenger.proto.events import g_messengerEvents

class _Listener(object):
    __slots__ = ('_controllers', '_arena')

    def __init__(self):
        super(_Listener, self).__init__()
        self._arena = lambda : None
        self._controllers = set()

    def __del__(self):
        LOG_DEBUG('Deleted:', self)

    def addController(self, battleCtx, controller):
        controller.setBattleCtx(battleCtx)
        self._controllers.add(weakref.ref(controller))
        return True

    def removeController(self, controller):
        result = False
        controllerRef = weakref.ref(controller)
        if controllerRef in self._controllers:
            self._controllers.remove(controllerRef)
            result = True
        return result

    def clear(self):
        while len(self._controllers):
            ref = self._controllers.pop()
            ctrl = ref()
            if ctrl:
                ctrl.clear()

    def start(self, arena, **kwargs):
        self._arena = arena

    def stop(self):
        self.clear()
        arena = self._arena()
        self._arena = lambda : None
        return arena

    def _invokeListenersMethod(self, method, *args):
        for ref in set(self._controllers):
            controller = ref()
            if controller:
                operator.methodcaller(method, *args)(controller)


class ArenaVehiclesListener(_Listener):
    __slots__ = ('_dataProvider', '__callbackID')

    def __init__(self):
        super(ArenaVehiclesListener, self).__init__()
        self._dataProvider = None
        self.__callbackID = None
        return

    def start(self, arena, arenaDP = None):
        super(ArenaVehiclesListener, self).start(arena)
        if arenaDP is None:
            LOG_ERROR('Arena data provider is None')
            return
        else:
            arena = self._arena()
            self._dataProvider = arenaDP
            self._dataProvider.buildVehiclesData(arena.vehicles, arena.guiType)
            self._dataProvider.buildStatsData(arena.statistics)
            arena.onNewVehicleListReceived += self.__arena_onNewVehicleListReceived
            arena.onVehicleAdded += self.__arena_onVehicleAdded
            arena.onVehicleUpdated += self.__arena_onVehicleUpdated
            arena.onVehicleKilled += self.__arena_onVehicleKilled
            arena.onAvatarReady += self.__arena_onAvatarReady
            arena.onNewStatisticsReceived += self.__arena_onNewStatisticsReceived
            arena.onVehicleStatisticsUpdate += self.__arena_onVehicleStatisticsUpdate
            arena.onTeamKiller += self.__arena_onTeamKiller
            arena.onInteractiveStats += self.__arena_onInteractiveStats
            return

    def stop(self):
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        if self._dataProvider is not None:
            self._dataProvider.clear()
            self._dataProvider = None
        arena = super(ArenaVehiclesListener, self).stop()
        if arena is None:
            return
        else:
            arena.onNewVehicleListReceived -= self.__arena_onNewVehicleListReceived
            arena.onVehicleAdded -= self.__arena_onVehicleAdded
            arena.onVehicleUpdated -= self.__arena_onVehicleUpdated
            arena.onVehicleKilled -= self.__arena_onVehicleKilled
            arena.onAvatarReady -= self.__arena_onAvatarReady
            arena.onNewStatisticsReceived -= self.__arena_onNewStatisticsReceived
            arena.onVehicleStatisticsUpdate -= self.__arena_onVehicleStatisticsUpdate
            arena.onTeamKiller -= self.__arena_onTeamKiller
            arena.onInteractiveStats -= self.__arena_onInteractiveStats
            return

    def addController(self, battleCtx, controller):
        result = super(ArenaVehiclesListener, self).addController(battleCtx, controller)
        if result:
            controller.setBattleCtx(battleCtx)
            if self.__callbackID is None:
                self.__isRequiredDataExists()
        return result

    def removeController(self, controller):
        result = super(ArenaVehiclesListener, self).removeController(controller)
        if result:
            controller.setBattleCtx(None)
        return result

    def clear(self):
        while len(self._controllers):
            controller = self._controllers.pop()()
            if controller:
                controller.setBattleCtx(None)

        return

    def __arena_onNewVehicleListReceived(self):
        arena = self._arena()
        self._dataProvider.buildVehiclesData(arena.vehicles, arena.guiType)
        self._invokeListenersMethod('invalidateVehiclesInfo', self._dataProvider)

    def __arena_onVehicleAdded(self, vID):
        arena = self._arena()
        vo = self._dataProvider.addVehicleInfo(vID, arena.vehicles[vID], arena.guiType)
        self._invokeListenersMethod('addVehicleInfo', vo, self._dataProvider)

    def __arena_onVehicleUpdated(self, vID):
        flags, vo = self._dataProvider.updateVehicleInfo(vID, self._arena().vehicles[vID], self._arena().guiType)
        self._invokeListenersMethod('invalidateVehicleInfo', flags, vo, self._dataProvider)

    def __arena_onVehicleKilled(self, victimID, *args):
        flags, vo = self._dataProvider.updateVehicleStatus(victimID, self._arena().vehicles[victimID])
        self._invokeListenersMethod('invalidateVehicleStatus', flags, vo, self._dataProvider)

    def __arena_onAvatarReady(self, vID):
        flags, vo = self._dataProvider.updateVehicleStatus(vID, self._arena().vehicles[vID])
        self._invokeListenersMethod('invalidateVehicleStatus', flags, vo, self._dataProvider)

    def __arena_onNewStatisticsReceived(self):
        self._dataProvider.buildStatsData(self._arena().statistics)
        self._invokeListenersMethod('invalidateStats', self._dataProvider)

    def __arena_onVehicleStatisticsUpdate(self, vID):
        flags, vo = self._dataProvider.updateVehicleStats(vID, self._arena().statistics[vID])
        self._invokeListenersMethod('invalidateVehicleStats', flags, vo, self._dataProvider)

    def __arena_onTeamKiller(self, vID):
        flags, vo = self._dataProvider.updatePlayerStatus(vID, self._arena().vehicles[vID])
        self._invokeListenersMethod('invalidatePlayerStatus', flags, vo, self._dataProvider)

    def __arena_onInteractiveStats(self, stats):
        self._dataProvider.updateVehicleInteractiveStats(stats)
        self._invokeListenersMethod('invalidateVehicleInteractiveStats')

    def __isRequiredDataExists(self):
        self.__callbackID = None
        if self._dataProvider is not None and self._dataProvider.isRequiredDataExists():
            self._invokeListenersMethod('invalidateArenaInfo')
        else:
            self.__callbackID = BigWorld.callback(0.1, self.__isRequiredDataExists)
        return


_TAGS_TO_UPDATE = {USER_TAG.FRIEND, USER_TAG.IGNORED, USER_TAG.MUTED}

class ContactsListener(_Listener):

    def start(self, arena, **kwargs):
        super(ContactsListener, self).start(arena)
        g_messengerEvents.users.onUsersListReceived += self.__me_onUsersListReceived
        g_messengerEvents.users.onUserActionReceived += self.__me_onUserActionReceived

    def stop(self):
        g_messengerEvents.users.onUsersListReceived -= self.__me_onUsersListReceived
        g_messengerEvents.users.onUserActionReceived -= self.__me_onUserActionReceived
        super(ContactsListener, self).stop()

    def __me_onUsersListReceived(self, tags):
        if _TAGS_TO_UPDATE & tags:
            self._invokeListenersMethod('invalidateUsersTags')

    def __me_onUserActionReceived(self, actionID, user):
        if actionID in (USER_ACTION_ID.FRIEND_ADDED,
         USER_ACTION_ID.FRIEND_REMOVED,
         USER_ACTION_ID.IGNORED_ADDED,
         USER_ACTION_ID.IGNORED_REMOVED,
         USER_ACTION_ID.MUTE_SET,
         USER_ACTION_ID.MUTE_UNSET):
            self._invokeListenersMethod('invalidateUserTags', user)


class ArenaSpaceLoadListener(_Listener):
    MAX_PROGRESS_VALUE = 1.0
    SPACE_INVALIDATION_PERIOD = 0.5
    INFLUX_INVALIDATION_PERIOD = 0.5

    def __init__(self):
        super(ArenaSpaceLoadListener, self).__init__()
        self.__progress = 0.0
        self.__spaceLoadCB = None
        self.__influxDrawCB = None
        return

    def start(self, arena, **kwargs):
        super(ArenaSpaceLoadListener, self).start(arena)
        self.__onSpaceLoadStarted()
        self.__loadSpaceCallback()

    def stop(self):
        self.__clearSpaceCallback()
        self.__clearInfluxCallback()
        super(ArenaSpaceLoadListener, self).stop()

    def __loadSpaceCallback(self):
        self.__clearSpaceCallback()
        progress = 1.0
        import BattleReplay
        if not BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            progress = BigWorld.spaceLoadStatus()
        if progress > self.__progress:
            self.__progress = progress
            self.__onSpaceLoadUpdated(progress)
        if progress < self.MAX_PROGRESS_VALUE:
            self.__spaceLoadCB = BigWorld.callback(self.SPACE_INVALIDATION_PERIOD, self.__loadSpaceCallback)
            BigWorld.SetDrawInflux(False)
        else:
            self.__onSpaceLoadCompleted()
            BigWorld.SetDrawInflux(True)
            self.__loadInfluxCallback()

    def __loadInfluxCallback(self):
        self.__clearInfluxCallback()
        if BigWorld.worldDrawEnabled():
            self.__onArenaLoadCompleted()
        else:
            self.__influxDrawCB = BigWorld.callback(self.SPACE_INVALIDATION_PERIOD, self.__loadInfluxCallback)

    def __clearSpaceCallback(self):
        if self.__spaceLoadCB is not None:
            BigWorld.cancelCallback(self.__spaceLoadCB)
            self.__spaceLoadCB = None
        return

    def __clearInfluxCallback(self):
        if self.__influxDrawCB is not None:
            BigWorld.cancelCallback(self.__influxDrawCB)
            self.__influxDrawCB = None
        return

    def __onSpaceLoadUpdated(self, progress):
        self._invokeListenersMethod('updateSpaceLoadProgress', progress)

    def __onSpaceLoadStarted(self):
        self._invokeListenersMethod('spaceLoadStarted')

    def __onSpaceLoadCompleted(self):
        self._invokeListenersMethod('spaceLoadCompleted')

    def __onArenaLoadCompleted(self):
        self._invokeListenersMethod('arenaLoadCompleted')


class ArenaTeamBasesListener(_Listener):
    __slots__ = ('__baseIDs', '__points')

    def __init__(self):
        super(ArenaTeamBasesListener, self).__init__()

    def start(self, arena, **kwargs):
        super(ArenaTeamBasesListener, self).start(arena, **kwargs)
        arena = self._arena()
        arena.onTeamBasePointsUpdate += self.__arena_onTeamBasePointsUpdate
        arena.onTeamBaseCaptured += self.__arena_onTeamBaseCaptured
        arena.onPeriodChange += self.__arena_onPeriodChange

    def stop(self):
        arena = super(ArenaTeamBasesListener, self).stop()
        if arena is None:
            return
        else:
            arena.onTeamBasePointsUpdate -= self.__arena_onTeamBasePointsUpdate
            arena.onTeamBaseCaptured -= self.__arena_onTeamBaseCaptured
            arena.onPeriodChange -= self.__arena_onPeriodChange
            return

    def __arena_onTeamBasePointsUpdate(self, team, baseID, points, capturingStopped):
        self._invokeListenersMethod('invalidateTeamBasePoints', team, baseID, points, capturingStopped)

    def __arena_onTeamBaseCaptured(self, team, baseID):
        self._invokeListenersMethod('invalidateTeamBaseCaptured', team, baseID)

    def __arena_onPeriodChange(self, period, *args):
        if period == ARENA_PERIOD.AFTERBATTLE:
            self._invokeListenersMethod('removeTeamsBases')


class ArenaPeriodListener(_Listener):

    def start(self, arena, **kwargs):
        super(ArenaPeriodListener, self).start(arena, **kwargs)
        arena = self._arena()
        self._invokeListenersMethod('setPeriodInfo', arena.period, arena.periodEndTime, arena.periodLength, arena.arenaType.battleCountdownTimerSound)
        arena.onPeriodChange += self.__arena_onPeriodChange

    def stop(self):
        arena = super(ArenaPeriodListener, self).stop()
        if arena is None:
            return
        else:
            arena.onPeriodChange -= self.__arena_onPeriodChange
            return

    def __arena_onPeriodChange(self, period, endTime, length, *args):
        self._invokeListenersMethod('invalidatePeriodInfo', period, endTime, length)


class ArenaRespawnListener(_Listener):

    def start(self, arena, **kwargs):
        super(ArenaRespawnListener, self).start(arena, **kwargs)
        arena = self._arena()
        arena.onRespawnAvailableVehicles += self.__arena_onRespawnAvailableVehicles
        arena.onRespawnCooldowns += self.__arena_onRespawnCooldowns
        arena.onRespawnRandomVehicle += self.__arena_onRespawnRandomVehicle
        arena.onRespawnResurrected += self.__arena_onRespawnResurrected

    def stop(self):
        arena = super(ArenaRespawnListener, self).stop()
        if arena is None:
            return
        else:
            arena.onRespawnAvailableVehicles -= self.__arena_onRespawnAvailableVehicles
            arena.onRespawnCooldowns -= self.__arena_onRespawnCooldowns
            arena.onRespawnRandomVehicle -= self.__arena_onRespawnRandomVehicle
            arena.onRespawnResurrected -= self.__arena_onRespawnResurrected
            return

    def __arena_onRespawnAvailableVehicles(self, vehsList):
        self._invokeListenersMethod('updateRespawnVehicles', vehsList)

    def __arena_onRespawnCooldowns(self, cooldowns):
        self._invokeListenersMethod('updateRespawnCooldowns', cooldowns)

    def __arena_onRespawnRandomVehicle(self, respawnInfo):
        self._invokeListenersMethod('updateRespawnInfo', respawnInfo)

    def __arena_onRespawnResurrected(self, respawnInfo):
        self._invokeListenersMethod('updateRespawnRessurectedInfo', respawnInfo)


class ListenersCollection(_Listener):
    __slots__ = ('__vehicles', '__teamsBases', '__loader', '__contacts', '__period', '__respawn')

    def __init__(self):
        super(ListenersCollection, self).__init__()
        self.__vehicles = ArenaVehiclesListener()
        self.__teamsBases = ArenaTeamBasesListener()
        self.__contacts = ContactsListener()
        self.__loader = ArenaSpaceLoadListener()
        self.__period = ArenaPeriodListener()
        self.__respawn = ArenaRespawnListener()

    def addController(self, battleCtx, controller):
        result = False
        try:
            scope = controller.getCtrlScope()
        except AttributeError:
            LOG_ERROR('Controller is not valid', controller)
            return False

        if scope & _SCOPE.LOAD > 0:
            result |= self.__loader.addController(battleCtx, controller)
        if scope & _SCOPE.VEHICLES > 0:
            result |= self.__vehicles.addController(battleCtx, controller)
            result |= self.__contacts.addController(battleCtx, controller)
        if scope & _SCOPE.PERIOD > 0:
            result |= self.__period.addController(battleCtx, controller)
        if scope & _SCOPE.TEAMS_BASES > 0:
            result |= self.__teamsBases.addController(battleCtx, controller)
        if scope & _SCOPE.RESPAWN > 0:
            result |= self.__respawn.addController(battleCtx, controller)
        return result

    def removeController(self, controller):
        result = self.__vehicles.removeController(controller)
        result |= self.__teamsBases.removeController(controller)
        result |= self.__contacts.removeController(controller)
        result |= self.__loader.removeController(controller)
        result |= self.__period.removeController(controller)
        result |= self.__respawn.removeController(controller)
        return result

    def start(self, arena, **kwargs):
        if arena is None:
            LOG_NOTE('ClientArena is not found')
            return
        else:
            ref = weakref.ref(arena)
            self.__vehicles.start(ref, **kwargs)
            self.__teamsBases.start(ref, **kwargs)
            self.__contacts.start(ref, **kwargs)
            self.__loader.start(ref, **kwargs)
            self.__period.start(ref, **kwargs)
            self.__respawn.start(ref, **kwargs)
            return

    def stop(self):
        self.__vehicles.stop()
        self.__teamsBases.stop()
        self.__contacts.stop()
        self.__loader.stop()
        self.__period.stop()
        self.__respawn.stop()

    def clear(self):
        self.__vehicles.clear()
        self.__teamsBases.clear()
        self.__contacts.clear()
        self.__loader.clear()
        self.__period.clear()
        self.__respawn.clear()
