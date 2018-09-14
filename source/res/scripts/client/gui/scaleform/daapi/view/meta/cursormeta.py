# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CursorMeta.py
from gui.Scaleform.framework.entities.View import View

class CursorMeta(View):

    def as_setCursorS(self, cursor):
        if self._isDAAPIInited():
            return self.flashObject.as_setCursor(cursor)
