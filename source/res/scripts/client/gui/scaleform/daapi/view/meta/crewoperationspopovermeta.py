# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CrewOperationsPopOverMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class CrewOperationsPopOverMeta(DAAPIModule):

    def invokeOperation(self, operationName):
        self._printOverrideError('invokeOperation')

    def as_updateS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_update(data)
