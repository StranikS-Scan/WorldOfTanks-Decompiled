# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/UnboundInjectWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class UnboundInjectWindowMeta(AbstractWindowView):

    def as_setDataS(self, image, label):
        return self.flashObject.as_setData(image, label) if self._isDAAPIInited() else None
