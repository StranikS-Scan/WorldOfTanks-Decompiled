# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/storages/local_storage.py
from constants import ARENA_GUI_TYPE, QUEUE_TYPE
from gui.battle_control.arena_visitor import createByAvatar
from gui.shared.system_factory import collectCanSelectPrbEntity

class LocalStorage(object):
    __slots__ = ()

    def init(self):
        pass

    def fini(self):
        pass

    def swap(self):
        pass

    def release(self, *args):
        pass

    def suspend(self):
        pass

    def isModeSelected(self):
        return False

    def clear(self):
        pass

    def onAvatarBecomePlayer(self):
        pass


class SessionStorage(LocalStorage):
    __slots__ = ('_isSelected',)
    _GUI_TYPE = ARENA_GUI_TYPE.UNKNOWN

    def __init__(self):
        super(SessionStorage, self).__init__()
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
        arenaVisitor = createByAvatar()
        self._isSelected = self._determineSelection(arenaVisitor)

    def _determineSelection(self, arenaVisitor):
        return arenaVisitor.gui.guiType == self._GUI_TYPE


class RecentPrbStorage(LocalStorage):
    __slots__ = ('_queueType',)

    def __init__(self):
        super(RecentPrbStorage, self).__init__()
        self._queueType = QUEUE_TYPE.UNKNOWN

    @property
    def queueType(self):
        return self._queueType

    @queueType.setter
    def queueType(self, queueType):
        self._queueType = queueType

    def isModeSelected(self):
        return collectCanSelectPrbEntity(self._queueType)()

    def onAvatarBecomePlayer(self):
        arenaVisitor = createByAvatar()
        self._queueType = arenaVisitor.extra.queueType
