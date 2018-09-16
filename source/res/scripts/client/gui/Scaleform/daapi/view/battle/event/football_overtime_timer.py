# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/football_overtime_timer.py
from gui.Scaleform.daapi.view.meta.FootballOvertimeTimerMeta import FootballOvertimeTimerMeta
from gui.Scaleform.locale.FOOTBALL2018 import FOOTBALL2018
from gui.battle_control.controllers.football_ctrl import IFootballPeriodListener
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from helpers.time_utils import ONE_MINUTE

class FootballOvertimeTimer(FootballOvertimeTimerMeta, IFootballPeriodListener, IAbstractPeriodView):

    def __init__(self):
        super(FootballOvertimeTimer, self).__init__()
        self.__showView = False
        self.__shown = False

    def _populate(self):
        super(FootballOvertimeTimer, self)._populate()
        self.as_setVisibilityS(False)

    def onPrepareFootballOvertime(self):
        self.__showView = True

    def onStartFootballOvertime(self):
        self.__showView = False
        self.as_setVisibilityS(self.__showView)

    def onBallDrop(self):
        self.__showView = False

    def setCountdown(self, state, timeLeft):
        if self.__showView:
            if not self.__shown:
                self.__shown = True
                self.as_setVisibilityS(self.__showView)
                self.as_setTextS({'header': FOOTBALL2018.MESSAGES_FOOTBALL_OVERTIME_HEADER,
                 'headerDescr': FOOTBALL2018.MESSAGES_FOOTBALL_OVERTIME_HEADERDESCR,
                 'or': FOOTBALL2018.MESSAGES_FOOTBALL_OVERTIME_OR,
                 'condA': FOOTBALL2018.MESSAGES_FOOTBALL_OVERTIME_CONDA,
                 'condB': FOOTBALL2018.MESSAGES_FOOTBALL_OVERTIME_CONDB,
                 'timerDescr': FOOTBALL2018.MESSAGES_FOOTBALL_OVERTIME_TIMERDESCR})
            minutes, seconds = divmod(int(timeLeft), ONE_MINUTE)
            minutesStr = '{:02d}'.format(minutes)
            secondsStr = '{:02d}'.format(seconds)
            self.as_setTimerS(minutesStr, secondsStr)
        else:
            if self.__shown:
                self.__shown = False
            self.as_setVisibilityS(False)
