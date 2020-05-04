# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/drone_music_player.py
import BigWorld
from gui.Scaleform.daapi.view.battle.event.game_event_getter import GameEventGetterMixin
from gui.Scaleform.daapi.view.battle.shared.drone_music_player import DroneMusicPlayer, _Condition, _Severity, _delegate
from constants import ARENA_PERIOD
_BOSS_MARKER_TYPES = set(['bossKill', 'heavyTankElite'])

class _EventCondition(_Condition):

    def onOwnRespawnLivesUpdated(self, ownLivesLeft):
        return False

    def onRespawnLivesUpdated(self, livesLeft):
        return False

    def onTimerUpdate(self, timeLeft):
        return False

    def onBotsUpdate(self, bots):
        return False


class _EventTimeRemainedCondition(_EventCondition):

    def __init__(self, criticalValue):
        super(_EventTimeRemainedCondition, self).__init__(criticalValue, _Severity.LOW)
        self.__period = None
        self.__timeLeft = None
        return

    def setPeriod(self, period):
        self.__period = period
        return self._isCriticalAchieved()

    def onTimerUpdate(self, timeLeft):
        self.__timeLeft = timeLeft
        return self._isCriticalAchieved()

    def _isCriticalAchieved(self):
        if self.__period is not None and self.__timeLeft is not None:
            self._initialized = True
        return self._updateValidValue(self.__timeLeft <= self.criticalValue) if self.__period == ARENA_PERIOD.BATTLE and self.__timeLeft is not None else False


class _TeamLivesLeftCondition(_EventCondition):

    def __init__(self, criticalValue):
        super(_TeamLivesLeftCondition, self).__init__(criticalValue, _Severity.MEDIUM)
        self._initialized = True

    def _isCriticalAchieved(self, livesLeft):
        return self._updateValidValue(livesLeft < self.criticalValue)

    def onRespawnLivesUpdated(self, livesLeft):
        return self._isCriticalAchieved(livesLeft)


class _PlayerObserverCondition(_EventCondition):

    def __init__(self, criticalValue):
        super(_PlayerObserverCondition, self).__init__(criticalValue, _Severity.MEDIUM)
        self._initialized = True
        self.__arenaPeriod = None
        self.__ownLivesLeft = None
        self.__teamLivesLeft = None
        return

    def setPeriod(self, period):
        self.__arenaPeriod = period

    def onOwnRespawnLivesUpdated(self, ownLivesLeft):
        self.__ownLivesLeft = ownLivesLeft
        return self._isCriticalAchieved()

    def onRespawnLivesUpdated(self, livesLeft):
        self.__teamLivesLeft = livesLeft
        return self._isCriticalAchieved()

    def _isCriticalAchieved(self):
        return self._updateValidValue(self.__ownLivesLeft == 0 and self.__teamLivesLeft is not None and self.__teamLivesLeft > 0) if self.__arenaPeriod == ARENA_PERIOD.BATTLE else False


class _BossBattleCondition(_EventCondition):

    def __init__(self, criticalValue):
        super(_BossBattleCondition, self).__init__(criticalValue, _Severity.LOW)
        self._initialized = True
        self._arenaPeriod = None
        return

    def setPeriod(self, period):
        self._arenaPeriod = period

    def _isCriticalAchieved(self, bots):
        return self._updateValidValue(_BOSS_MARKER_TYPES & bots) if self._arenaPeriod == ARENA_PERIOD.BATTLE else False

    def onBotsUpdate(self, bots):
        return self._isCriticalAchieved(bots)


class EventDroneMusicPlayer(DroneMusicPlayer, GameEventGetterMixin):
    _SETTING_TO_CONDITION_MAPPING = {'timeRemained': (lambda player: True, (_EventTimeRemainedCondition,), lambda name, key, data: data[name][key]),
     'playerObserver': (lambda player: True, (_PlayerObserverCondition,), lambda name, key, data: data[name][key]),
     'teamLivesLeft': (lambda player: True, (_TeamLivesLeftCondition,), lambda name, key, data: data[name][key]),
     'bossBattle': (lambda player: True, (_BossBattleCondition,), lambda name, key, data: data[name][key])}

    def __init__(self):
        super(EventDroneMusicPlayer, self).__init__()
        self.__killedBotsIDs = set()
        self.__goalFinishTime = 0
        self.__arenaLoaded = False
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onPlayerRespawnLivesUpdated += self.onOwnRespawnLivesUpdated
        self.teammateLifecycle.onUpdated += self.__onRespawnLivesUpdated
        self.activeTimers.onActiveTimersUpdated += self.__onTimerUpdate
        player = BigWorld.player()
        player.onBotRolesReceived += self.__onBotRolesReceived
        player.arena.onVehicleKilled += self.__onArenaVehicleKilled
        return

    def detachedFromCtrl(self, ctrlID):
        super(EventDroneMusicPlayer, self).detachedFromCtrl(ctrlID)
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onPlayerRespawnLivesUpdated -= self.onOwnRespawnLivesUpdated
        self.teammateLifecycle.onUpdated -= self.__onRespawnLivesUpdated
        self.activeTimers.onActiveTimersUpdated -= self.__onTimerUpdate
        player = BigWorld.player()
        player.onBotRolesReceived -= self.__onBotRolesReceived
        player.arena.onVehicleKilled -= self.__onArenaVehicleKilled
        return

    @_delegate
    def onRespawnLivesUpdated(self, livesLeft):
        pass

    @_delegate
    def onOwnRespawnLivesUpdated(self, livesLeft):
        pass

    @_delegate
    def onTimerUpdate(self, timeLeft):
        pass

    @_delegate
    def onBotsUpdate(self, bots):
        pass

    def arenaLoadCompleted(self):
        super(EventDroneMusicPlayer, self).arenaLoadCompleted()
        self.__initConditionsData()

    def setPeriod(self, period):
        super(EventDroneMusicPlayer, self).setPeriod(period)
        if period == ARENA_PERIOD.BATTLE:
            self.__initConditionsData()
        elif period == ARENA_PERIOD.AFTERBATTLE:
            self._stopMusic()

    def __initConditionsData(self):
        if self._isProperBattlePeroid():
            self.__onRespawnLivesUpdated()
            self.__updateBots()
            self.__onTimerUpdate()

    def setTotalTime(self, totalTime):
        super(EventDroneMusicPlayer, self).setTotalTime(totalTime)
        if self.__goalFinishTime > 0:
            self.onTimerUpdate(self.__goalFinishTime - BigWorld.serverTime())

    def __onTimerUpdate(self, diff=None):
        if not self.activeTimers.hasSyncData():
            return
        else:
            timersData = self.activeTimers.getSyncData()
            if timersData is not None:
                self.__goalFinishTime = max([ goal.get('finishTime', 0) for goal in timersData.itervalues() ])
            return

    def __onRespawnLivesUpdated(self):
        teammateLifecycleData = self.teammateLifecycle.getParams()
        self.onRespawnLivesUpdated(sum([ getattr(veh, 'lives', 0) for veh in teammateLifecycleData.itervalues() ]))

    def __updateBots(self):
        markerTypes = BigWorld.player().getBotMarkerTypes()
        aliveVehiclesTypes = set((markerType for vehicleId, markerType in markerTypes.iteritems() if vehicleId not in self.__killedBotsIDs))
        self.onBotsUpdate(aliveVehiclesTypes)

    def __onBotRolesReceived(self):
        self.__updateBots()

    def __onArenaVehicleKilled(self, targetID, attackerID, equipmentID, reason):
        self.__killedBotsIDs.add(targetID)
        self.__updateBots()
