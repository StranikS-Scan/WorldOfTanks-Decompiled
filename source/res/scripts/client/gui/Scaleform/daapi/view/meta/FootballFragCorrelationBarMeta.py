# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FootballFragCorrelationBarMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class FootballFragCorrelationBarMeta(BaseDAAPIComponent):

    def as_initTeamsS(self, dataVO):
        return self.flashObject.as_initTeams(dataVO) if self._isDAAPIInited() else None

    def as_setTextS(self, dataVO):
        return self.flashObject.as_setText(dataVO) if self._isDAAPIInited() else None

    def as_updateScoreS(self, alliedScore, enemyScore):
        return self.flashObject.as_updateScore(alliedScore, enemyScore) if self._isDAAPIInited() else None

    def as_showGoalAllyS(self):
        return self.flashObject.as_showGoalAlly() if self._isDAAPIInited() else None

    def as_showGoalEnemyS(self):
        return self.flashObject.as_showGoalEnemy() if self._isDAAPIInited() else None

    def as_showGoalSelfS(self):
        return self.flashObject.as_showGoalSelf() if self._isDAAPIInited() else None

    def as_setColorBlindS(self, isColorBlind):
        return self.flashObject.as_setColorBlind(isColorBlind) if self._isDAAPIInited() else None
