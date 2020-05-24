# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StorageCategoryInHangarViewMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class StorageCategoryInHangarViewMeta(BaseDAAPIComponent):

    def setActiveState(self, isActive):
        self._printOverrideError('setActiveState')

    def as_setTabsDataS(self, tabs):
        return self.flashObject.as_setTabsData(tabs) if self._isDAAPIInited() else None
