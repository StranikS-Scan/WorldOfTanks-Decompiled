# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/arena_info/listeners.py
import weakref
import operator
from collections import namedtuple
import BigWorld
from constants import ARENA_PERIOD, FINISH_REASON
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui.battle_control.arena_info.invitations import SquadInvitationsFilter
from gui.battle_control.battle_constants import WinStatus
from gui.battle_control.arena_info.settings import ARENA_LISTENER_SCOPE as _SCOPE
from gui.battle_control.arena_info.settings import INVALIDATE_OP
from gui.prb_control import prbInvitesProperty
from messenger.m_constants import USER_ACTION_ID, USER_TAG
from messenger.proto.events import g_messengerEvents

class _PeriodAdditionalInfo(namedtuple('_PeriodAdditionalInfo', ['winStatus', 'winnerTeam', 'finishReason'])):

    def getWinnerTeam(self):
        return self.winnerTeam

    def getWinStatus(self):
        return self.winStatus

    def isExtermination(self):
        return self.finishReason == FINISH_REASON.EXTERMINATION


def _getPeriodAdditionalInfo(arenaDP, period, additionalInfo):
    if period == ARENA_PERIOD.AFTERBATTLE:
        winnerTeam, finishReason = additionalInfo
        return _PeriodAdditionalInfo(WinStatus.fromWinnerTeam(winnerTeam, arenaDP.isAllyTeam(winnerTeam)), winnerTeam, finishReason)
    else:
        return None


class _Listener(object):
    __slots__ = ('_controllers', '_visitor', '_arenaDP')

    def __init__(self):
        super(_Listener, self).__init__()
        self._visitor = None
        self._arenaDP = None
        self._controllers = set()
        return

    def __del__(self):
        LOG_DEBUG('Deleted:', self)

    def addController(self, controller):
        self._controllers.add(weakref.ref(controller))
        return True

    def removeController(self, controller):
        result = False
        ref = weakref.ref(controller)
        if ref in self._controllers:
            self._controllers.remove(ref)
            ctrl = ref()
            if ctrl is not None:
                ctrl.stopControl()
            result = True
        return result

    def clear(self):
        while len(self._controllers):
            ref = self._controllers.pop()
            ctrl = ref()
            if ctrl is not None:
                ctrl.stopControl()

        return

    def start(self, setup):
        self._visitor = weakref.proxy(setup.arenaVisitor)
        self._arenaDP = weakref.proxy(setup.arenaDP)

    def stop(self):
        self._visitor = None
        self._arenaDP = None
        self.clear()
        return

    def _invokeListenersMethod(self, method, *args):
        caller = operator.methodcaller(method, *args)
        for ref in set(self._controllers):
            controller = ref()
            if controller is not None:
                caller(controller)

        return


class ArenaVehiclesListener(_Listener):
    """Listener of vehicles on the arena"""
    __slots__ = ('__callbackID',)

    def __init__(self):
        super(ArenaVehiclesListener, self).__init__()
        self.__callbackID = None
        return

    def start(self, setup):
        super(ArenaVehiclesListener, self).start(setup)
        self._arenaDP.buildVehiclesData(self._visitor.getArenaVehicles())
        self._arenaDP.buildStatsData(self._visitor.getArenaStatistics())
        arena = self._visitor.getArenaSubscription()
        if arena is not None:
            arena.onNewVehicleListReceived += self.__arena_onNewVehicleListReceived
            arena.onVehicleAdded += self.__arena_onVehicleAdded
            arena.onVehicleUpdated += self.__arena_onVehicleUpdated
            arena.onVehicleKilled += self.__arena_onVehicleKilled
            arena.onAvatarReady += self.__arena_onAvatarReady
            arena.onNewStatisticsReceived += self.__arena_onNewStatisticsReceived
            arena.onVehicleStatisticsUpdate += self.__arena_onVehicleStatisticsUpdate
            arena.onTeamKiller += self.__arena_onTeamKiller
            arena.onInteractiveStats += self.__arena_onInteractiveStats
            arena.onGameModeSpecifcStats += self.__arena_onGameModeSpecifcStats
        return

    def stop(self):
        self.__clearCallback()
        arena = self._visitor.getArenaSubscription()
        if arena is not None:
            arena.onNewVehicleListReceived -= self.__arena_onNewVehicleListReceived
            arena.onVehicleAdded -= self.__arena_onVehicleAdded
            arena.onVehicleUpdated -= self.__arena_onVehicleUpdated
            arena.onVehicleKilled -= self.__arena_onVehicleKilled
            arena.onAvatarReady -= self.__arena_onAvatarReady
            arena.onNewStatisticsReceived -= self.__arena_onNewStatisticsReceived
            arena.onVehicleStatisticsUpdate -= self.__arena_onVehicleStatisticsUpdate
            arena.onTeamKiller -= self.__arena_onTeamKiller
            arena.onInteractiveStats -= self.__arena_onInteractiveStats
            arena.onGameModeSpecifcStats -= self.__arena_onGameModeSpecifcStats
        super(ArenaVehiclesListener, self).stop()
        return

    def addController(self, controller):
        result = super(ArenaVehiclesListener, self).addController(controller)
        if result:
            if self.__isRequiredDataExists():
                if self.__callbackID is not None:
                    self.__clearCallback()
                    self._invokeListenersMethod('invalidateArenaInfo')
                else:
                    controller.invalidateArenaInfo()
            elif self.__callbackID is None:
                self.__setCallback()
        return result

    def __arena_onNewVehicleListReceived(self):
        self._arenaDP.buildVehiclesData(self._visitor.getArenaVehicles())
        self._invokeListenersMethod('invalidateVehiclesInfo', self._arenaDP)

    def __arena_onVehicleAdded(self, vehicleID):
        added, updated = self._arenaDP.addVehicleInfo(vehicleID, self._visitor.vehicles.getVehicleInfo(vehicleID))
        if added is not None:
            self._invokeListenersMethod('addVehicleInfo', added, self._arenaDP)
        if updated:
            self._invokeListenersMethod('updateVehiclesInfo', updated, self._arenaDP)
        return

    def __arena_onVehicleUpdated(self, vehicleID):
        updated = self._arenaDP.updateVehicleInfo(vehicleID, self._visitor.vehicles.getVehicleInfo(vehicleID))
        if updated:
            self._invokeListenersMethod('updateVehiclesInfo', updated, self._arenaDP)

    def __arena_onVehicleKilled(self, victimID, *args):
        flags, vo = self._arenaDP.updateVehicleStatus(victimID, self._visitor.vehicles.getVehicleInfo(victimID))
        if flags != INVALIDATE_OP.NONE:
            self._invokeListenersMethod('invalidateVehicleStatus', flags, vo, self._arenaDP)

    def __arena_onAvatarReady(self, vehicleID):
        flags, vo = self._arenaDP.updateVehicleStatus(vehicleID, self._visitor.vehicles.getVehicleInfo(vehicleID))
        if flags != INVALIDATE_OP.NONE:
            self._invokeListenersMethod('invalidateVehicleStatus', flags, vo, self._arenaDP)

    def __arena_onNewStatisticsReceived(self):
        self._arenaDP.buildStatsData(self._visitor.getArenaStatistics())
        self._invokeListenersMethod('invalidateVehiclesStats', self._arenaDP)

    def __arena_onVehicleStatisticsUpdate(self, vehicleID):
        flags, vo = self._arenaDP.updateVehicleStats(vehicleID, self._visitor.getArenaStatistics()[vehicleID])
        if flags != INVALIDATE_OP.NONE:
            self._invokeListenersMethod('updateVehiclesStats', [(flags, vo)], self._arenaDP)

    def __arena_onTeamKiller(self, vehicleID):
        flags, vo = self._arenaDP.updatePlayerStatus(vehicleID, self._visitor.vehicles.getVehicleInfo(vehicleID))
        if flags != INVALIDATE_OP.NONE:
            self._invokeListenersMethod('invalidatePlayerStatus', flags, vo, self._arenaDP)

    def __arena_onInteractiveStats(self, stats):
        stats, statuses = self._arenaDP.updateVehicleInteractiveStats(stats)
        for flags, vo in statuses:
            self._invokeListenersMethod('invalidateVehicleStatus', flags, vo, self._arenaDP)

        if stats:
            self._invokeListenersMethod('updateVehiclesStats', stats, self._arenaDP)

    def __arena_onGameModeSpecifcStats(self, isStatic, stats):
        for vehicleID, vehicleStats in stats.iteritems():
            flags, vo = self._arenaDP.updateGameModeSpecificStats(vehicleID, isStatic, vehicleStats)
            if isStatic:
                self._invokeListenersMethod('updateVehiclesInfo', [(flags, vo)], self._arenaDP)
            if flags != INVALIDATE_OP.NONE:
                self._invokeListenersMethod('updateVehiclesStats', [(flags, vo)], self._arenaDP)

    def __isRequiredDataExists(self):
        return self._arenaDP is not None and self._arenaDP.isRequiredDataExists()

    def __setCallback(self):
        self.__callbackID = BigWorld.callback(0.1, self.__handleCallback)

    def __clearCallback(self):
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        return

    def __handleCallback(self):
        self.__callbackID = None
        if self.__isRequiredDataExists():
            self._invokeListenersMethod('invalidateArenaInfo')
        else:
            self.__setCallback()
        return


_TAGS_TO_UPDATE = {USER_TAG.FRIEND,
 USER_TAG.IGNORED,
 USER_TAG.IGNORED_TMP,
 USER_TAG.MUTED}

class ContactsListener(_Listener):
    __slots__ = ()

    def start(self, setup):
        super(ContactsListener, self).start(setup)
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
         USER_ACTION_ID.TMP_IGNORED_ADDED,
         USER_ACTION_ID.TMP_IGNORED_REMOVED,
         USER_ACTION_ID.MUTE_SET,
         USER_ACTION_ID.MUTE_UNSET):
            self._invokeListenersMethod('invalidateUserTags', user)


class PersonalInvitationsListener(_Listener):
    __slots__ = ('__filter',)

    def __init__(self):
        super(PersonalInvitationsListener, self).__init__()
        self.__filter = SquadInvitationsFilter()

    @prbInvitesProperty
    def prbInvites(self):
        return None

    def start(self, setup):
        super(PersonalInvitationsListener, self).start(setup)
        self.__filter.setArenaUniqueID(self._visitor.getArenaUniqueID())
        invitesManager = self.prbInvites
        invitesManager.onReceivedInviteListModified += self.__im_onReceivedInviteModified
        invitesManager.onSentInviteListModified += self.__im_onSentInviteListModified
        invitesManager.onInvitesListInited += self.__im_onInvitesListInited

    def stop(self):
        invitesManager = self.prbInvites
        invitesManager.onReceivedInviteListModified -= self.__im_onReceivedInviteModified
        invitesManager.onSentInviteListModified -= self.__im_onSentInviteListModified
        invitesManager.onInvitesListInited -= self.__im_onInvitesListInited
        super(PersonalInvitationsListener, self).stop()

    def addController(self, controller):
        result = super(PersonalInvitationsListener, self).addController(controller)
        if result:
            self.__updateInvitationsStatuses()
        return result

    def __updateFilteredStatuses(self, filtered):
        update = self._arenaDP.updateInvitationStatus
        vos = []
        for dbID, include, exclude in filtered:
            flags, vo = update(dbID, include=include, exclude=exclude)
            if vo is not None and flags != INVALIDATE_OP.NONE:
                LOG_DEBUG('Invitation status has been changed', dbID, vo.invitationDeliveryStatus)
                vos.append(vo)

        if vos:
            self._invokeListenersMethod('invalidateInvitationsStatuses', vos, self._arenaDP)
        return

    def __updateInvitationsStatuses(self):
        update = self._arenaDP.updateInvitationStatus
        vos = []
        for invite in self.prbInvites.getInvites(incoming=True):
            accountDBID, include = self.__filter.addReceivedInvite(invite)
            flags, vo = update(accountDBID, include=include)
            if vo is not None and flags != INVALIDATE_OP.NONE:
                vos.append(vo)

        for invite in self.prbInvites.getInvites(incoming=False):
            accountDBID, include = self.__filter.addSentInvite(invite)
            flags, vo = update(accountDBID, include=include)
            if vo is not None and flags != INVALIDATE_OP.NONE:
                vos.append(vo)

        if vos:
            self._invokeListenersMethod('invalidateInvitationsStatuses', vos, self._arenaDP)
        return

    def __im_onReceivedInviteModified(self, added, changed, deleted):
        filtered = self.__filter.filterReceivedInvites(self.prbInvites.getInvite, added, changed, deleted)
        self.__updateFilteredStatuses(filtered)

    def __im_onSentInviteListModified(self, added, changed, deleted):
        filtered = self.__filter.filterSentInvites(self.prbInvites.getInvite, added, changed, deleted)
        self.__updateFilteredStatuses(filtered)

    def __im_onInvitesListInited(self):
        self.__updateInvitationsStatuses()


_MAX_PROGRESS_VALUE = 1.0
_SPACE_INVALIDATION_PERIOD = 0.5
_INFLUX_INVALIDATION_PERIOD = 0.5

class _LOAD_STATE_FLAG(object):
    UNDEFINED = 0
    SPACE_LOAD_COMPLETED = 2
    INFLUX_LOAD_COMPLETED = 4


class ArenaSpaceLoadListener(_Listener):
    """Listener of Arena space loading status."""

    def __init__(self):
        super(ArenaSpaceLoadListener, self).__init__()
        self.__progress = 0.0
        self.__state = _LOAD_STATE_FLAG.UNDEFINED
        self.__spaceLoadCB = None
        self.__influxDrawCB = None
        return

    def start(self, setup):
        super(ArenaSpaceLoadListener, self).start(setup)
        self.__onSpaceLoadStarted()
        self.__loadSpaceCallback()

    def stop(self):
        self.__clearSpaceCallback()
        self.__clearInfluxCallback()
        super(ArenaSpaceLoadListener, self).stop()

    def addController(self, controller):
        result = super(ArenaSpaceLoadListener, self).addController(controller)
        if result:
            controller.spaceLoadStarted()
            if self.__state != _LOAD_STATE_FLAG.UNDEFINED:
                if self.__state & _LOAD_STATE_FLAG.SPACE_LOAD_COMPLETED > 0:
                    controller.spaceLoadCompleted()
                if self.__state & _LOAD_STATE_FLAG.INFLUX_LOAD_COMPLETED > 0:
                    controller.arenaLoadCompleted()
        return result

    def __loadSpaceCallback(self):
        self.__clearSpaceCallback()
        progress = 1.0
        import BattleReplay
        if not BattleReplay.g_replayCtrl.isTimeWarpInProgress:
            progress = BigWorld.spaceLoadStatus()
        if progress > self.__progress:
            self.__progress = progress
            self.__onSpaceLoadUpdated(progress)
        if progress < _MAX_PROGRESS_VALUE:
            self.__spaceLoadCB = BigWorld.callback(_SPACE_INVALIDATION_PERIOD, self.__loadSpaceCallback)
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
            self.__influxDrawCB = BigWorld.callback(_SPACE_INVALIDATION_PERIOD, self.__loadInfluxCallback)

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
        self.__state |= _LOAD_STATE_FLAG.SPACE_LOAD_COMPLETED
        self._invokeListenersMethod('spaceLoadCompleted')

    def __onArenaLoadCompleted(self):
        self.__state |= _LOAD_STATE_FLAG.INFLUX_LOAD_COMPLETED
        self._invokeListenersMethod('arenaLoadCompleted')


class ArenaTeamBasesListener(_Listener):
    __slots__ = ('__baseIDs', '__points')

    def __init__(self):
        super(ArenaTeamBasesListener, self).__init__()

    def start(self, setup):
        super(ArenaTeamBasesListener, self).start(setup)
        arena = self._visitor.getArenaSubscription()
        if arena is not None:
            arena.onTeamBasePointsUpdate += self.__arena_onTeamBasePointsUpdate
            arena.onTeamBaseCaptured += self.__arena_onTeamBaseCaptured
            arena.onPeriodChange += self.__arena_onPeriodChange
        return

    def stop(self):
        arena = self._visitor.getArenaSubscription()
        if arena is not None:
            arena.onTeamBasePointsUpdate -= self.__arena_onTeamBasePointsUpdate
            arena.onTeamBaseCaptured -= self.__arena_onTeamBaseCaptured
            arena.onPeriodChange -= self.__arena_onPeriodChange
        super(ArenaTeamBasesListener, self).stop()
        return

    def __arena_onTeamBasePointsUpdate(self, team, baseID, points, timeLeft, invadersCnt, capturingStopped):
        self._invokeListenersMethod('invalidateTeamBasePoints', team, baseID, points, timeLeft, invadersCnt, capturingStopped)

    def __arena_onTeamBaseCaptured(self, team, baseID):
        self._invokeListenersMethod('invalidateTeamBaseCaptured', team, baseID)

    def __arena_onPeriodChange(self, period, *args):
        if period == ARENA_PERIOD.AFTERBATTLE:
            self._invokeListenersMethod('removeTeamsBases')


class ArenaPeriodListener(_Listener):
    __slots__ = ()

    def start(self, setup):
        super(ArenaPeriodListener, self).start(setup)
        self.__setPeriodInfo(controller=None)
        arena = self._visitor.getArenaSubscription()
        if arena is not None:
            arena.onPeriodChange += self.__arena_onPeriodChange
        return

    def stop(self):
        arena = self._visitor.getArenaSubscription()
        if arena is not None:
            arena.onPeriodChange -= self.__arena_onPeriodChange
        super(ArenaPeriodListener, self).stop()
        return

    def addController(self, controller):
        result = super(ArenaPeriodListener, self).addController(controller)
        if result:
            self.__setPeriodInfo(controller)
        return result

    def __setPeriodInfo(self, controller=None):
        if self._visitor is not None:
            period = self._visitor.getArenaPeriod()
            periodAddInfo = _getPeriodAdditionalInfo(self._arenaDP, period, self._visitor.getArenaPeriodAdditionalInfo())
            if controller is not None:
                controller.setPeriodInfo(period, self._visitor.getArenaPeriodEndTime(), self._visitor.getArenaPeriodLength(), periodAddInfo, self._visitor.type.getCountdownTimerSound())
            else:
                self._invokeListenersMethod('setPeriodInfo', period, self._visitor.getArenaPeriodEndTime(), self._visitor.getArenaPeriodLength(), periodAddInfo, self._visitor.type.getCountdownTimerSound())
        return

    def __arena_onPeriodChange(self, period, endTime, length, additionalInfo):
        self._invokeListenersMethod('invalidatePeriodInfo', period, endTime, length, _getPeriodAdditionalInfo(self._arenaDP, period, additionalInfo))


class ArenaRespawnListener(_Listener):
    __slots__ = ()

    def start(self, setup):
        super(ArenaRespawnListener, self).start(setup)
        arena = self._visitor.getArenaSubscription()
        if arena is not None:
            arena.onRespawnAvailableVehicles += self.__arena_onRespawnAvailableVehicles
            arena.onRespawnCooldowns += self.__arena_onRespawnCooldowns
            arena.onRespawnRandomVehicle += self.__arena_onRespawnRandomVehicle
            arena.onRespawnResurrected += self.__arena_onRespawnResurrected
        return

    def stop(self):
        arena = self._visitor.getArenaSubscription()
        if arena is not None:
            arena.onRespawnAvailableVehicles -= self.__arena_onRespawnAvailableVehicles
            arena.onRespawnCooldowns -= self.__arena_onRespawnCooldowns
            arena.onRespawnRandomVehicle -= self.__arena_onRespawnRandomVehicle
            arena.onRespawnResurrected -= self.__arena_onRespawnResurrected
        super(ArenaRespawnListener, self).stop()
        return

    def __arena_onRespawnAvailableVehicles(self, vehsList):
        self._invokeListenersMethod('updateRespawnVehicles', vehsList)

    def __arena_onRespawnCooldowns(self, cooldowns):
        self._invokeListenersMethod('updateRespawnCooldowns', cooldowns)

    def __arena_onRespawnRandomVehicle(self, respawnInfo):
        self._invokeListenersMethod('updateRespawnInfo', respawnInfo)

    def __arena_onRespawnResurrected(self, respawnInfo):
        self._invokeListenersMethod('updateRespawnRessurectedInfo', respawnInfo)


class PositionsListener(_Listener):
    __slots__ = ()

    def start(self, setup):
        super(PositionsListener, self).start(setup)
        arena = self._visitor.getArenaSubscription()
        if arena is not None:
            arena.onPositionsUpdated += self.__arena_onPositionsUpdated
        return

    def stop(self):
        arena = self._visitor.getArenaSubscription()
        if arena is not None:
            arena.onPositionsUpdated -= self.__arena_onPositionsUpdated
        super(PositionsListener, self).stop()
        return

    def __arena_onPositionsUpdated(self):
        positions = self._visitor.getArenaPositions()
        if self._arenaDP is not None:
            getter = self._arenaDP.getVehicleInfo
        else:

            def getter(_):
                return None

        def _iterator():
            for vehicleID, position in positions.iteritems():
                yield (getter(vehicleID), position)

        self._invokeListenersMethod('updatePositions', _iterator)
        return


class ViewPointsListener(_Listener):
    __slots__ = ()

    def start(self, setup):
        super(ViewPointsListener, self).start(setup)
        arena = self._visitor.getArenaSubscription()
        if arena is not None:
            arena.onViewPoints += self.__arena_onViewPoints
        return

    def stop(self):
        arena = self._visitor.getArenaSubscription()
        if arena is not None:
            arena.onViewPoints -= self.__arena_onViewPoints
        super(ViewPointsListener, self).stop()
        return

    def __arena_onViewPoints(self, viewPoints):
        self._invokeListenersMethod('updateViewPoints', viewPoints)


class ListenersCollection(_Listener):
    __slots__ = ('__vehicles', '__teamsBases', '__loader', '__contacts', '__period', '__respawn', '__invitations', '__positions', '__viewPoints', '__battleCtx')

    def __init__(self):
        super(ListenersCollection, self).__init__()
        self.__battleCtx = None
        self.__vehicles = ArenaVehiclesListener()
        self.__teamsBases = ArenaTeamBasesListener()
        self.__contacts = ContactsListener()
        self.__loader = ArenaSpaceLoadListener()
        self.__period = ArenaPeriodListener()
        self.__respawn = ArenaRespawnListener()
        self.__invitations = PersonalInvitationsListener()
        self.__positions = PositionsListener()
        self.__viewPoints = ViewPointsListener()
        return

    def addController(self, controller):
        result = False
        try:
            scope = controller.getCtrlScope()
        except AttributeError:
            LOG_ERROR('Controller is not valid', controller)
            return False

        controller.startControl(self.__battleCtx, self._visitor)
        if scope & _SCOPE.LOAD > 0:
            result |= self.__loader.addController(controller)
        if scope & _SCOPE.VEHICLES > 0:
            result |= self.__vehicles.addController(controller)
        if scope & _SCOPE.CONTACTS > 0:
            result |= self.__contacts.addController(controller)
        if scope & _SCOPE.PERIOD > 0:
            result |= self.__period.addController(controller)
        if scope & _SCOPE.TEAMS_BASES > 0:
            result |= self.__teamsBases.addController(controller)
        if scope & _SCOPE.RESPAWN > 0:
            result |= self.__respawn.addController(controller)
        if scope & _SCOPE.INVITATIONS > 0:
            result |= self.__invitations.addController(controller)
        if scope & _SCOPE.POSITIONS > 0:
            result |= self.__positions.addController(controller)
        if scope & _SCOPE.VIEW_POINTS > 0:
            result |= self.__viewPoints.addController(controller)
        if not result:
            controller.stopControl()
        return result

    def removeController(self, controller):
        result = self.__vehicles.removeController(controller)
        result |= self.__teamsBases.removeController(controller)
        result |= self.__contacts.removeController(controller)
        result |= self.__loader.removeController(controller)
        result |= self.__period.removeController(controller)
        result |= self.__respawn.removeController(controller)
        result |= self.__invitations.removeController(controller)
        result |= self.__positions.removeController(controller)
        result |= self.__viewPoints.removeController(controller)
        return result

    def start(self, setup):
        self.__battleCtx = weakref.proxy(setup.battleCtx)
        super(ListenersCollection, self).start(setup)
        self.__vehicles.start(setup)
        self.__teamsBases.start(setup)
        self.__contacts.start(setup)
        self.__loader.start(setup)
        self.__period.start(setup)
        self.__respawn.start(setup)
        self.__invitations.start(setup)
        self.__positions.start(setup)
        self.__viewPoints.start(setup)

    def stop(self):
        self.__vehicles.stop()
        self.__teamsBases.stop()
        self.__contacts.stop()
        self.__loader.stop()
        self.__period.stop()
        self.__respawn.stop()
        self.__invitations.stop()
        self.__positions.stop()
        self.__viewPoints.stop()
        self.__battleCtx = None
        super(ListenersCollection, self).stop()
        return

    def clear(self):
        self.__vehicles.clear()
        self.__teamsBases.clear()
        self.__contacts.clear()
        self.__loader.clear()
        self.__period.clear()
        self.__respawn.clear()
        self.__invitations.clear()
        self.__positions.clear()
        self.__viewPoints.clear()
        super(ListenersCollection, self).clear()
