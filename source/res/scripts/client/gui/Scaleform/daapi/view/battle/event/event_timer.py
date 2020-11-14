# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/event_timer.py
from gui import makeHtmlString
from gui.Scaleform.daapi.view.meta.EventTimerMeta import EventTimerMeta

class EventTimer(EventTimerMeta):
    _COLOR = '#ffffff'
    _MESSAGE = 'timerEventMessage'
    _HTML_TEMPLATE_PATH = 'html_templates:battleTimer'
    _WAIT_TIME = 300
    _ALARM_TIME = 60
    _ALART_STATE_ENABLED = 1
    _ALART_STATE_DISABLED = 0
    _MAX_PROGRESS = 100
    _TITLE_TMPL = '<font color="{color}">{text}</font>'
    _TIMER_TMPL = '<font color="{color}">{min:02d}:{sec:02d}</font>'

    def __init__(self):
        super(EventTimer, self).__init__()
        self._waitTime = self._WAIT_TIME
        self._alarmTime = self._ALARM_TIME
        self._visible = True
        self._progress = 0

    def _populate(self):
        super(EventTimer, self)._populate()
        self._onUpdateScenarioTimer(self._waitTime, self._alarmTime, self._visible)

    def _dispose(self):
        self._waitTime = 0
        self._alarmTime = 0
        self._visible = False
        super(EventTimer, self)._dispose()

    def _onUpdateScenarioTimer(self, waitTime, alarmTime, visible):
        self._waitTime = waitTime
        self._alarmTime = alarmTime
        self._visible = visible
        self._updateTimer()

    def _updateTimer(self):
        if self._waitTime >= 0 and self._visible:
            m, s = divmod(int(self._waitTime), self._ALARM_TIME)
            timeLeft = self._TIMER_TMPL.format(color=self._COLOR, min=m, sec=s)
            message = makeHtmlString(self._HTML_TEMPLATE_PATH, self._MESSAGE)
            titlText = self._TITLE_TMPL.format(color=self._COLOR, text=message)
            timerStateAlarm = self._ALART_STATE_DISABLED
            if self._waitTime <= self._alarmTime:
                timerStateAlarm = self._ALART_STATE_ENABLED
                if self._waitTime == self._ALARM_TIME:
                    self.as_playFxS()
            self.as_setTimerStateS(timerStateAlarm)
            self.as_updateTimeS(timeLeft)
            if self._progress < self._MAX_PROGRESS:
                self.as_updateTitleS(titlText)
                self.as_updateProgressBarS(self._progress, True)
        else:
            self._hideTimer()

    def _playFxS(self):
        self.as_playFxS()

    def _hideTimer(self):
        self.as_updateTimeS('')
        self.as_updateTitleS('')
        self.as_updateProgressBarS(0, False)

    def setProgress(self, progress):
        self._progress = progress
