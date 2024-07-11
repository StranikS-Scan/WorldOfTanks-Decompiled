# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/Scaleform/daapi/view/battle/races/races_end_warning_panel.py
import BigWorld
import WWISE
from races.gui.impl.battle.battle_helpers import getRemainingTime
from constants import ARENA_PERIOD
from gui.Scaleform.daapi.view.meta.BattleEndWarningPanelMeta import BattleEndWarningPanelMeta
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from gui.impl import backport
from gui.impl.gen.resources import R
from helpers import dependency
from helpers.time_utils import ONE_MINUTE
from skeletons.gui.battle_session import IBattleSessionProvider

class _WWISE_EVENTS(object):
    APPEAR = 'time_buzzer_01'


_SWF_FILE_NAME = 'BattleEndWarningPanel.swf'
_CALLBACK_NAME = 'battle.onLoadEndWarningPanel'

class RacesEndWarningPanel(BattleEndWarningPanelMeta, IAbstractPeriodView):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    FINISH_FLAG_DURATION = 3

    def __init__(self):
        super(RacesEndWarningPanel, self).__init__()
        arenaVisitor = self.__sessionProvider.arenaVisitor
        self._duration = arenaVisitor.type.getBattleEndWarningDuration()
        self._appearTime = arenaVisitor.type.getBattleEndWarningAppearTime()
        self._roundLength = arenaVisitor.getRoundLength()
        self._isShown = False
        self._prematureEnd = False
        self._textInfo = None
        self._finishedRace = False
        return

    def _populate(self):
        super(RacesEndWarningPanel, self)._populate()
        arenaInfo = self.__sessionProvider.arenaVisitor.getArenaInfo()
        if arenaInfo is not None:
            if arenaInfo:
                arenaInfo.dynamicComponents.get('arenaInfoRacesComponent', None).onRaceEndTimeUpdated += self._onRaceEndTimeUpdated
        return

    def _dispose(self):
        super(RacesEndWarningPanel, self)._dispose()
        arenaInfo = self.__sessionProvider.arenaVisitor.getArenaInfo()
        if arenaInfo is not None:
            if arenaInfo:
                arenaInfo.dynamicComponents.get('arenaInfoRacesComponent', None).onRaceEndTimeUpdated -= self._onRaceEndTimeUpdated
        return

    def setTotalTime(self, totalTime):
        if not self._isInBattle():
            return
        finishFlagAnimationTime = 0
        if self._finishedRace:
            finishFlagAnimationTime = self.FINISH_FLAG_DURATION
        totalTime = int(getRemainingTime())
        if totalTime == self._appearTime - finishFlagAnimationTime:
            if not self._prematureEnd:
                self._isShown = True
            self._callWWISE(_WWISE_EVENTS.APPEAR)
            self.as_setTextInfoS(self._getTextInfo())
            self.as_setStateS(True)
        totalTime = int(getRemainingTime())
        minutes, seconds = divmod(int(totalTime), ONE_MINUTE)
        minutesStr = '{:02d}'.format(minutes)
        secondsStr = '{:02d}'.format(seconds)
        if self._isShown or self._prematureEnd:
            self.as_setTotalTimeS(minutesStr, secondsStr)
        if totalTime <= self._appearTime - self._duration - finishFlagAnimationTime and (self._isShown or self._prematureEnd):
            self.as_setStateS(False)

    def _callWWISE(self, wwiseEventName):
        WWISE.WW_eventGlobal(wwiseEventName)

    def _onRaceEndTimeUpdated(self, timeEnd):
        if not self._isInBattle():
            return
        elif self._isShown:
            return
        else:
            if self._textInfo is None:
                vehicleID = self.__sessionProvider.shared.vehicleState.getControllingVehicleID()
                vehicle = BigWorld.entity(vehicleID)
                upd = vehicle.dynamicComponents.get('raceVehicleComponent')
                if upd.raceFinishTime > 0.0:
                    self._finishedRace = True
            if not self._finishedRace:
                self.as_setStateS(True)
            self._prematureEnd = True
            self.setTotalTime(self._appearTime)
            self.as_setTextInfoS(self._getTextInfo())
            return

    def _getTextInfo(self):
        if self._textInfo is None:
            if self._prematureEnd and not self._finishedRace:
                self._textInfo = backport.text(R.strings.races.battle.timer.enemyFinished())
            else:
                self._textInfo = backport.text(R.strings.races.battle.timer.raceFinishPeriod())
        return self._textInfo

    def _isInBattle(self):
        periodCtrl = self.__sessionProvider.shared.arenaPeriod
        period = periodCtrl.getPeriod()
        return period == ARENA_PERIOD.BATTLE
