# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/LoaderManagerMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class LoaderManagerMeta(DAAPIModule):

    def viewLoaded(self, token, view):
        self._printOverrideError('viewLoaded')

    def viewLoadError(self, token, alias, text):
        self._printOverrideError('viewLoadError')

    def viewInitializationError(self, token, config, alias):
        self._printOverrideError('viewInitializationError')

    def as_loadViewS(self, config, token, alias, name):
        if self._isDAAPIInited():
            return self.flashObject.as_loadView(config, token, alias, name)
