# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/storages/selection_storage.py
from gui.prb_control.storages.local_storage import LocalStorage

class SelectionStorage(LocalStorage):
    __slots__ = ('_isSelected',)

    def __init__(self):
        super(SelectionStorage, self).__init__()
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
        self._isSelected = self._isInMode()

    def _isInMode(self):
        raise NotImplementedError
