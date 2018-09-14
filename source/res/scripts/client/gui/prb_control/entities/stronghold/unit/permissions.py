# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/stronghold/unit/permissions.py
from UnitBase import UNIT_FLAGS, UNIT_ROLE
from gui.shared.utils.decorators import ReprInjector
from gui.prb_control.entities.base.unit.permissions import UnitPermissions
from constants import CLAN_MEMBER_FLAGS

@ReprInjector.simple(('_clanRoles', 'clanRoles'), ('_isLegionary', 'isLegionary'), ('_strongholdRoles', 'strongholdRoles'), ('_isInSlot', 'isInSlot'), ('_canStealLeadership', 'canStealLeadership'), ('_isFreezed', 'isFreezed'))
class StrongholdPermissions(UnitPermissions):

    def __init__(self, roles=UNIT_ROLE.DEFAULT, flags=UNIT_FLAGS.DEFAULT, isCurrentPlayer=False, isPlayerReady=False, hasLockedState=False, clanRoles=None, strongholdRoles=None, isLegionary=False, isInSlot=False, canStealLeadership=False, isFreezed=False):
        super(StrongholdPermissions, self).__init__(roles, flags, isCurrentPlayer, isPlayerReady, hasLockedState)
        self._clanRoles = clanRoles
        self._strongholdRoles = strongholdRoles
        self._isInSlot = isInSlot
        self._isLegionary = isLegionary
        self._canStealLeadership = canStealLeadership
        self._isFreezed = isFreezed

    def isNotFreezed(self):
        return not self._isFreezed

    def isClanLead(self):
        return self._clanRoles == CLAN_MEMBER_FLAGS.LEADER and not self._isLegionary

    def isClanSubLead(self):
        return self._clanRoles == CLAN_MEMBER_FLAGS.VICE_LEADER and not self._isLegionary

    def isClanStaffOfficer(self):
        return self._clanRoles == CLAN_MEMBER_FLAGS.STAFF and not self._isLegionary

    def canStealLeadership(self):
        correctRole = self.isClanLead() or self.isClanSubLead()
        return not self._isLegionary and correctRole and self.isNotFreezed() and self._canStealLeadership

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
        if not self.isCommander(self._roles) or not self.isNotFreezed():
            return False
        else:
            if not self._isLegionary:
                if self._strongholdRoles is not None:
                    for role in self._strongholdRoles:
                        if self._clanRoles & role > 0:
                            return True

                if self.isClanLead() or self.isClanSubLead() or self.isClanStaffOfficer():
                    return True
            return False

    def canChangeUnitState(self):
        return self._roles & UNIT_ROLE.CREATOR == UNIT_ROLE.CREATOR

    def canSendInvite(self):
        return not self._isLegionary

    def canKick(self):
        return self.isCommander(self._roles) and not self._isLegionary and not self._isFreezed
