# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StorageCategoryStorageViewMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class StorageCategoryStorageViewMeta(BaseDAAPIComponent):

    def setActiveState(self, isActive):
        self._printOverrideError('setActiveState')

    def onOpenTab(self, index):
        self._printOverrideError('onOpenTab')

    def as_setTabsDataS(self, tabs):
        return self.flashObject.as_setTabsData(tabs) if self._isDAAPIInited() else None

    def as_setTabCounterS(self, sectionIdx, value):
        return self.flashObject.as_setTabCounter(sectionIdx, value) if self._isDAAPIInited() else None
