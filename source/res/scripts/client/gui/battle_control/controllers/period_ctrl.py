# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/period_ctrl.py
import weakref
import BattleReplay
import BigWorld
from constants import ARENA_PERIOD as _PERIOD
from gui.battle_control import event_dispatcher
from gui.battle_control.arena_info.interfaces import IArenaPeriodController
from gui.battle_control.battle_constants import COUNTDOWN_STATE, BATTLE_CTRL_ID
from gui.battle_control.view_components import IViewComponentsController
import SoundGroups
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager
_COUNTDOWN_HIDE_SPEED = 1.5
_START_NOTIFICATION_TIME = 5.0

class ITimersBar(object):
    """Interface of timers bar to display the countdown timer on the center of screen,
    timer of duration on the right top position on the screen.
    """

    def setTotalTime(self, totalTime):
        """Sets value of time for the timer of duration on the right top position on the screen.
        :param totalTime: integer containing time.
        """
        raise NotImplementedError

    def hideTotalTime(self):
        """Hides the timer of duration on the right top position on the screen."""
        raise NotImplementedError

    def setCountdown(self, state, timeLeft):
        """Sets value of time for the countdown timer on the center of screen.
        :param state: one of them COUNTDOWN_STATE.
        :param timeLeft: integer containing time.
        """
        raise NotImplementedError

    def hideCountdown(self, state, speed):
        """Hides the countdown timer on the center of screen.
        :param state: one of them COUNTDOWN_STATE.
        :param speed: float containing speed of hiding.
        """
        raise NotImplementedError

    def setWinConditionText(self, text):
        raise NotImplementedError

    def setState(self, state):
        """Controller notifies its components when state changes.
        :param state: one of COUNTDOWN_STATE
        """
        raise NotImplementedError


class IPlayersPanelsSwitcher(object):
    """Interface of switcher in UI to change display mode of players panels."""

    def setInitialMode(self):
        """Sets mode that is stored in settings."""
        raise NotImplementedError

    def setLargeMode(self):
        """Sets large mode until battle starts."""
        raise NotImplementedError


class ArenaPeriodController(IArenaPeriodController, IViewComponentsController):
    """Class of controller to sets/updates timers in the battle."""
    __slots__ = ('_callbackID', '_period', '_endTime', '_length', '_sound', '_battleTimerUI', '_preBattleTimerUI', '_cdState', '_ttState', '_isNotified', '_totalTime', '_countdown', '_playingTime', '_switcherUI', '_switcherState', '_battleCtx', '_arenaVisitor', '_battleEndWarning')

    def __init__(self):
        super(ArenaPeriodController, self).__init__()
        self._callbackID = None
        self._period = _PERIOD.IDLE
        self._totalTime = -1
        self._endTime = 0
        self._countdown = -1
        self._length = 0
        self._sound = None
        self._battleTimerUI = None
        self._preBattleTimerUI = None
        self._switcherUI = None
        self._cdState = COUNTDOWN_STATE.UNDEFINED
        self._ttState = 0
        self._switcherState = 0
        self._isNotified = False
        self._playingTime = 0
        self._battleCtx = None
        self._arenaVisitor = None
        self._battleEndWarning = None
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.ARENA_PERIOD

    def startControl(self, battleCtx, arenaVisitor):
        self._battleCtx = battleCtx
        self._arenaVisitor = arenaVisitor

    def stopControl(self):
        """Routine must be invoked when a battle is finishing."""
        self._battleCtx = None
        self._arenaVisitor = None
        self.__clearCallback()
        self._stopSound()
        self._setPlayingTimeOnArena()
        return

    def setViewComponents(self, battleTimerUI, preBattleTimerUI, switcherUI=None, battleEndWarning=None):
        """ Sets UI.
        :param battleTimerUI: reference to view of timer that show total time (top right on the screen).
        :param preBattleTimerUI: reference to view of timer that show countdown time (center on the screen).
        :param switcherUI: reference to view of player's panel switcher.
        :param battleEndWarning: reference to view of warning.
        """
        self._battleEndWarning = battleEndWarning
        self._battleTimerUI = battleTimerUI
        self._preBattleTimerUI = preBattleTimerUI
        self._switcherUI = switcherUI
        if self._period == _PERIOD.BATTLE:
            if switcherUI is not None:
                self._switcherUI.setInitialMode()
                self._switcherState = 1
        elif switcherUI is not None:
            self._switcherUI.setLargeMode()
            self._switcherState = 0
        if self._cdState in COUNTDOWN_STATE.VISIBLE:
            self._preBattleTimerUI.setCountdown(self._cdState, self._countdown)
            self._battleTimerUI.setState(self._cdState)
            if self._battleCtx is not None:
                self._preBattleTimerUI.setWinConditionText(self._battleCtx.getArenaWinString())
        self._battleTimerUI.setTotalTime(self._totalTime)
        return

    def clearViewComponents(self):
        """Removes reference to UI."""
        self._battleTimerUI = None
        self._preBattleTimerUI = None
        self._switcherUI = None
        return

    def getEndTime(self):
        return self._endTime

    def getPeriod(self):
        return self._period

    def setPeriodInfo(self, period, endTime, length, additionalInfo, soundID=None):
        """ Sets current time metrics that takes from the ClientArena.
        :param period: integer containing one of the ARENA_PERIOD.* values.
        :param endTime: float containing server time of the period end.
        :param length: float containing period length.
        :param additionalInfo: _PeriodAdditionalInfo.
        :param soundID: string containing path to the sound of countdown timer.
        """
        self._period = period
        self._endTime = endTime
        self._length = length
        if soundID:
            self._sound = SoundGroups.g_instance.getSound2D(soundID)
        self.__setCallback()

    def invalidatePeriodInfo(self, period, endTime, length, additionalInfo):
        """ Time metrics has been updated by server.
        :param period: integer containing one of the ARENA_PERIOD.* values.
        :param endTime: float containing server time of the period end.
        :param length: float containing period length.
        :param additionalInfo: _PeriodAdditionalInfo.
        """
        self._period = period
        self._endTime = endTime
        self._length = length
        self.__clearCallback()
        self.__setCallback()
        self._setArenaWinStatus(additionalInfo)

    def _getTickInterval(self, floatLength):
        """Calls tick once per second in regular mode and more precise if
        # arenaLength time comes to end.
        :param floatLength: float containing time left to end.
        :return: float containing next interval.
        """
        return 1 if floatLength > 1 else 0

    def _getHideSpeed(self):
        """ Gets speed of hiding. It's override in replay controller to hide
        countdown quickly.
        :return: float.
        """
        return _COUNTDOWN_HIDE_SPEED

    def _calculate(self):
        """ Gets current value of time until the end of the period.
        :return: float.
        """
        return self._endTime - BigWorld.serverTime()

    def _setPlayingTimeOnArena(self):
        if self._playingTime:
            event_dispatcher.setPlayingTimeOnArena(self._playingTime)

    def _setTotalTime(self, totalTime):
        if self._totalTime == totalTime:
            return
        else:
            self._totalTime = totalTime
            if self._battleTimerUI is not None:
                self._battleTimerUI.setTotalTime(totalTime)
            if self._battleEndWarning is not None and self._battleEndWarning.isLoaded():
                self._battleEndWarning.setCurrentTimeLeft(totalTime)
            return

    def _hideTotalTime(self):
        if self._battleTimerUI is not None:
            self._battleTimerUI.hideTotalTime()
        return

    def _setCountdown(self, state, timeLeft=None):
        if timeLeft is not None and self._countdown == timeLeft:
            return
        else:
            self._countdown = timeLeft
            if self._preBattleTimerUI is not None:
                self._preBattleTimerUI.setCountdown(state, timeLeft)
                self._battleTimerUI.setState(state)
            return

    def _hideCountdown(self, state, speed):
        self._countdown = None
        if self._preBattleTimerUI is not None:
            self._preBattleTimerUI.hideCountdown(state, speed)
            self._battleTimerUI.setState(state)
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
                            if self._switcherUI is not None:
                                self._switcherUI.setInitialMode()
                            self._switcherState = 1
                    elif self._switcherState != 0:
                        if self._switcherUI is not None:
                            self._switcherUI.setLargeMode()
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
    """Class of controller to sets/updates timers in the battle if client records
    battle to the replay file.
    """
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
    """Class of controller to sets/updates timers in the battle replay."""
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
        if self._playingTime > _COUNTDOWN_HIDE_SPEED:
            return 0
        else:
            return super(ArenaPeriodPlayer, self)._getHideSpeed()

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

    def _updateCountdown(self, timeLeft):
        super(ArenaPeriodPlayer, self)._updateCountdown(timeLeft)

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
