# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CursorMeta.py
from gui.Scaleform.framework.entities.View import View

class CursorMeta(View):

    def as_setCursorS(self, cursor):
        return self.flashObject.as_setCursor(cursor) if self._isDAAPIInited() else None

    def as_showCursorS(self):
        return self.flashObject.as_showCursor() if self._isDAAPIInited() else None

    def as_hideCursorS(self):
        return self.flashObject.as_hideCursor() if self._isDAAPIInited() else None
