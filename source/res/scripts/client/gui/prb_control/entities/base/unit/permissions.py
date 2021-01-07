# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/unit/permissions.py
import account_helpers
from UnitBase import UNIT_FLAGS, UNIT_ROLE
from gui.prb_control.entities.base.permissions import IPrbPermissions
from gui.prb_control.items.unit_items import UnitFlags
from gui.shared.utils.decorators import ReprInjector

class IUnitPermissions(IPrbPermissions):

    def canKick(self):
        return False

    def canChangeUnitState(self):
        return False

    def canChangeRosters(self):
        return False

    def canSetVehicle(self):
        return False

    def canSetReady(self):
        return False

    def canChangeClosedSlots(self):
        return False

    def canAssignToSlot(self, dbID):
        return False

    def canReassignToSlot(self):
        return False

    def canChangeComment(self):
        return False

    def canStartAutoSearch(self):
        return False

    def canStopAutoSearch(self):
        return False

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

    @classmethod
    def isCommander(cls, roles):
        return False


@ReprInjector.simple(('_hasLockedState', 'hasLockedState'))
class UnitIntroPermissions(IUnitPermissions):

    def __init__(self, hasLockedState=False):
        super(UnitIntroPermissions, self).__init__()
        self._hasLockedState = hasLockedState

    def canCreateSquad(self):
        return not self._hasLockedState

    def canChangeVehicle(self):
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

    def canStartAutoSearch(self):
        return self._roles & UNIT_ROLE.START_STOP_BATTLE > 0

    def canStopAutoSearch(self):
        return self._roles & UNIT_ROLE.START_STOP_BATTLE > 0

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
