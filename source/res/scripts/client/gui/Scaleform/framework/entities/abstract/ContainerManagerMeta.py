# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/ContainerManagerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class ContainerManagerMeta(BaseDAAPIComponent):

    def isModalViewsIsExists(self):
        self._printOverrideError('isModalViewsIsExists')

    def as_getViewS(self, name):
        return self.flashObject.as_getView(name) if self._isDAAPIInited() else None

    def as_showS(self, name, x=0, y=0):
        return self.flashObject.as_show(name, x, y) if self._isDAAPIInited() else None

    def as_registerContainerS(self, layer, name):
        return self.flashObject.as_registerContainer(layer, name) if self._isDAAPIInited() else None

    def as_unregisterContainerS(self, layer):
        return self.flashObject.as_unregisterContainer(layer) if self._isDAAPIInited() else None

    def as_closePopUpsS(self):
        return self.flashObject.as_closePopUps() if self._isDAAPIInited() else None

    def as_isOnTopS(self, layer, windowName):
        return self.flashObject.as_isOnTop(layer, windowName) if self._isDAAPIInited() else None

    def as_bringToFrontS(self, layer, windowName):
        return self.flashObject.as_bringToFront(layer, windowName) if self._isDAAPIInited() else None

    def as_showContainersS(self, layers, time=0):
        return self.flashObject.as_showContainers(layers, time) if self._isDAAPIInited() else None

    def as_hideContainersS(self, layers, time=0):
        return self.flashObject.as_hideContainers(layers, time) if self._isDAAPIInited() else None

    def as_isContainerShownS(self, layer):
        return self.flashObject.as_isContainerShown(layer) if self._isDAAPIInited() else None

    def as_getVisibleLayersS(self):
        return self.flashObject.as_getVisibleLayers() if self._isDAAPIInited() else None

    def as_setVisibleLayersS(self, layers):
        return self.flashObject.as_setVisibleLayers(layers) if self._isDAAPIInited() else None
