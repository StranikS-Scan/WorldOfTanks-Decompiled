# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/event_timer.py
from enum import IntEnum
from gui import makeHtmlString
from gui.Scaleform.daapi.view.battle.event.game_event_getter import GameEventGetterMixin
from gui.Scaleform.daapi.view.meta.EventTimerMeta import EventTimerMeta
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control.battle_constants import EventBattleGoal

class _AlarmTime(IntEnum):
    FIRST = 60
    SECOND = 30
    LAST = 10


class _AlertState(IntEnum):
    DISABLED = 0
    ENABLED = 1


class EventTimer(EventTimerMeta, GameEventGetterMixin):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _COLOR = '#ffffff'
    _HTML_TEMPLATE_PATH = 'html_templates:battleTimer'
    _ALERT_STATE_ENABLED = 1
    _ALERT_STATE_DISABLED = 0
    _ONE_MINUTE_SECONDS = 60
    _GOAL_MESSAGES = {EventBattleGoal.UNKNOWN: None,
     EventBattleGoal.COLLECT_MATTER: 'collectMatter',
     EventBattleGoal.DELIVER_MATTER: 'deliverMatter',
     EventBattleGoal.GET_TO_COLLECTOR: 'getToPoint'}

    def __init__(self):
        super(EventTimer, self).__init__()
        self._visible = False
        self._currentHint = None
        return

    def _populate(self):
        super(EventTimer, self)._populate()
        battleGoalsCtrl = self.sessionProvider.dynamic.battleGoals
        if battleGoalsCtrl is not None:
            battleGoalsCtrl.events.onTimerUpdated += self._onTimerUpdated
            battleGoalsCtrl.events.onUpdatePointerMessage += self._onBattlePointerUpdated
        return

    def _dispose(self):
        self._visible = False
        battleGoalsCtrl = self.sessionProvider.dynamic.battleGoals
        if battleGoalsCtrl is not None:
            battleGoalsCtrl.events.onTimerUpdated -= self._onTimerUpdated
            battleGoalsCtrl.events.onUpdatePointerMessage -= self._onBattlePointerUpdated
        super(EventTimer, self)._dispose()
        return

    def _onTimerUpdated(self, seconds, isVisible, isAlarm):
        self._visible = isVisible
        if not isVisible:
            self._hideTimer()
            return
        m, s = divmod(int(seconds), self._ONE_MINUTE_SECONDS)
        timeString = '<font color="{color}">{min:02d}:{sec:02d}</font>'.format(color=self._COLOR, min=m, sec=s)
        if isAlarm or seconds == _AlarmTime.FIRST or seconds == _AlarmTime.SECOND or seconds <= _AlarmTime.LAST:
            self.as_playFxS()
        needAlarm = isAlarm or seconds <= _AlarmTime.FIRST
        timerState = _AlertState.ENABLED if needAlarm else _AlertState.DISABLED
        self.as_setTimerStateS(timerState.value)
        self.as_updateTimeS(timeString)

    def _onBattlePointerUpdated(self, currentGoal):
        self._updateTitle(currentGoal)

    def _updateTitle(self, currentGoal):
        if not self._visible:
            return
        else:
            title = ''
            if currentGoal is not None and currentGoal != EventBattleGoal.UNKNOWN:
                messageId = self._GOAL_MESSAGES[currentGoal]
                title = makeHtmlString(self._HTML_TEMPLATE_PATH, messageId)
            self.as_updateTitleS(title)
            return

    def _hideTimer(self):
        self.as_updateTimeS('')
        self.as_updateTitleS('')
