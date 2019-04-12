# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/CursorManagerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class CursorManagerMeta(BaseDAAPIComponent):

    def as_setCursorS(self, cursor):
        return self.flashObject.as_setCursor(cursor) if self._isDAAPIInited() else None
