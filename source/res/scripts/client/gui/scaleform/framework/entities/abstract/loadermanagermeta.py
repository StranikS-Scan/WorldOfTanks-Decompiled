# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/LoaderManagerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule

class LoaderManagerMeta(BaseDAAPIModule):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIModule
    """

    def viewLoaded(self, alias, name, view):
        """
        :param view: Represented by IView (AS)
        """
        self._printOverrideError('viewLoaded')

    def viewLoadError(self, alias, name, text):
        self._printOverrideError('viewLoadError')

    def viewInitializationError(self, alias, name):
        self._printOverrideError('viewInitializationError')

    def as_loadViewS(self, data):
        """
        :param data: Represented by LoadViewVO (AS)
        """
        return self.flashObject.as_loadView(data) if self._isDAAPIInited() else None
