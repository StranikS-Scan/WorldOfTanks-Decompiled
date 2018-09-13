# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/BaseDAAPIModuleMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class BaseDAAPIModuleMeta(DAAPIModule):

    def as_populateS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_populate()

    def as_disposeS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_dispose()
