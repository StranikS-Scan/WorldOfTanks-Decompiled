# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/battle_royale_tournament/pre_queue/permissions.py
from gui.prb_control.entities.base.pre_queue.permissions import PreQueuePermissions

class BattleRoyaleTournamentPermissions(PreQueuePermissions):

    def canCreateSquad(self):
        return False
