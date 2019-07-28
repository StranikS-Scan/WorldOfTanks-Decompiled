# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/storages/ranked_storage.py
from gui.battle_control.arena_visitor import createByAvatar
from gui.prb_control.storages.selection_storage import SelectionStorage

class RankedStorage(SelectionStorage):

    def _isInMode(self):
        arenaVisitor = createByAvatar()
        return arenaVisitor.gui.isRankedBattle()
