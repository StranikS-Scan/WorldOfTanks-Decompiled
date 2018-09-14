# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/BaseDAAPIComponentMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule

class BaseDAAPIComponentMeta(BaseDAAPIModule):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIModule
    null
    """

    def registerFlashComponent(self, component, alias):
        """
        :param component:
        :param alias:
        :return :
        """
        self._printOverrideError('registerFlashComponent')

    def isFlashComponentRegistered(self, alias):
        """
        :param alias:
        :return Boolean:
        """
        self._printOverrideError('isFlashComponentRegistered')

    def unregisterFlashComponent(self, alias):
        """
        :param alias:
        :return :
        """
        self._printOverrideError('unregisterFlashComponent')

    def as_populateS(self):
        """
        :return :
        """
        return self.flashObject.as_populate() if self._isDAAPIInited() else None

    def as_disposeS(self):
        """
        :return :
        """
        return self.flashObject.as_dispose() if self._isDAAPIInited() else None
