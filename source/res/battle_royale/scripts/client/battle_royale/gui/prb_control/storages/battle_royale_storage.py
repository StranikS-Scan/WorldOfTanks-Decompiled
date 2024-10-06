# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/prb_control/storages/battle_royale_storage.py
from gui.prb_control.storages.local_storage import SessionStorage

class BattleRoyaleStorage(SessionStorage):

    def _determineSelection(self, arenaVisitor):
        return arenaVisitor.gui.isBattleRoyale()
