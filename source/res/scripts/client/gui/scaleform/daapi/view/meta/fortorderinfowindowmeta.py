# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortOrderInfoWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class FortOrderInfoWindowMeta(AbstractWindowView):

    def as_setWindowDataS(self, data):
        return self.flashObject.as_setWindowData(data) if self._isDAAPIInited() else None

    def as_setDynPropertiesS(self, data):
        return self.flashObject.as_setDynProperties(data) if self._isDAAPIInited() else None
