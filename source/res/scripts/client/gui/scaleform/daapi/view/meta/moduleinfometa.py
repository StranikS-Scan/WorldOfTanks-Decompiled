# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ModuleInfoMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class ModuleInfoMeta(AbstractWindowView):

    def onCancelClick(self):
        self._printOverrideError('onCancelClick')

    def as_setModuleInfoS(self, moduleInfo):
        return self.flashObject.as_setModuleInfo(moduleInfo) if self._isDAAPIInited() else None
