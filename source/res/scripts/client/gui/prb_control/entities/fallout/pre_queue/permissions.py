# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/fallout/pre_queue/permissions.py
from constants import QUEUE_TYPE
from gui.prb_control.entities.base.pre_queue.permissions import PreQueuePermissions
from gui.prb_control.storages import prequeue_storage_getter

class FalloutPermissions(PreQueuePermissions):

    @prequeue_storage_getter(QUEUE_TYPE.FALLOUT)
    def storage(self):
        return None

    def canCreateSquad(self):
        canDo = super(FalloutPermissions, self).canCreateSquad()
        if canDo:
            canDo = self.storage.getBattleType() in QUEUE_TYPE.FALLOUT
        return canDo
