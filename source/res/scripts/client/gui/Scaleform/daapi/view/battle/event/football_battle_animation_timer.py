# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/football_battle_animation_timer.py
from gui.Scaleform.daapi.view.meta.FootballBattleAnimationTimerMeta import FootballBattleAnimationTimerMeta
from gui.battle_control.controllers.football_ctrl import IFootballPeriodListener, IFootballView

class FootballBattleAnimationTimer(FootballBattleAnimationTimerMeta, IFootballView, IFootballPeriodListener):

    def updateScore(self, teamScore, scoreInfo):
        self.as_showBattleTimerS(False)

    def onReturnToPlay(self, data):
        self.as_showBattleTimerS(True)

    def onPrepareFootballOvertime(self):
        self.as_showBattleTimerS(False)

    def onStartFootballOvertime(self):
        self.as_showBattleTimerS(True)

    def _callWWISE(self, wwiseEventName):
        if wwiseEventName not in ('time_countdown', 'time_countdown_stop'):
            super(FootballBattleAnimationTimer, self)._callWWISE(wwiseEventName)
