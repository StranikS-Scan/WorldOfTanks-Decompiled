# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/ContainerManagerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule

class ContainerManagerMeta(BaseDAAPIModule):

    def isModalViewsIsExists(self):
        self._printOverrideError('isModalViewsIsExists')

    def canCancelPreviousLoading(self, containerType):
        self._printOverrideError('canCancelPreviousLoading')

    def as_getViewS(self, name):
        if self._isDAAPIInited():
            return self.flashObject.as_getView(name)

    def as_showS(self, name, x, y):
        if self._isDAAPIInited():
            return self.flashObject.as_show(name, x, y)

    def as_hideS(self, name):
        if self._isDAAPIInited():
            return self.flashObject.as_hide(name)

    def as_registerContainerS(self, type, name):
        if self._isDAAPIInited():
            return self.flashObject.as_registerContainer(type, name)

    def as_unregisterContainerS(self, type):
        if self._isDAAPIInited():
            return self.flashObject.as_unregisterContainer(type)

    def as_closePopUpsS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_closePopUps()

    def as_isOnTopS(self, cType, vName):
        if self._isDAAPIInited():
            return self.flashObject.as_isOnTop(cType, vName)

    def as_bringToFrontS(self, cType, vName):
        if self._isDAAPIInited():
            return self.flashObject.as_bringToFront(cType, vName)
