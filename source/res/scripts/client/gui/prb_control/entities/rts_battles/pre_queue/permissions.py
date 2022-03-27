# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/rts_battles/pre_queue/permissions.py
from gui.prb_control.entities.base.pre_queue.permissions import PreQueuePermissions

class RTSPermissions(PreQueuePermissions):

    def canCreateSquad(self):
        return False

    def canAppeal(self):
        return False
