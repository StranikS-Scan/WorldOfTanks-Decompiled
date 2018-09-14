# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/TickerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class TickerMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def showBrowser(self, entryID):
        """
        :param entryID:
        :return :
        """
        self._printOverrideError('showBrowser')

    def as_setItemsS(self, items):
        """
        :param items:
        :return :
        """
        return self.flashObject.as_setItems(items) if self._isDAAPIInited() else None
