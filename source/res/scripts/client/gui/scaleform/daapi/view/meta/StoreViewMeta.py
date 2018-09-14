# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StoreViewMeta.py
from gui.Scaleform.framework.entities.View import View

class StoreViewMeta(View):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends View
    """

    def onClose(self):
        self._printOverrideError('onClose')

    def onTabChange(self, tabId):
        self._printOverrideError('onTabChange')

    def as_showStorePageS(self, viewAlias):
        return self.flashObject.as_showStorePage(viewAlias) if self._isDAAPIInited() else None

    def as_initS(self, data):
        """
        :param data: Represented by StoreViewInitVO (AS)
        """
        return self.flashObject.as_init(data) if self._isDAAPIInited() else None
