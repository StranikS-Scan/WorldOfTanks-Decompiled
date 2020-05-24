# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/MissionsPageMeta.py
from gui.Scaleform.framework.entities.View import View

class MissionsPageMeta(View):

    def resetFilters(self):
        self._printOverrideError('resetFilters')

    def onTabSelected(self, alias, prefix):
        self._printOverrideError('onTabSelected')

    def onClose(self):
        self._printOverrideError('onClose')

    def as_setTabsDataProviderS(self, dataProvider):
        return self.flashObject.as_setTabsDataProvider(dataProvider) if self._isDAAPIInited() else None

    def as_showFilterS(self, visible, topShadowVisible):
        return self.flashObject.as_showFilter(visible, topShadowVisible) if self._isDAAPIInited() else None

    def as_showFilterCounterS(self, countText, isFilterApplied):
        return self.flashObject.as_showFilterCounter(countText, isFilterApplied) if self._isDAAPIInited() else None

    def as_blinkFilterCounterS(self):
        return self.flashObject.as_blinkFilterCounter() if self._isDAAPIInited() else None

    def as_setTabsCounterDataS(self, data):
        return self.flashObject.as_setTabsCounterData(data) if self._isDAAPIInited() else None
