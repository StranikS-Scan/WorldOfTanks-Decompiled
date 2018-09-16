# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/football_overtime_bar.py
from gui.Scaleform.daapi.view.meta.FootballOvertimeBarMeta import FootballOvertimeBarMeta
from gui.Scaleform.locale.FOOTBALL2018 import FOOTBALL2018
from gui.battle_control import avatar_getter
from gui.battle_control.controllers.football_ctrl import IFootballPeriodListener
from gui.battle_control.controllers.football_ctrl import IFootballView
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView

class FootballOvertimeBar(FootballOvertimeBarMeta, IFootballPeriodListener, IFootballView, IAbstractPeriodView):

    def __init__(self):
        super(FootballOvertimeBar, self).__init__()
        self.__isTeam1 = False

    def _populate(self):
        super(FootballOvertimeBar, self)._populate()
        team = avatar_getter.getPlayerTeam()
        if team == 1:
            self.__isTeam1 = True
        self.as_setScoreS(0, 0)
        self.as_setVisibilityS(False)
        self.as_setTextS({'title': FOOTBALL2018.MESSAGES_FOOTBALL_OVERTIMEBAR_TITLE,
         'winOnPoints': FOOTBALL2018.MESSAGES_FOOTBALL_OVERTIMEBAR_WINONPOINTS,
         'winOnPointsEnemy': FOOTBALL2018.MESSAGES_FOOTBALL_OVERTIMEBAR_WINONPOINTSENEMY})

    def updateOvertimeScore(self, points):
        if points:
            if self.__isTeam1:
                self.as_setScoreS(points[1], points[2])
            else:
                self.as_setScoreS(points[2], points[1])

    def onStartFootballOvertime(self):
        self.as_setVisibilityS(True)
