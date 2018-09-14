# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/legacy/permissions.py
from constants import PREBATTLE_ACCOUNT_STATE, PREBATTLE_ROLE, PREBATTLE_TEAM_STATE
from gui.prb_control.entities.base.permissions import IPrbPermissions
from gui.prb_control.items.prb_items import TeamStateInfo
from gui.shared.utils.decorators import ReprInjector

class ILegacyPermissions(IPrbPermissions):
    """
    Base legacy prebattle permission interface.
    """

    def canKick(self, team=1):
        """
        Can current player kick player from given team.
        Args:
            team: team to check permission
        """
        return False

    def canAssignToTeam(self, team=1):
        """
        Can current player assign player to given team.
        Args:
            team: team to check permission
        """
        return False

    def canChangePlayerTeam(self):
        """
        Can current player change player's team.
        """
        return False

    def canSetTeamState(self, team=1):
        """
        Can current player change state of given team.
        Args:
            team: team to check permission
        """
        return False

    def canMakeOpenedClosed(self):
        """
        Can current player change room's open state.
        """
        return False

    def canChangeComment(self):
        """
        Can current player change room's comment.
        """
        return False

    def canChangeArena(self):
        """
        Can current player change room's map.
        """
        return False

    def canChangeArenaVOIP(self):
        """
        Can current player change voice chat availability setting.
        """
        return False

    def canChangeDivision(self):
        """
        Can current player change division for legacy.
        """
        return False

    def canChangeGamePlayMask(self):
        """
        Can current player change room's gameplay mode.
        """
        return False

    def canChangeSetting(self):
        """
        Can current player change room's setting.
        """
        return False

    def canStartBattle(self):
        """
        Can current player start battle.
        """
        return False

    @classmethod
    def isCreator(cls, roles):
        """
        Is player with given role - room's creator.
        Args:
            roles: roles mask to check
        """
        return False


class LegacyIntroPermissions(ILegacyPermissions):

    def canCreateSquad(self):
        """
        Can current player create squad
        """
        return True


@ReprInjector.simple(('_roles', 'roles'), ('_pState', 'pState'), ('_teamState', 'teamState'))
class LegacyPermissions(ILegacyPermissions):
    """
    Class for legacy room permissions.
    """

    def __init__(self, roles=0, pState=PREBATTLE_ACCOUNT_STATE.UNKNOWN, teamState=None, hasLockedState=False):
        super(LegacyPermissions, self).__init__()
        self._roles = roles
        self._pState = pState
        self._hasLockedState = hasLockedState
        if teamState is None:
            self._teamState = TeamStateInfo(PREBATTLE_TEAM_STATE.NOT_READY)
        else:
            self._teamState = teamState
        return

    def canCreateSquad(self):
        return not self._hasLockedState

    def canSendInvite(self):
        return self._roles & PREBATTLE_ROLE.INVITE != 0 and self._teamState.isNotReady()

    def canKick(self, team=1):
        result = False
        if team is 1:
            result = self._roles & PREBATTLE_ROLE.KICK_1 != 0
        elif team is 2:
            result = self._roles & PREBATTLE_ROLE.KICK_2 != 0
        return result

    def canAssignToTeam(self, team=1):
        if self._teamState.isInQueue():
            return False
        result = False
        if team is 1:
            result = self._roles & PREBATTLE_ROLE.ASSIGNMENT_1 != 0
        elif team is 2:
            result = self._roles & PREBATTLE_ROLE.ASSIGNMENT_2 != 0
        return result

    def canChangePlayerTeam(self):
        return self._roles & PREBATTLE_ROLE.ASSIGNMENT_1_2 != 0

    def canSetTeamState(self, team=1):
        result = False
        if team is 1:
            result = self._roles & PREBATTLE_ROLE.TEAM_READY_1 != 0
        elif team is 2:
            result = self._roles & PREBATTLE_ROLE.TEAM_READY_2 != 0
        return result

    def canMakeOpenedClosed(self):
        return self._roles & PREBATTLE_ROLE.OPEN_CLOSE != 0

    def canChangeComment(self):
        return self._roles & PREBATTLE_ROLE.CHANGE_COMMENT != 0

    def canChangeArena(self):
        return self._roles & PREBATTLE_ROLE.CHANGE_ARENA != 0

    def canChangeArenaVOIP(self):
        return self._roles & PREBATTLE_ROLE.CHANGE_ARENA_VOIP != 0

    def canChangeGamePlayMask(self):
        return self._roles & PREBATTLE_ROLE.CHANGE_GAMEPLAYSMASK != 0

    def canChangeVehicle(self):
        return self._pState & PREBATTLE_ACCOUNT_STATE.READY == 0 and (not self._teamState.state or self._teamState.isNotReady())
