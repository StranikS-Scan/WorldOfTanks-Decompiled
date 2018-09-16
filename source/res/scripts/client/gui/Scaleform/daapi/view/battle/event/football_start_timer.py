# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/football_start_timer.py
from gui.Scaleform.daapi.view.meta.FootballStartTimerMeta import FootballStartTimerMeta
from gui.Scaleform.locale.FOOTBALL2018 import FOOTBALL2018
from gui.battle_control.controllers.football_ctrl import IFootballPeriodListener
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView

class FootballStartTimer(FootballStartTimerMeta, IAbstractPeriodView, IFootballPeriodListener):

    def __init__(self):
        super(FootballStartTimer, self).__init__()
        self.__showView = False
        self.__shown = False

    def _populate(self):
        super(FootballStartTimer, self)._populate()
        self.as_setVisibilityS(False)

    def onPrepareFootballOvertime(self):
        self.__showView = False

    def onStartFootballOvertime(self):
        self.__showView = False
        self.as_setVisibilityS(self.__showView)

    def onBallDrop(self):
        self.__showView = True
        self.as_setVisibilityS(self.__showView)
        self.as_setTextS({'timerDescr': FOOTBALL2018.MESSAGES_FOOTBALL_BALLDROP_TIMERDESCR,
         'objectiveDescr': FOOTBALL2018.MESSAGES_FOOTBALL_STARTTIMER_OBJECTIVEDESCR})

    def hideCountdown(self, state, speed):
        super(FootballStartTimer, self).hideCountdown(state, speed)
        self.__showView = False
        self.as_setVisibilityS(self.__showView)

    def setCountdown(self, state, timeLeft):
        if self.__showView:
            if not self.__shown:
                self.__shown = True
                self.as_setVisibilityS(self.__showView)
            secondsStr = '{:02d}'.format(timeLeft)
            self.as_setTimerS(secondsStr)
        else:
            if self.__shown:
                self.__shown = False
                self.as_setTimerS(None)
            self.as_setVisibilityS(False)
        return
