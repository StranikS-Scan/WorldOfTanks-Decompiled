# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/storages/tournament_storage.py
from gui.prb_control.storages.local_storage import LocalStorage

class TournamentStorage(LocalStorage):
    __slots__ = ('_animationIdx',)

    def __init__(self):
        super(TournamentStorage, self).__init__()
        self._animationIdx = 0

    def fini(self):
        super(TournamentStorage, self).fini()
        self.clear()

    def clear(self):
        super(TournamentStorage, self).clear()
        self._animationIdx = 0

    def suspend(self):
        super(TournamentStorage, self).suspend()
        self._animationIdx = 0

    def setActiveAnimationIdx(self, animIdx):
        self._animationIdx = animIdx

    def getActiveAnimationIdx(self):
        return self._animationIdx
