# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/football_frag_correlation_bar.py
from gui.Scaleform.daapi.view.meta.FootballFragCorrelationBarMeta import FootballFragCorrelationBarMeta
from gui.Scaleform.locale.FOOTBALL2018 import FOOTBALL2018
from gui.battle_control import avatar_getter
from gui.battle_control.controllers.football_ctrl import IFootballView
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class FootballFragCorrelationBar(FootballFragCorrelationBarMeta, IFootballView):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(FootballFragCorrelationBar, self).__init__()
        self.__isTeam1 = False

    def _populate(self):
        super(FootballFragCorrelationBar, self)._populate()
        self.as_updateScoreS(0, 0)
        team = avatar_getter.getPlayerTeam()
        if team == 1:
            self.__isTeam1 = True
        self.as_setTextS({'goalAlly': FOOTBALL2018.MESSAGES_FOOTBALL_FRAGBAR_GOALALLY,
         'goalEnemy': FOOTBALL2018.MESSAGES_FOOTBALL_FRAGBAR_GOALENEMY,
         'goalSelf': FOOTBALL2018.MESSAGES_FOOTBALL_FRAGBAR_GOALSELF})
        self.as_initTeamsS({'alliedName': FOOTBALL2018.MESSAGES_FOOTBALL_FRAGBAR_ALLIEDNAME,
         'enemyName': FOOTBALL2018.MESSAGES_FOOTBALL_FRAGBAR_ENEMYNAME,
         'isTeam1': self.__isTeam1})

    def updateScore(self, scores, scoreInfo=None):
        team1Score, team2Score = scores
        if self.__isTeam1:
            self.as_updateScoreS(team1Score, team2Score)
        else:
            self.as_updateScoreS(team2Score, team1Score)
        if scoreInfo is not None:
            selfGoal, scoringTeam = scoreInfo
            bScoredGoalForAllyTeam = self.sessionProvider.getArenaDP().isAllyTeam(scoringTeam)
            if selfGoal:
                if not bScoredGoalForAllyTeam:
                    self.as_showGoalSelfS()
                else:
                    self.as_showGoalAllyS()
            elif bScoredGoalForAllyTeam:
                self.as_showGoalAllyS()
            else:
                self.as_showGoalEnemyS()
        return
