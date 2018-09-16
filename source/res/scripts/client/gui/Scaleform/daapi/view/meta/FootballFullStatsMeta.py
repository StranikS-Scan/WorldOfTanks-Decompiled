# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FootballFullStatsMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class FootballFullStatsMeta(BaseDAAPIComponent):

    def as_initDataS(self, dataVO):
        return self.flashObject.as_initData(dataVO) if self._isDAAPIInited() else None

    def as_updateBallPossessionS(self, team1, team2):
        return self.flashObject.as_updateBallPossession(team1, team2) if self._isDAAPIInited() else None

    def as_showBallPossesionS(self, visible):
        return self.flashObject.as_showBallPossesion(visible) if self._isDAAPIInited() else None

    def as_updateScoreS(self, team1, team2, both):
        return self.flashObject.as_updateScore(team1, team2, both) if self._isDAAPIInited() else None

    def as_updateWinTextS(self, winText):
        return self.flashObject.as_updateWinText(winText) if self._isDAAPIInited() else None

    def as_addGoalLeftS(self, time, playerName, vehicleType, clrSchemeName):
        return self.flashObject.as_addGoalLeft(time, playerName, vehicleType, clrSchemeName) if self._isDAAPIInited() else None

    def as_addGoalRightS(self, time, playerName, vehicleType, clrSchemeName):
        return self.flashObject.as_addGoalRight(time, playerName, vehicleType, clrSchemeName) if self._isDAAPIInited() else None
