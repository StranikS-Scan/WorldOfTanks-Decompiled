# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/TeamBase.py
import BigWorld

class TeamBase(BigWorld.Entity):

    def updateCapturingInfo(self, baseID, team, info):
        points, timeLeft, invadersCnt, capturingStopped = info
        BigWorld.player().arena.onTeamBasePointsUpdate(team, baseID, points, timeLeft, invadersCnt, capturingStopped)

    def onCaptured(self, baseID, team):
        BigWorld.player().arena.onTeamBaseCaptured(team, baseID)
