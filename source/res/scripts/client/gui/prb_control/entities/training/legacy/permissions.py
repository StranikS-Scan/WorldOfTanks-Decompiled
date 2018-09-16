# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/training/legacy/permissions.py
from constants import PREBATTLE_ROLE
from gui.prb_control.entities.base.legacy.permissions import LegacyPermissions

class TrainingPermissions(LegacyPermissions):

    def canChangeVehicle(self):
        return True

    @classmethod
    def isCreator(cls, roles):
        return roles == PREBATTLE_ROLE.TRAINING_CREATOR

    def canChangeSetting(self):
        return self.canChangeComment() or self.canChangeArena() or self.canMakeOpenedClosed()

    def canStartBattle(self):
        return self.canSetTeamState(1) and self.canSetTeamState(2)
