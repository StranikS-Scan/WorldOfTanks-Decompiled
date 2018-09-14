# Embedded file name: scripts/client/gui/prb_control/restrictions/permissions.py
from UnitBase import UNIT_ROLE, UNIT_FLAGS
import account_helpers
from constants import PREBATTLE_ROLE, PREBATTLE_TEAM_STATE, QUEUE_TYPE, FALLOUT_BATTLE_TYPE
from constants import PREBATTLE_ACCOUNT_STATE
from gui.prb_control import prb_getters
from gui.prb_control.items.prb_items import TeamStateInfo
from gui.prb_control.items.unit_items import UnitFlags
from gui.prb_control.restrictions import interfaces
from gui.prb_control.restrictions import limits
from gui.prb_control.storage import prequeue_storage_getter

class IntroPrbPermissions(interfaces.IPrbPermissions):

    def canCreateSquad(self):
        return True


class DefaultPrbPermissions(interfaces.IPrbPermissions):

    def __init__(self, roles = 0, pState = PREBATTLE_ACCOUNT_STATE.UNKNOWN, teamState = None, hasLockedState = False):
        super(DefaultPrbPermissions, self).__init__()
        self._roles = roles
        self._pState = pState
        self._hasLockedState = hasLockedState
        if teamState is None:
            self._teamState = TeamStateInfo(PREBATTLE_TEAM_STATE.NOT_READY)
        else:
            self._teamState = teamState
        return

    def __repr__(self):
        return '{0:>s}(roles = {1:n}, pState = {2:n}, teamState = {2!r:s})'.format(self.__class__.__name__, self._roles, self._pState, self._teamState)

    def canCreateSquad(self):
        return not self._hasLockedState

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
        clientPrb = prb_getters.getClientPrebattle()
        result = False
        if clientPrb is not None:
            settings = prb_getters.getPrebattleSettings(prebattle=clientPrb)
            rosters = prb_getters.getPrebattleRosters(prebattle=clientPrb)
            result, _ = limits.TotalMaxCount().check(rosters, 1, settings.getTeamLimits(1))
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
            clientPrb = prb_getters.getClientPrebattle()
            result = False
            if clientPrb is not None:
                settings = prb_getters.getPrebattleSettings(prebattle=clientPrb)
                rosters = prb_getters.getPrebattleRosters(prebattle=clientPrb)
                prbType = prb_getters.getPrebattleType(clientPrb, settings)
                result, _ = limits.TeamNoPlayersInBattle(prbType).check(rosters, team, settings.getTeamLimits(team))
            return result

    def _canAddPlayers(self):
        clientPrb = prb_getters.getClientPrebattle()
        result = False
        if clientPrb is not None:
            settings = prb_getters.getPrebattleSettings(prebattle=clientPrb)
            rosters = prb_getters.getPrebattleRosters(prebattle=clientPrb)
            result, _ = limits.MaxCount().check(rosters, 1, settings.getTeamLimits(1))
        return result


class IntroUnitPermissions(interfaces.IUnitPermissions):

    def canCreateSquad(self):
        return True


class UnitPermissions(interfaces.IUnitPermissions):

    def __init__(self, roles = 0, flags = UNIT_FLAGS.DEFAULT, isCurrentPlayer = False, isPlayerReady = False, hasLockedState = False):
        super(UnitPermissions, self).__init__()
        self._roles = roles
        self._flags = UnitFlags(flags)
        self._isCurrentPlayer = isCurrentPlayer
        self._isPlayerReady = isPlayerReady
        self._hasLockedState = hasLockedState

    def __repr__(self):
        return '{0:>s}(roles = {1:n}, state = {2!r:s}, isCurrentPlayer = {3!r:s})'.format(self.__class__.__name__, self._roles, self._flags, self._isCurrentPlayer)

    def canCreateSquad(self):
        return not self._hasLockedState

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
        return self._roles & UNIT_ROLE.ADD_REMOVE_MEMBERS > 0 or dbID == account_helpers.getAccountDatabaseID()

    def canReassignToSlot(self):
        return self._roles & UNIT_ROLE.ADD_REMOVE_MEMBERS > 0

    def canChangeComment(self):
        return self._roles & UNIT_ROLE.CHANGE_ROSTER > 0 and not self._flags.isInIdle()

    def canInvokeAutoSearch(self):
        return self._roles & UNIT_ROLE.START_STOP_BATTLE > 0 and not self._flags.isInArena()

    def canStartBattleQueue(self):
        return self._roles & UNIT_ROLE.START_STOP_BATTLE > 0

    def canStopBattleQueue(self):
        return self._roles & UNIT_ROLE.START_STOP_BATTLE > 0 and not self._flags.isInArena()

    def canChangeVehicle(self):
        return self._isCurrentPlayer and not self._isPlayerReady

    def canChangeLeadership(self):
        return self._roles & UNIT_ROLE.CHANGE_LEADERSHIP > 0

    def canStealLeadership(self):
        return self.canChangeLeadership()

    def canChangeConsumables(self):
        return self._roles & UNIT_ROLE.CHANGE_ROSTER > 0

    def canLead(self):
        return self._roles & UNIT_ROLE.CAN_LEAD > 0

    def canChangeRated(self):
        return self._roles & UNIT_ROLE.CHANGE_ROSTER > 0

    @classmethod
    def isCreator(cls, roles):
        return roles & UNIT_ROLE.CREATOR == UNIT_ROLE.CREATOR


class SquadPermissions(UnitPermissions):

    def canChangeLeadership(self):
        return True

    def canStealLeadership(self):
        return False

    def canExitFromQueue(self):
        return self.isCreator(self._roles)


class PreQueuePermissions(interfaces.IGUIPermissions):

    def __init__(self, isInQueue):
        super(PreQueuePermissions, self).__init__()
        self.__isInQueue = isInQueue

    def canChangeVehicle(self):
        return not self.__isInQueue

    def canCreateSquad(self):
        return not self.__isInQueue


class FalloutQueuePermissions(PreQueuePermissions):

    @prequeue_storage_getter(QUEUE_TYPE.EVENT_BATTLES)
    def storage(self):
        return None

    def canCreateSquad(self):
        canDo = super(FalloutQueuePermissions, self).canCreateSquad()
        if canDo:
            canDo = self.storage.getBattleType() != FALLOUT_BATTLE_TYPE.UNDEFINED
        return canDo
