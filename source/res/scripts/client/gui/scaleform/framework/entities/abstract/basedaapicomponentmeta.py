# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/BaseDAAPIComponentMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule

class BaseDAAPIComponentMeta(BaseDAAPIModule):

    def registerFlashComponent(self, component, alias):
        self._printOverrideError('registerFlashComponent')

    def isFlashComponentRegistered(self, alias):
        self._printOverrideError('isFlashComponentRegistered')

    def unregisterFlashComponent(self, alias):
        self._printOverrideError('unregisterFlashComponent')

    def as_populateS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_populate()

    def as_disposeS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_dispose()
