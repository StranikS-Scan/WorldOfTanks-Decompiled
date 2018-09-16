# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/football_goal_celebration.py
from MapActivities import startActivity
from gui.battle_control.controllers.football_ctrl import IFootballView

class FootballGoalCelebration(IFootballView):

    def updateScore(self, scores, scoreInfo):
        if scoreInfo:
            pickActivity = ''
            if scoreInfo[1] == 2:
                if scoreInfo[0] == 1:
                    pickActivity = 'autogoalToRed'
                else:
                    pickActivity = 'goalToRed'
            elif scoreInfo[1] == 1:
                if scoreInfo[0] == 1:
                    pickActivity = 'autogoalToBlue'
                else:
                    pickActivity = 'goalToBlue'
            startActivity(pickActivity)
