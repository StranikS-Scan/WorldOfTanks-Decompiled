# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/TeamBase.py
import BigWorld
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
CAPTURE_POINTS_LIMIT = 100.0

class TeamBase(BigWorld.Entity):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def onEnterWorld(self, prereqs):
        ctrl = self.sessionProvider.dynamic.teamBases
        if ctrl is not None:
            ctrl.addTeamBase(self)
        return

    def onBaseTeamChanged(self, baseID, team):
        ctrl = self.sessionProvider.dynamic.teamBases
        if ctrl is not None:
            ctrl.onBaseTeamChanged(baseID, team)
        return
