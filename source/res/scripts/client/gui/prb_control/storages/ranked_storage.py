# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/storages/ranked_storage.py
from gui.prb_control.storages.local_storage import SessionStorage

class RankedStorage(SessionStorage):

    def _determineSelection(self, arenaVisitor):
        return arenaVisitor.gui.isRankedBattle()
