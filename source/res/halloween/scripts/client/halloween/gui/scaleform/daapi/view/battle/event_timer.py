# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/battle/event_timer.py
from __future__ import absolute_import
from enum import IntEnum
import typing
from HWArenaPhasesComponent import HWArenaPhasesComponent
from gui.Scaleform.daapi.view.meta.EventTimerMeta import EventTimerMeta
from halloween.gui.halloween_gui_constants import BATTLE_CTRL_ID
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from typing import Optional

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
        self._timerState = None
        return

    @property
    def hwBattleGuiCtrl(self):
        return self.sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.HW_BATTLE_GUI_CTRL)

    def _populate(self):
        super(EventTimer, self)._populate()
        hwBattleGuiCtrl = self.hwBattleGuiCtrl
        if hwBattleGuiCtrl:
            hwBattleGuiCtrl.onChangeAnomaliesViewVisibility += self._onChangeAnomaliesViewVisibility
        HWArenaPhasesComponent.onPhaseTimeChanged += self._onTimerUpdated

    def _dispose(self):
        self._visible = False
        hwBattleGuiCtrl = self.hwBattleGuiCtrl
        if hwBattleGuiCtrl:
            hwBattleGuiCtrl.onChangeAnomaliesViewVisibility -= self._onChangeAnomaliesViewVisibility
        HWArenaPhasesComponent.onPhaseTimeChanged -= self._onTimerUpdated
        super(EventTimer, self)._dispose()

    def _onChangeAnomaliesViewVisibility(self, _):
        self._refreshTimerState()

    def _onTimerUpdated(self, seconds, prev, lastPhase):
        self._visible = seconds > 0
        if not self._visible:
            self._hideTimer()
            return
        m, s = divmod(int(seconds), self._ONE_MINUTE_SECONDS)
        timeString = '<font color="{color}">{min:02d}:{sec:02d}</font>'.format(color=self._COLOR, min=m, sec=s)
        needAlarm = seconds <= _AlarmTime.FIRST
        self._timerState = _AlertState.ENABLED if needAlarm else _AlertState.DISABLED
        self._refreshTimerState()
        self.as_updateTimeS(timeString)
        if seconds == _AlarmTime.FIRST or seconds == _AlarmTime.SECOND or seconds <= _AlarmTime.LAST:
            self.as_playFxS()

    def _refreshTimerState(self):
        if self._timerState is not None:
            timerState = _AlertState.DISABLED if self.hwBattleGuiCtrl.isAnomaliesViewVisible else self._timerState
            self.as_setTimerStateS(timerState.value)
        return

    def _hideTimer(self):
        self.as_setTimerStateS(_AlertState.DISABLED)
        self.as_updateTimeS('')
        self.as_updateTitleS('')
