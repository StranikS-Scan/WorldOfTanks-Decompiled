# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/LoaderManagerMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class LoaderManagerMeta(DAAPIModule):

    def viewLoaded(self, name, view):
        self._printOverrideError('viewLoaded')

    def viewLoadError(self, alias, name, text):
        self._printOverrideError('viewLoadError')

    def viewInitializationError(self, config, alias, name):
        self._printOverrideError('viewInitializationError')

    def as_loadViewS(self, config, alias, name):
        if self._isDAAPIInited():
            return self.flashObject.as_loadView(config, alias, name)
