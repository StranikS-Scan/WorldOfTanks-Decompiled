# Embedded file name: scripts/client/gui/prb_control/restrictions/interfaces.py


class IGUIPermissions(object):

    def canExitFromQueue(self):
        return True

    def canChangeVehicle(self):
        return True

    def canSendInvite(self):
        return False

    def canCreateSquad(self):
        return False


class IPrbPermissions(IGUIPermissions):

    def canKick(self, team = 1):
        return False

    def canAssignToTeam(self, team = 1):
        return False

    def canChangePlayerTeam(self):
        return False

    def canSetTeamState(self, team = 1):
        return False

    def canMakeOpenedClosed(self):
        return False

    def canChangeComment(self):
        return False

    def canChangeArena(self):
        return False

    def canChangeArenaVOIP(self):
        return False

    def canChangeDivision(self):
        return False

    def canChangeGamePlayMask(self):
        return False

    def canChangeSetting(self):
        return False

    def canStartBattle(self):
        return False

    @classmethod
    def isCreator(cls, roles):
        return False


class IUnitPermissions(IGUIPermissions):

    def canKick(self):
        return False

    def canChangeUnitState(self):
        return False

    def canChangeRosters(self):
        return False

    def canSetVehicle(self):
        return False

    def canChangeClosedSlots(self):
        return False

    def canAssignToSlot(self, dbID):
        return False

    def canReassignToSlot(self):
        return False

    def canChangeComment(self):
        return False

    def canInvokeAutoSearch(self):
        return True

    def canStartBattleQueue(self):
        return False

    def canStopBattleQueue(self):
        return False

    def canChangeLeadership(self):
        return False

    def canStealLeadership(self):
        return False

    def canChangeConsumables(self):
        return False

    def canLead(self):
        return False

    def canChangeRated(self):
        return False

    @classmethod
    def isCreator(cls, roles):
        return False


class IVehicleLimit(object):

    def check(self, teamLimits):
        return (True, '')


class ITeamLimit(object):

    def check(self, rosters, team, teamLimits):
        return (True, '')
