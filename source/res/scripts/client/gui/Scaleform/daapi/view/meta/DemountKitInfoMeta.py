# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/DemountKitInfoMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class DemountKitInfoMeta(AbstractWindowView):

    def onCancelClick(self):
        self._printOverrideError('onCancelClick')

    def as_setDemountKitInfoS(self, demountKitInfo):
        return self.flashObject.as_setDemountKitInfo(demountKitInfo) if self._isDAAPIInited() else None
