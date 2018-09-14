# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/ContextMenuManagerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule

class ContextMenuManagerMeta(BaseDAAPIModule):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIModule
    """

    def requestOptions(self, type, ctx):
        self._printOverrideError('requestOptions')

    def onOptionSelect(self, optionId):
        self._printOverrideError('onOptionSelect')

    def onHide(self):
        self._printOverrideError('onHide')

    def as_setOptionsS(self, data):
        """
        :param data: Represented by ContextMenuOptionsVO (AS)
        """
        return self.flashObject.as_setOptions(data) if self._isDAAPIInited() else None

    def as_hideS(self):
        return self.flashObject.as_hide() if self._isDAAPIInited() else None
