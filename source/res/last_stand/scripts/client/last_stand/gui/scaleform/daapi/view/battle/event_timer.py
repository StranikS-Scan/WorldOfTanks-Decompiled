# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/battle/event_timer.py
from enum import IntEnum
from gui.Scaleform.daapi.view.meta.EventTimerMeta import EventTimerMeta
from helpers import dependency
from last_stand.gui.ls_gui_constants import BATTLE_CTRL_ID
from skeletons.gui.battle_session import IBattleSessionProvider

class _AlarmTime(IntEnum):
    FIRST = 60
    SECOND = 30
    LAST = 10


class _AlertState(IntEnum):
    DISABLED = 0
    ENABLED = 1


class EventTimer(EventTimerMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _COLOR = '#ffffff'
    _HTML_TEMPLATE_PATH = 'html_templates:battleTimer'
    _ALERT_STATE_ENABLED = 1
    _ALERT_STATE_DISABLED = 0
    _ONE_MINUTE_SECONDS = 60

    def __init__(self):
        super(EventTimer, self).__init__()
        self._visible = False
        self._currentHint = None
        return

    @property
    def lsBattleGuiCtrl(self):
        return self.sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.LS_BATTLE_GUI_CTRL)

    def _populate(self):
        super(EventTimer, self)._populate()
        if self.lsBattleGuiCtrl is not None:
            self.lsBattleGuiCtrl.onPhaseTimeChanged += self._onTimerUpdated
        return

    def _dispose(self):
        self._visible = False
        if self.lsBattleGuiCtrl is not None:
            self.lsBattleGuiCtrl.onPhaseTimeChanged -= self._onTimerUpdated
        super(EventTimer, self)._dispose()
        return

    def _onTimerUpdated(self, seconds, prev, lastPhase, isTimerAlarmEnabled):
        self._visible = seconds > 0 and self.lsBattleGuiCtrl is not None and self.lsBattleGuiCtrl.isEventTimerEnabled
        if not self._visible:
            self._hideTimer()
            return
        else:
            m, s = divmod(int(seconds), self._ONE_MINUTE_SECONDS)
            timeString = '<font color="{color}">{min:02d}:{sec:02d}</font>'.format(color=self._COLOR, min=m, sec=s)
            if isTimerAlarmEnabled and (seconds == _AlarmTime.FIRST or seconds == _AlarmTime.SECOND or seconds <= _AlarmTime.LAST):
                self.as_playFxS()
            needAlarm = isTimerAlarmEnabled and seconds <= _AlarmTime.FIRST
            timerState = _AlertState.ENABLED if needAlarm else _AlertState.DISABLED
            self.as_setTimerStateS(timerState.value)
            self.as_updateTimeS(timeString)
            return

    def _hideTimer(self):
        self.as_setTimerStateS(_AlertState.DISABLED)
        self.as_updateTimeS('')
        self.as_updateTitleS('')
