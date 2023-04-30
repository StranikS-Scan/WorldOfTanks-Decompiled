# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/winback/pre_queue/permissions.py
from gui.prb_control.entities.base.pre_queue.permissions import PreQueuePermissions

class WinbackPermissions(PreQueuePermissions):

    def canCreateSquad(self):
        return False

    def hasSquadArrow(self):
        return True
