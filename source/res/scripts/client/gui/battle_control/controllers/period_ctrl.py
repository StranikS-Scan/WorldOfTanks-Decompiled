# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/period_ctrl.py
import weakref
import BattleReplay
import BigWorld
from constants import ARENA_PERIOD as _PERIOD
from gui.battle_control import event_dispatcher
from gui.battle_control.arena_info.interfaces import IArenaPeriodController
from gui.battle_control.battle_constants import COUNTDOWN_STATE, BATTLE_CTRL_ID
from gui.battle_control.view_components import ViewComponentsController
import SoundGroups
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager
_COUNTDOWN_HIDE_SPEED = 1.5
_START_NOTIFICATION_TIME = 5.0

class IPlayersPanelsSwitcher(object):

    def setInitialMode(self):
        pass

    def setLargeMode(self):
        pass


class IAbstractPeriodView(IPlayersPanelsSwitcher):

    def setState(self, state):
        pass

    def setPeriod(self, period):
        pass

    def setTotalTime(self, totalTime):
        pass

    def hideTotalTime(self):
        pass

    def setCountdown(self, state, timeLeft):
        pass

    def hideCountdown(self, state, speed):
        pass

    def updateBattleCtx(self, ctx):
        pass


class ITimersBar(object):

    def setTotalTime(self, totalTime):
        raise NotImplementedError

    def hideTotalTime(self):
        raise NotImplementedError

    def setCountdown(self, state, timeLeft):
        raise NotImplementedError

    def hideCountdown(self, state, speed):
        raise NotImplementedError

    def updateBattleCtx(self, ctx):
        raise NotImplementedError

    def setState(self, state):
        raise NotImplementedError


class ArenaPeriodController(IArenaPeriodController, ViewComponentsController):
    __slots__ = ('_callbackID', '_period', '_endTime', '_length', '_sound', '_cdState', '_ttState', '_isNotified', '_totalTime', '_countdown', '_playingTime', '_switcherState', '_battleCtx', '_arenaVisitor', '_timeNotifications')

    def __init__(self):
        super(ArenaPeriodController, self).__init__()
        self._callbackID = None
        self._period = _PERIOD.IDLE
        self._totalTime = -1
        self._endTime = 0
        self._countdown = -1
        self._length = 0
        self._sound = None
        self._cdState = COUNTDOWN_STATE.UNDEFINED
        self._ttState = 0
        self._switcherState = 0
        self._isNotified = False
        self._playingTime = 0
        self._battleCtx = None
        self._arenaVisitor = None
        self._timeNotifications = []
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.ARENA_PERIOD

    def startControl(self, battleCtx, arenaVisitor):
        self._battleCtx = battleCtx
        self._arenaVisitor = arenaVisitor

    def stopControl(self):
        self._battleCtx = None
        self._arenaVisitor = None
        self.__clearCallback()
        self._stopSound()
        self._setPlayingTimeOnArena()
        return

    def setViewComponents(self, *components):
        super(ArenaPeriodController, self).setViewComponents(*components)
        if self._period == _PERIOD.BATTLE:
            for viewCmp in self._viewComponents:
                viewCmp.setInitialMode()

            self._switcherState = 1
        else:
            for viewCmp in self._viewComponents:
                viewCmp.setLargeMode()

            self._switcherState = 0
        if self._cdState in COUNTDOWN_STATE.VISIBLE:
            for viewCmp in self._viewComponents:
                viewCmp.setState(self._cdState)
                viewCmp.setCountdown(self._cdState, self._countdown)
                if self._battleCtx is not None:
                    viewCmp.updateBattleCtx(self._battleCtx)

        for viewCmp in self._viewComponents:
            viewCmp.setPeriod(self._period)
            viewCmp.setTotalTime(self._totalTime)

        return

    def addRemainingTimeNotification(self, minutes, seconds, callback):
        conValid = self._totalTime <= minutes * 60 + seconds
        self._timeNotifications.append((minutes,
         seconds,
         callback,
         conValid))

    def getEndTime(self):
        return self._endTime

    def getPeriod(self):
        return self._period

    def setPeriodInfo(self, period, endTime, length, additionalInfo, soundID=None):
        self._period = period
        self._endTime = endTime
        self._length = length
        self.__invokeViewPeriodUpdate()
        if soundID:
            self._sound = SoundGroups.g_instance.getSound2D(soundID)
        self.__setCallback()

    def invalidatePeriodInfo(self, period, endTime, length, additionalInfo):
        self._period = period
        self._endTime = endTime
        self._length = length
        self.__invokeViewPeriodUpdate()
        self.__clearCallback()
        self.__setCallback()
        self._setArenaWinStatus(additionalInfo)

    def _getTickInterval(self, floatLength):
        return 1 if floatLength > 1 else 0

    def _getHideSpeed(self):
        return _COUNTDOWN_HIDE_SPEED

    def _calculate(self):
        return self._endTime - BigWorld.serverTime()

    def _setPlayingTimeOnArena(self):
        if self._playingTime:
            event_dispatcher.setPlayingTimeOnArena(self._playingTime)

    def _setTotalTime(self, totalTime):
        if self._totalTime == totalTime:
            return
        self._totalTime = totalTime
        for viewCmp in self._viewComponents:
            viewCmp.setTotalTime(totalTime)

        minutes, seconds = divmod(int(totalTime), 60)
        for idx in range(len(self._timeNotifications)):
            m, s, f, state = self._timeNotifications[idx]
            condValid = totalTime <= m * 60 + s
            if condValid and not state:
                f(minutes, seconds)
                self._timeNotifications[idx] = (m,
                 s,
                 f,
                 True)
            if state and not condValid:
                self._timeNotifications[idx] = (m,
                 s,
                 f,
                 False)

    def _hideTotalTime(self):
        for viewCmp in self._viewComponents:
            viewCmp.hideTotalTime()

    def _setCountdown(self, state, timeLeft=None):
        if timeLeft is not None and self._countdown == timeLeft:
            return
        else:
            self._countdown = timeLeft
            for viewCmp in self._viewComponents:
                viewCmp.setCountdown(state, timeLeft)
                viewCmp.setState(state)

            return

    def _hideCountdown(self, state, speed):
        self._countdown = None
        for viewCmp in self._viewComponents:
            viewCmp.hideCountdown(state, speed)
            viewCmp.setState(state)

        return

    def _playSound(self):
        if self._sound and not self._sound.isPlaying:
            self._sound.play()

    def _stopSound(self):
        if self._sound and self._sound.isPlaying:
            self._sound.stop()

    def _updateSound(self, timeLeft):
        if timeLeft:
            self._playSound()
        else:
            self._stopSound()

    def _doNotify(self):
        if not self._isNotified:
            BigWorld.WGWindowsNotifier.onBattleBeginning()
            self._isNotified = True

    def _updateCountdown(self, timeLeft):
        if self._period == _PERIOD.WAITING:
            if self._cdState != COUNTDOWN_STATE.WAIT:
                self._cdState = COUNTDOWN_STATE.WAIT
                self._setCountdown(COUNTDOWN_STATE.WAIT)
        elif self._period == _PERIOD.PREBATTLE:
            if timeLeft <= _START_NOTIFICATION_TIME:
                self._doNotify()
            self._cdState = COUNTDOWN_STATE.START
            self._setCountdown(COUNTDOWN_STATE.START, timeLeft)
            self._updateSound(timeLeft)
        elif self._period == _PERIOD.BATTLE and self._cdState in COUNTDOWN_STATE.VISIBLE:
            self._cdState = COUNTDOWN_STATE.STOP
            self._stopSound()
            self._hideCountdown(COUNTDOWN_STATE.STOP, self._getHideSpeed())

    def _setArenaWinStatus(self, additionalInfo):
        if additionalInfo is not None:
            self._battleCtx.setLastArenaWinStatus(additionalInfo.getWinStatus())
        return

    def __invokeViewPeriodUpdate(self):
        for view in self._viewComponents:
            view.setPeriod(self._period)

    def __tick(self):
        floatLength = self._calculate()
        if floatLength is None:
            return 0
        else:
            intLength = max(int(floatLength), 0)
            if self._period != _PERIOD.AFTERBATTLE:
                self._ttState = 1
                self._setTotalTime(intLength)
                if self._period == _PERIOD.BATTLE:
                    self._playingTime = self._length - floatLength
                    if self._period == _PERIOD.BATTLE:
                        if self._switcherState != 1:
                            for viewCmp in self._viewComponents:
                                viewCmp.setInitialMode()

                            self._switcherState = 1
                    elif self._switcherState != 0:
                        for viewCmp in self._viewComponents:
                            viewCmp.setLargeMode()

                        self._switcherState = 0
            elif self._ttState:
                self._ttState = 0
                self._hideTotalTime()
            self._updateCountdown(intLength)
            return floatLength

    def __setCallback(self):
        self._callbackID = None
        length = self.__tick()
        self._callbackID = BigWorld.callback(self._getTickInterval(length), self.__setCallback)
        return

    def __clearCallback(self):
        if self._callbackID is not None:
            BigWorld.cancelCallback(self._callbackID)
            self._callbackID = None
        return


class ArenaPeriodRecorder(ArenaPeriodController):
    __slots__ = ('__recorder',)
    connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self):
        super(ArenaPeriodRecorder, self).__init__()
        self.__recorder = None
        return

    def startControl(self, battleCtx, arenaVisitor):
        if not arenaVisitor.gui.isTutorialBattle():
            ctrl = BattleReplay.g_replayCtrl
            self.connectionMgr.onDisconnected += self.__onDisconnected
            ctrl.onStopped += self.__onReplayStopped
            self.__recorder = ctrl.setArenaPeriod
        else:
            self.__recorder = None
        super(ArenaPeriodRecorder, self).startControl(battleCtx, arenaVisitor)
        return

    def stopControl(self):
        self.connectionMgr.onDisconnected -= self.__onDisconnected
        BattleReplay.g_replayCtrl.onStopped -= self.__onReplayStopped
        self.__recorder = None
        super(ArenaPeriodRecorder, self).stopControl()
        return

    def _calculate(self):
        floatLength = super(ArenaPeriodRecorder, self)._calculate()
        if self.__recorder is not None and self._period != _PERIOD.AFTERBATTLE:
            self.__recorder(self._period, floatLength)
        return floatLength

    def __onReplayStopped(self):
        self.__recorder = None
        return

    def __onDisconnected(self):
        self.__recorder = None
        return


class ArenaPeriodPlayer(ArenaPeriodController):
    __slots__ = ('__replay',)

    def __init__(self):
        super(ArenaPeriodPlayer, self).__init__()
        self.__replay = None
        return

    def startControl(self, battleCtx, arenaVisitor):
        self.__replay = weakref.proxy(BattleReplay.g_replayCtrl)
        super(ArenaPeriodPlayer, self).startControl(battleCtx, arenaVisitor)

    def stopControl(self):
        self.__replay = None
        super(ArenaPeriodPlayer, self).stopControl()
        return

    def _getTickInterval(self, floatLength):
        return 1 if self._period == _PERIOD.IDLE else 0

    def _getHideSpeed(self):
        return 0 if self._playingTime > _COUNTDOWN_HIDE_SPEED else super(ArenaPeriodPlayer, self)._getHideSpeed()

    def _calculate(self):
        if self.__replay is None:
            return 0
        else:
            self._period = self.__replay.getArenaPeriod()
            return None if self._period == _PERIOD.IDLE else self.__replay.getArenaLength()

    def _setPlayingTimeOnArena(self):
        pass

    def _setTotalTime(self, totalTime):
        if self.__replay is not None and not self.__replay.isFinished():
            super(ArenaPeriodPlayer, self)._setTotalTime(totalTime)
        return

    def _updateSound(self, timeLeft):
        if timeLeft and not self.__replay.playbackSpeed == 0:
            self._playSound()
        else:
            self._stopSound()

    def _doNotify(self):
        pass


def createPeriodCtrl(setup):
    if setup.isReplayRecording:
        clazz = ArenaPeriodRecorder
    elif setup.isReplayPlaying:
        clazz = ArenaPeriodPlayer
    else:
        clazz = ArenaPeriodController
    return clazz()
