# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/LegalInfoWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class LegalInfoWindowMeta(AbstractWindowView):

    def getLegalInfo(self):
        self._printOverrideError('getLegalInfo')

    def onCancelClick(self):
        self._printOverrideError('onCancelClick')

    def as_setLegalInfoS(self, legalInfo):
        return self.flashObject.as_setLegalInfo(legalInfo) if self._isDAAPIInited() else None
