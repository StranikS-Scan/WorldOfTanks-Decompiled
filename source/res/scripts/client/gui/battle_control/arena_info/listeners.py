# Embedded file name: scripts/client/gui/battle_control/arena_info/listeners.py
import weakref
import BigWorld
from debug_utils import LOG_DEBUG, LOG_NOTE, LOG_ERROR
from gui.battle_control.arena_info import getClientArena
from gui.battle_control.arena_info import IArenaController
from messenger.m_constants import USER_ACTION_ID, USER_TAG
from messenger.proto.events import g_messengerEvents

class _Listener(object):

    def __init__(self):
        super(_Listener, self).__init__()
        self._controllers = set()

    def __del__(self):
        LOG_DEBUG('Deleted:', self)

    def addController(self, battleCtx, controller):
        result = True
        if isinstance(controller, IArenaController):
            controllerRef = weakref.ref(controller)
            self._controllers.add(controllerRef)
        else:
            LOG_ERROR('Object is not extend IArenaController', controller)
            result = False
        return result

    def removeController(self, controller):
        result = False
        controllerRef = weakref.ref(controller)
        if controllerRef in self._controllers:
            self._controllers.remove(controllerRef)
            result = True
        return result

    def clear(self):
        while len(self._controllers):
            self._controllers.pop()

    def start(self, **kwargs):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def _invokeListenersMethod(self, method, *args):
        for ref in set(self._controllers):
            controller = ref()
            if controller:
                getattr(controller, method)(*args)


class ArenaListener(_Listener):

    def __init__(self):
        super(ArenaListener, self).__init__()
        self._dataProvider = None
        self._controller = lambda : None
        self._arena = lambda : None
        self.__callbackID = None
        return

    def start(self, arenaDP = None):
        if arenaDP is None:
            LOG_ERROR('Arena data provider is None')
            return
        else:
            self._dataProvider = arenaDP
            arena = getClientArena()
            if arena is None:
                LOG_NOTE('Arena not found')
                return
            self._arena = weakref.ref(arena)
            self._dataProvider.buildVehiclesData(self._arena().vehicles, self._arena().guiType)
            self._dataProvider.buildStatsData(self._arena().statistics)
            arena.onNewVehicleListReceived += self.__arena_onNewVehicleListReceived
            arena.onVehicleAdded += self.__arena_onVehicleAdded
            arena.onVehicleUpdated += self.__arena_onVehicleUpdated
            arena.onVehicleKilled += self.__arena_onVehicleKilled
            arena.onAvatarReady += self.__arena_onAvatarReady
            arena.onNewStatisticsReceived += self.__arena_onNewStatisticsReceived
            arena.onVehicleStatisticsUpdate += self.__arena_onVehicleStatisticsUpdate
            arena.onTeamKiller += self.__arena_onTeamKiller
            arena.onRespawnAvailableVehicles += self.__arena_onRespawnAvailableVehicles
            arena.onRespawnCooldowns += self.__arena_onRespawnCooldowns
            arena.onRespawnRandomVehicle += self.__arena_onRespawnRandomVehicle
            arena.onRespawnResurrected += self.__arena_onRespawnResurrected
            arena.onInteractiveStats += self.__arena_onInteractiveStats
            return

    def stop(self):
        self.clear()
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        if self._dataProvider is not None:
            self._dataProvider.clear()
            self._dataProvider = None
        arena = self._arena()
        self._arena = lambda : None
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
            arena.onRespawnAvailableVehicles -= self.__arena_onRespawnAvailableVehicles
            arena.onRespawnCooldowns -= self.__arena_onRespawnCooldowns
            arena.onRespawnRandomVehicle -= self.__arena_onRespawnRandomVehicle
            arena.onRespawnResurrected -= self.__arena_onRespawnResurrected
            arena.onInteractiveStats -= self.__arena_onInteractiveStats
            return

    def addController(self, battleCtx, controller):
        result = super(ArenaListener, self).addController(battleCtx, controller)
        if result:
            controller.setBattleCtx(battleCtx)
            if self.__callbackID is None:
                self.__isRequiredDataExists()
        return result

    def removeController(self, controller):
        result = super(ArenaListener, self).removeController(controller)
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

    def __arena_onVehicleKilled(self, victimID, killerID, reason):
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

    def __arena_onRespawnAvailableVehicles(self, vehsList):
        self._invokeListenersMethod('updateRespawnVehicles', vehsList)

    def __arena_onRespawnCooldowns(self, cooldowns):
        self._invokeListenersMethod('updateRespawnCooldowns', cooldowns)

    def __arena_onRespawnRandomVehicle(self, respawnInfo):
        self._invokeListenersMethod('updateRespawnInfo', respawnInfo)

    def __arena_onRespawnResurrected(self, respawnInfo):
        self._invokeListenersMethod('updateRespawnRessurectedInfo', respawnInfo)

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

class UsersListListener(_Listener):

    def start(self, **kwargs):
        g_messengerEvents.users.onUsersListReceived += self.__me_onUsersListReceived
        g_messengerEvents.users.onUserActionReceived += self.__me_onUserActionReceived

    def stop(self):
        g_messengerEvents.users.onUsersListReceived -= self.__me_onUsersListReceived
        g_messengerEvents.users.onUserActionReceived -= self.__me_onUserActionReceived
        self.clear()

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

    def start(self, **kwargs):
        self.__onSpaceLoadStarted()
        self.__loadSpaceCallback()

    def stop(self):
        self.__clearSpaceCallback()
        self.__clearInfluxCallback()
        self.clear()

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


class ListenersCollection(_Listener):
    __slots__ = ('__arenaListener', '__usersListListener', '__arenaLoadListener')

    def __init__(self):
        super(ListenersCollection, self).__init__()
        self.__arenaListener = ArenaListener()
        self.__usersListListener = UsersListListener()
        self.__arenaLoadListener = ArenaSpaceLoadListener()

    def addController(self, battleCtx, controller):
        return self.__arenaListener.addController(battleCtx, controller) and self.__usersListListener.addController(battleCtx, controller) and self.__arenaLoadListener.addController(battleCtx, controller)

    def removeController(self, controller):
        result = self.__arenaListener.removeController(controller)
        result |= self.__usersListListener.removeController(controller)
        result |= self.__arenaLoadListener.removeController(controller)
        return result

    def start(self, **kwargs):
        self.__arenaListener.start(**kwargs)
        self.__usersListListener.start(**kwargs)
        self.__arenaLoadListener.start(**kwargs)

    def stop(self):
        self.__arenaListener.stop()
        self.__usersListListener.stop()
        self.__arenaLoadListener.stop()

    def clear(self):
        self.__arenaListener.clear()
        self.__usersListListener.clear()
        self.__arenaLoadListener.clear()
