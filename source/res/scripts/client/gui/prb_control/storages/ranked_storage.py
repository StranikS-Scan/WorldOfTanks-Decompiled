# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/storages/ranked_storage.py
from gui.battle_control.arena_visitor import createByAvatar
from gui.prb_control.storages.local_storage import LocalStorage

class RankedStorage(LocalStorage):
    """
    This storage hold session-like ranked battle selection. No server or client physical storage,
    only per-launch basis and per-battle selection.
    """
    __slots__ = ('_isSelected',)

    def __init__(self):
        super(RankedStorage, self).__init__()
        self._isSelected = False

    def clear(self):
        self._isSelected = False

    def release(self):
        self._isSelected = True

    def suspend(self):
        self.clear()

    def isModeSelected(self):
        return self._isSelected

    def onAvatarBecomePlayer(self):
        """
        This method is needed for settings storage state in selected mode
        to get player back into ranked from battle.
        """
        arenaVisitor = createByAvatar()
        self._isSelected = arenaVisitor.gui.isRankedBattle()
