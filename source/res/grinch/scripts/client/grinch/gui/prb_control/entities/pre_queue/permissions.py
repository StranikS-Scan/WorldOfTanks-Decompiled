# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/prb_control/entities/pre_queue/permissions.py
from gui.prb_control.entities.base.pre_queue.permissions import PreQueuePermissions
from grinch.skeletons.battle_controller import IGrinchController
from helpers import dependency

class GrinchPermissions(PreQueuePermissions):
    grinchCtrl = dependency.descriptor(IGrinchController)

    def canCreateSquad(self):
        canCreateSquad = super(GrinchPermissions, self).canCreateSquad()
        return canCreateSquad and self.grinchCtrl.isAvailable()
