# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/storages/rts_1vs1_battle_storage.py
from gui.prb_control.storages.local_storage import SessionStorage
from constants import ARENA_BONUS_TYPE

class RTS1x1BattlesStorage(SessionStorage):

    def __init__(self):
        super(RTS1x1BattlesStorage, self).__init__()
        self.errors = {}

    def clear(self):
        super(RTS1x1BattlesStorage, self).clear()
        self.errors.clear()

    def _determineSelection(self, arenaVisitor):
        return arenaVisitor.getArenaBonusType() == ARENA_BONUS_TYPE.RTS_1x1
