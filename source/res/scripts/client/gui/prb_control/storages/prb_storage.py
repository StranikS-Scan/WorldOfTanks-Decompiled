# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/storages/prb_storage.py
from gui.prb_control.storages.local_storage import LocalStorage

class TrainingStorage(LocalStorage):
    __slots__ = ('arenaGuiType', 'isObserver')

    def __init__(self):
        super(TrainingStorage, self).__init__()
        self.arenaGuiType = None
        self.isObserver = False
        return

    def clear(self):
        self.arenaGuiType = None
        self.isObserver = False
        return

    def suspend(self):
        self.clear()
