# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortIntelligenceNotAvailableWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class FortIntelligenceNotAvailableWindowMeta(AbstractWindowView):

    def as_setDataS(self, value):
        """
        :param value: Represented by Array (AS)
        """
        return self.flashObject.as_setData(value) if self._isDAAPIInited() else None
