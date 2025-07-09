# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/ranked/pre_queue/permissions.py
from gui.prb_control.entities.base.pre_queue.permissions import PreQueuePermissions
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController

class RankedPermissions(PreQueuePermissions):
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def canSendInvite(self):
        return True

    def canCreateSquad(self):
        return False if not self.__rankedController.hasSuitableVehicles() else super(RankedPermissions, self).canCreateSquad()
