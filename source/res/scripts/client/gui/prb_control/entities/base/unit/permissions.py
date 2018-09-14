# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/unit/permissions.py
import account_helpers
from UnitBase import UNIT_FLAGS, UNIT_ROLE
from gui.prb_control.entities.base.permissions import IPrbPermissions
from gui.prb_control.items.unit_items import UnitFlags
from gui.shared.utils.decorators import ReprInjector

class IUnitPermissions(IPrbPermissions):
    """
    Base unit permission interface.
    """

    def canKick(self):
        """
        Can this player kick another one.
        """
        return False

    def canChangeUnitState(self):
        """
        Can this player change unit state to ready/not ready
        """
        return False

    def canChangeRosters(self):
        """
        Can this player change slots rosters
        """
        return False

    def canSetVehicle(self):
        """
        Can this player select vehicle to participate
        """
        return False

    def canSetReady(self):
        """
        Can this player set himself ready/not ready
        """
        return False

    def canChangeClosedSlots(self):
        """
        Can this player open/close slots
        """
        return False

    def canAssignToSlot(self, dbID):
        """
        Can this player with given ID assign to any slot
        """
        return False

    def canReassignToSlot(self):
        """
        Can this player reassign to another slot
        """
        return False

    def canChangeComment(self):
        """
        Can this player change unit's comment
        """
        return False

    def canInvokeAutoSearch(self):
        """
        Can this player start auto search
        """
        return True

    def canStartBattleQueue(self):
        """
        Can this player enqueue
        """
        return False

    def canStopBattleQueue(self):
        """
        Can this player dequeue
        """
        return False

    def canChangeLeadership(self):
        """
        Can this player change commander of this unit
        """
        return False

    def canStealLeadership(self):
        """
        Can this player set himself unit's commander
        """
        return False

    def canChangeConsumables(self):
        """
        Can this player set battle consumables
        """
        return False

    def canLead(self):
        """
        Can this player take leadership
        """
        return False

    @classmethod
    def isCommander(cls, roles):
        """
        Is player with given roles - unit's commander
        Args:
            roles: roles mask
        """
        return False


@ReprInjector.simple(('_hasLockedState', 'hasLockedState'))
class UnitIntroPermissions(IUnitPermissions):

    def __init__(self, hasLockedState=False):
        super(UnitIntroPermissions, self).__init__()
        self._hasLockedState = hasLockedState

    def canCreateSquad(self):
        return not self._hasLockedState


@ReprInjector.simple(('_roles', 'roles'), ('_flags', 'flags'), ('_isCurrentPlayer', 'isCurrentPlayer'), ('_isPlayerReady', 'isPlayerReady'), ('_hasLockedState', 'hasLockedState'))
class UnitPermissions(IUnitPermissions):

    def __init__(self, roles=0, flags=UNIT_FLAGS.DEFAULT, isCurrentPlayer=False, isPlayerReady=False, hasLockedState=False):
        super(UnitPermissions, self).__init__()
        self._roles = roles
        self._flags = UnitFlags(flags)
        self._isCurrentPlayer = isCurrentPlayer
        self._isPlayerReady = isPlayerReady
        self._hasLockedState = hasLockedState

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

    @classmethod
    def isCommander(cls, roles):
        return roles & UNIT_ROLE.CREATOR == UNIT_ROLE.CREATOR
