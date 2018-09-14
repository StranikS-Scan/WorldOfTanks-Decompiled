# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/ContainerManagerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule

class ContainerManagerMeta(BaseDAAPIModule):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIModule
    null
    """

    def isModalViewsIsExists(self):
        """
        :return Boolean:
        """
        self._printOverrideError('isModalViewsIsExists')

    def canCancelPreviousLoading(self, containerType):
        """
        :param containerType:
        :return Boolean:
        """
        self._printOverrideError('canCancelPreviousLoading')

    def as_getViewS(self, name):
        """
        :param name:
        :return Boolean:
        """
        return self.flashObject.as_getView(name) if self._isDAAPIInited() else None

    def as_showS(self, name, x, y):
        """
        :param name:
        :param x:
        :param y:
        :return Boolean:
        """
        return self.flashObject.as_show(name, x, y) if self._isDAAPIInited() else None

    def as_hideS(self, name):
        """
        :param name:
        :return Boolean:
        """
        return self.flashObject.as_hide(name) if self._isDAAPIInited() else None

    def as_registerContainerS(self, type, name):
        """
        :param type:
        :param name:
        :return :
        """
        return self.flashObject.as_registerContainer(type, name) if self._isDAAPIInited() else None

    def as_unregisterContainerS(self, type):
        """
        :param type:
        :return :
        """
        return self.flashObject.as_unregisterContainer(type) if self._isDAAPIInited() else None

    def as_closePopUpsS(self):
        """
        :return :
        """
        return self.flashObject.as_closePopUps() if self._isDAAPIInited() else None

    def as_isOnTopS(self, cType, vName):
        """
        :param cType:
        :param vName:
        :return Boolean:
        """
        return self.flashObject.as_isOnTop(cType, vName) if self._isDAAPIInited() else None

    def as_bringToFrontS(self, cType, vName):
        """
        :param cType:
        :param vName:
        :return :
        """
        return self.flashObject.as_bringToFront(cType, vName) if self._isDAAPIInited() else None

    def as_showContainersS(self, viewTypes):
        """
        :param viewTypes:
        :return :
        """
        return self.flashObject.as_showContainers(viewTypes) if self._isDAAPIInited() else None

    def as_hideContainersS(self, viewTypes):
        """
        :param viewTypes:
        :return :
        """
        return self.flashObject.as_hideContainers(viewTypes) if self._isDAAPIInited() else None

    def as_isContainerShownS(self, viewType):
        """
        :param viewType:
        :return Boolean:
        """
        return self.flashObject.as_isContainerShown(viewType) if self._isDAAPIInited() else None
