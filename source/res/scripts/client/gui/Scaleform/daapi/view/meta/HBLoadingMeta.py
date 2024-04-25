# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/HBLoadingMeta.py
from gui.Scaleform.framework.entities.View import View

class HBLoadingMeta(View):

    def as_setDataS(self, hints):
        return self.flashObject.as_setData(hints) if self._isDAAPIInited() else None

    def as_updateProgressS(self, percent):
        return self.flashObject.as_updateProgress(percent) if self._isDAAPIInited() else None

    def as_loadedS(self):
        return self.flashObject.as_loaded() if self._isDAAPIInited() else None
