# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/team_healthbar_mechanic.py
from debug_utils import LOG_DEBUG_DEV
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as BONUS_CAPS

class TeamHealthbarMechanic(object):

    def __init__(self):
        self.__enabled = False
        self.__lastTeamHealthPercentage = None
        return

    def onBecomePlayer(self):
        self.__enabled = BONUS_CAPS.checkAny(self.arenaBonusType, BONUS_CAPS.TEAM_HEALTH_BAR)
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
