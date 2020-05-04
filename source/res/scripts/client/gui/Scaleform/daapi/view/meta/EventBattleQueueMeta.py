# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventBattleQueueMeta.py
from gui.Scaleform.daapi.view.lobby.battle_queue import BaseBattleQueue

class EventBattleQueueMeta(BaseBattleQueue):

    def moveSpace(self, x, y, delta):
        self._printOverrideError('moveSpace')

    def notifyCursorOver3dScene(self, isOver3dScene):
        self._printOverrideError('notifyCursorOver3dScene')

    def notifyCursorDragging(self, isDragging):
        self._printOverrideError('notifyCursorDragging')

    def as_setSubdivisionNameS(self, value):
        return self.flashObject.as_setSubdivisionName(value) if self._isDAAPIInited() else None
