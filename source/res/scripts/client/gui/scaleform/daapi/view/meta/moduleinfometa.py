# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ModuleInfoMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ModuleInfoMeta(DAAPIModule):

    def onCancelClick(self):
        self._printOverrideError('onCancelClick')

    def as_setModuleInfoS(self, moduleInfo):
        if self._isDAAPIInited():
            return self.flashObject.as_setModuleInfo(moduleInfo)
