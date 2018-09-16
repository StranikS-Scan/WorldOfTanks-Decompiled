# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/stronghold/unit/permissions.py
from UnitBase import UNIT_FLAGS, UNIT_ROLE
from gui.shared.utils.decorators import ReprInjector
from gui.prb_control.entities.base.unit.permissions import UnitPermissions
from constants import CLAN_MEMBER_FLAGS

@ReprInjector.simple(('_clanRoles', 'clanRoles'), ('_isLegionary', 'isLegionary'), ('_strongholdManageReservesRoles', 'strongholdManageReservesRoles'), ('_strongholdStealLeadershipRoles', 'strongholdStealLeadershipRoles'), ('_isInSlot', 'isInSlot'), ('_isInIdle', 'isInIdle'), ('_isEquipmentCommander', 'isEquipmentCommander'), ('_isFreezed', 'isFreezed'))
class StrongholdPermissions(UnitPermissions):

    def __init__(self, roles=UNIT_ROLE.DEFAULT, flags=UNIT_FLAGS.DEFAULT, isCurrentPlayer=False, isPlayerReady=False, hasLockedState=False, clanRoles=None, strongholdManageReservesRoles=None, isLegionary=False, isInSlot=False, isInIdle=False, isFreezed=False, strongholdStealLeadershipRoles=None):
        super(StrongholdPermissions, self).__init__(roles, flags, isCurrentPlayer, isPlayerReady, hasLockedState)
        self._clanRoles = clanRoles
        self._strongholdManageReservesRoles = strongholdManageReservesRoles or []
        self._strongholdStealLeadershipRoles = strongholdStealLeadershipRoles or []
        self._isInSlot = isInSlot
        self._isLegionary = isLegionary
        self._isInIdle = isInIdle
        self._isFreezed = isFreezed

    def isNotFreezed(self):
        return not self._isFreezed

    def isInIdle(self):
        return self._isInIdle

    def isClanLead(self):
        return self._clanRoles == CLAN_MEMBER_FLAGS.LEADER and not self._isLegionary

    def isClanSubLead(self):
        return self._clanRoles == CLAN_MEMBER_FLAGS.VICE_LEADER and not self._isLegionary

    def isClanStaffOfficer(self):
        return self._clanRoles == CLAN_MEMBER_FLAGS.STAFF and not self._isLegionary

    def canStealLeadership(self):
        if self.isCommander(self._roles) or not self.isNotFreezed() or self.isInIdle() or self._isLegionary:
            return False
        for role in self._strongholdStealLeadershipRoles:
            if self._clanRoles & role > 0:
                return True

        return False

    def canChangeLeadership(self):
        return (not self._isLegionary or self.isCommander(self._roles)) and self.isNotFreezed()

    def canAssignToSlot(self, dbID):
        return super(StrongholdPermissions, self).canAssignToSlot(dbID) and self.isNotFreezed()

    def canReassignToSlot(self):
        return super(StrongholdPermissions, self).canReassignToSlot() and self.isNotFreezed()

    def canSetVehicle(self):
        canChange = self.isNotFreezed() or not self._isInSlot
        return super(StrongholdPermissions, self).canSetVehicle() and canChange

    def canChangeConsumables(self):
        if not self.isCommander(self._roles) or not self.isNotFreezed() or self._isLegionary:
            return False
        for role in self._strongholdManageReservesRoles:
            if self._clanRoles & role > 0:
                return True

        return False

    def canChangeUnitState(self):
        return self.isCommander(self._roles) and not self._isLegionary

    def canSendInvite(self):
        return not self._isLegionary

    def canKick(self):
        return self.isCommander(self._roles) and not self._isLegionary

    def canChangeExtraEquipmentRole(self):
        return self.isCommander(self._roles) and not self._isLegionary and self.isNotFreezed()

    def isEquipmentCommander(self):
        return self._roles & UNIT_ROLE.CAN_USE_EXTRA_EQUIPMENTS > 0
