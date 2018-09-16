# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StoreViewMeta.py
from gui.Scaleform.framework.entities.View import View

class StoreViewMeta(View):

    def onClose(self):
        self._printOverrideError('onClose')

    def onTabChange(self, tabId):
        self._printOverrideError('onTabChange')

    def onBackButtonClick(self):
        self._printOverrideError('onBackButtonClick')

    def as_showStorePageS(self, tabId):
        return self.flashObject.as_showStorePage(tabId) if self._isDAAPIInited() else None

    def as_initS(self, data):
        return self.flashObject.as_init(data) if self._isDAAPIInited() else None

    def as_showBackButtonS(self, label, description):
        return self.flashObject.as_showBackButton(label, description) if self._isDAAPIInited() else None

    def as_hideBackButtonS(self):
        return self.flashObject.as_hideBackButton() if self._isDAAPIInited() else None

    def as_setBtnTabCountersS(self, counters):
        return self.flashObject.as_setBtnTabCounters(counters) if self._isDAAPIInited() else None

    def as_removeBtnTabCountersS(self, counters):
        return self.flashObject.as_removeBtnTabCounters(counters) if self._isDAAPIInited() else None
