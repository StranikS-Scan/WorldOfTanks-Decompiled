# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/ContextMenuManagerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule

class ContextMenuManagerMeta(BaseDAAPIModule):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIModule
    null
    """

    def requestOptions(self, type, ctx):
        """
        :param type:
        :param ctx:
        :return :
        """
        self._printOverrideError('requestOptions')

    def onOptionSelect(self, optionId):
        """
        :param optionId:
        :return :
        """
        self._printOverrideError('onOptionSelect')

    def onHide(self):
        """
        :return :
        """
        self._printOverrideError('onHide')

    def as_setOptionsS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setOptions(data) if self._isDAAPIInited() else None

    def as_hideS(self):
        """
        :return :
        """
        return self.flashObject.as_hide() if self._isDAAPIInited() else None
