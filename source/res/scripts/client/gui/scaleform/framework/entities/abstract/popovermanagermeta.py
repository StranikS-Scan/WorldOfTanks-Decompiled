# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/PopoverManagerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule

class PopoverManagerMeta(BaseDAAPIModule):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIModule
    null
    """

    def requestShowPopover(self, alias, data):
        """
        :param alias:
        :param data:
        :return :
        """
        self._printOverrideError('requestShowPopover')

    def requestHidePopover(self):
        """
        :return :
        """
        self._printOverrideError('requestHidePopover')

    def as_onPopoverDestroyS(self):
        """
        :return :
        """
        return self.flashObject.as_onPopoverDestroy() if self._isDAAPIInited() else None
