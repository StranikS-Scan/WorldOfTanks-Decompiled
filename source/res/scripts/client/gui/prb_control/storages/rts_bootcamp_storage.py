# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/storages/rts_bootcamp_storage.py
from gui.prb_control.storages.local_storage import SessionStorage

class RTSBootcampStorage(SessionStorage):
    __slots__ = ('errors',)

    def __init__(self):
        super(RTSBootcampStorage, self).__init__()
        self.errors = {}

    def clear(self):
        super(RTSBootcampStorage, self).clear()
        self.errors.clear()

    def _determineSelection(self, arenaVisitor):
        return arenaVisitor.gui.isRTSBootcamp()
