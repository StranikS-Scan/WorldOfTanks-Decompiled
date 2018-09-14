# Embedded file name: scripts/client/gui/prb_control/restrictions/permissions.py
from UnitBase import UNIT_ROLE, UNIT_STATE
import account_helpers
from constants import PREBATTLE_ROLE, PREBATTLE_TEAM_STATE
from constants import PREBATTLE_ACCOUNT_STATE
from gui import prb_control
from gui.prb_control.items.prb_items import TeamStateInfo
from gui.prb_control.items.unit_items import UnitState
from gui.prb_control.restrictions.interfaces import IPrbPermissions, IUnitPermissions
from gui.prb_control.restrictions.limits import MaxCount, TotalMaxCount, TeamNoPlayersInBattle

class DefaultPrbPermissions(IPrbPermissions):

    def __init__(self, roles = 0, pState = PREBATTLE_ACCOUNT_STATE.UNKNOWN, teamState = None):
        super(DefaultPrbPermissions, self).__init__()
        self._roles = roles
        self._pState = pState
        if teamState is None:
            self._teamState = TeamStateInfo(PREBATTLE_TEAM_STATE.NOT_READY)
        else:
            self._teamState = teamState
        return

    def __repr__(self):
        return '{0:>s}(roles = {1:n}, pState = {2:n}, teamState = {2!r:s})'.format(self.__class__.__name__, self._roles, self._pState, self._teamState)

    def canSendInvite(self):
        return self._roles & PREBATTLE_ROLE.INVITE != 0 and self._teamState.isNotReady()

    def canKick(self, team = 1):
        result = False
        if team is 1:
            result = self._roles & PREBATTLE_ROLE.KICK_1 != 0
        elif team is 2:
            result = self._roles & PREBATTLE_ROLE.KICK_2 != 0
        return result

    def canAssignToTeam(self, team = 1):
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

    def canSetTeamState(self, team = 1):
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

    @classmethod
    def isCreator(cls, roles):
        return False


class TrainingPrbPermissions(DefaultPrbPermissions):

    def canChangeVehicle(self):
        return True

    @classmethod
    def isCreator(cls, roles):
        return roles == PREBATTLE_ROLE.TRAINING_CREATOR

    def canChangeSetting(self):
        return self.canChangeComment() or self.canChangeArena() or self.canMakeOpenedClosed()

    def canStartBattle(self):
        return self.canSetTeamState(1) and self.canSetTeamState(2)


class SquadPrbPermissions(DefaultPrbPermissions):

    def canSendInvite(self):
        return super(SquadPrbPermissions, self).canSendInvite() and self._canAddPlayers()

    def canAssignToTeam(self, team = 1):
        return False

    def canChangePlayerTeam(self):
        return False

    def canExitFromQueue(self):
        return self.isCreator(self._roles)

    @classmethod
    def isCreator(cls, roles):
        return roles == PREBATTLE_ROLE.SQUAD_CREATOR

    def _canAddPlayers(self):
        clientPrb = prb_control.getClientPrebattle()
        result = False
        if clientPrb is not None:
            settings = prb_control.getPrebattleSettings(prebattle=clientPrb)
            rosters = prb_control.getPrebattleRosters(prebattle=clientPrb)
            result, _ = MaxCount().check(rosters, 1, settings.getTeamLimits(1))
        return result


class CompanyPrbPermissions(DefaultPrbPermissions):

    def canSendInvite(self):
        return super(CompanyPrbPermissions, self).canSendInvite() and self._canAddPlayers()

    def canChangeDivision(self):
        return self._roles & PREBATTLE_ROLE.CHANGE_DIVISION != 0 and self._teamState.isNotReady()

    def canExitFromQueue(self):
        return self.isCreator(self._roles)

    @classmethod
    def isCreator(cls, roles):
        return roles == PREBATTLE_ROLE.COMPANY_CREATOR

    def _canAddPlayers(self):
        clientPrb = prb_control.getClientPrebattle()
        result = False
        if clientPrb is not None:
            settings = prb_control.getPrebattleSettings(prebattle=clientPrb)
            rosters = prb_control.getPrebattleRosters(prebattle=clientPrb)
            result, _ = TotalMaxCount().check(rosters, 1, settings.getTeamLimits(1))
        return result


class BattleSessionPrbPermissions(DefaultPrbPermissions):

    def canSendInvite(self):
        return super(BattleSessionPrbPermissions, self).canSendInvite() and self._canAddPlayers()

    def canExitFromQueue(self):
        return self.isCreator(self._roles)

    @classmethod
    def isCreator(cls, roles):
        return False

    def canAssignToTeam(self, team = 1):
        result = super(BattleSessionPrbPermissions, self).canAssignToTeam(team)
        if not result:
            return False
        else:
            clientPrb = prb_control.getClientPrebattle()
            result = False
            if clientPrb is not None:
                settings = prb_control.getPrebattleSettings(prebattle=clientPrb)
                rosters = prb_control.getPrebattleRosters(prebattle=clientPrb)
                prbType = prb_control.getPrebattleType(clientPrb, settings)
                result, _ = TeamNoPlayersInBattle(prbType).check(rosters, team, settings.getTeamLimits(team))
            return result

    def _canAddPlayers(self):
        clientPrb = prb_control.getClientPrebattle()
        result = False
        if clientPrb is not None:
            settings = prb_control.getPrebattleSettings(prebattle=clientPrb)
            rosters = prb_control.getPrebattleRosters(prebattle=clientPrb)
            result, _ = MaxCount().check(rosters, 1, settings.getTeamLimits(1))
        return result


class UnitPermissions(IUnitPermissions):

    def __init__(self, roles = 0, state = UNIT_STATE.DEFAULT, isCurrentPlayer = False, isPlayerReady = False):
        super(UnitPermissions, self).__init__()
        self._roles = roles
        self._state = UnitState(state)
        self._isCurrentPlayer = isCurrentPlayer
        self._isPlayerReady = isPlayerReady

    def __repr__(self):
        return '{0:>s}(roles = {1:n}, state = {2!r:s}, isCurrentPlayer = {3!r:s})'.format(self.__class__.__name__, self._roles, self._state, self._isCurrentPlayer)

    def canSendInvite(self):
        return self._roles & UNIT_ROLE.INVITE_KICK_PLAYERS > 0

    def canKick(self):
        return self._roles & UNIT_ROLE.INVITE_KICK_PLAYERS > 0

    def canChangeUnitState(self):
        return self._roles & UNIT_ROLE.CHANGE_ROSTER > 0

    def canChangeRosters(self):
        return self._roles & UNIT_ROLE.CHANGE_ROSTER > 0

    def canSetVehicle(self):
        return self._isCurrentPlayer

    def canSetReady(self):
        return self._isCurrentPlayer

    def canChangeClosedSlots(self):
        return self._roles & UNIT_ROLE.CHANGE_ROSTER > 0

    def canAssignToSlot(self, dbID):
        return self._roles & UNIT_ROLE.ADD_REMOVE_MEMBERS > 0 or dbID == account_helpers.getPlayerDatabaseID()

    def canReassignToSlot(self):
        return self._roles & UNIT_ROLE.ADD_REMOVE_MEMBERS > 0

    def canChangeComment(self):
        return self._roles & UNIT_ROLE.CHANGE_ROSTER > 0 and not self._state.isInIdle()

    def canInvokeAutoSearch(self):
        return self._roles & UNIT_ROLE.START_STOP_BATTLE > 0

    def canStartBattleQueue(self):
        return self._roles & UNIT_ROLE.START_STOP_BATTLE > 0

    def canStopBattleQueue(self):
        return self._roles & UNIT_ROLE.START_STOP_BATTLE > 0

    def canChangeVehicle(self):
        return self._isCurrentPlayer and not self._isPlayerReady and not self._state.isInQueue()

    def canGiveLeadership(self):
        return self.isCreator(self._roles)

    def canTakeLeadership(self):
        return not self._roles & UNIT_ROLE.LEGIONARY > 0

    @classmethod
    def isCreator(cls, roles):
        return roles & UNIT_ROLE.COMMANDER_UPDATES > 0
