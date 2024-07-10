# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/avatar_components/team_healthbar_mechanic.py
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as BONUS_CAPS

class TeamHealthbarMechanic(object):

    def __init__(self):
        self.__enabled = False
        self.__lastTeamHealthPercentage = None
        return

    def handleKey(self, isDown, key, mods):
        return False

    def onBecomePlayer(self):
        self.__enabled = self.hasBonusCap(BONUS_CAPS.TEAM_HEALTH_BAR)
        if not self.__enabled:
            return
        else:
            self.__lastTeamHealthPercentage = None
            return

    def onBecomeNonPlayer(self):
        if not self.__enabled:
            return
        else:
            self.__lastTeamHealthPercentage = None
            return

    def updateTeamsHealthPercentage(self, teamsHealthPercentage):
        if not self.__enabled:
            return
        self.__lastTeamHealthPercentage = teamsHealthPercentage
        self.arena.updateTeamHealthPercent(teamsHealthPercentage)

    def getHealthPercentage(self):
        return self.__lastTeamHealthPercentage
