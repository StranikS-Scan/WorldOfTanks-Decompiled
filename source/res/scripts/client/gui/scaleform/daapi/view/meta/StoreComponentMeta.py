# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StoreComponentMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class StoreComponentMeta(BaseDAAPIComponent):

    def requestTableData(self, nation, type, filter):
        self._printOverrideError('requestTableData')

    def requestFilterData(self, filterType):
        self._printOverrideError('requestFilterData')

    def onCloseButtonClick(self):
        self._printOverrideError('onCloseButtonClick')

    def onShowInfo(self, data):
        self._printOverrideError('onShowInfo')

    def getName(self):
        self._printOverrideError('getName')

    def as_setNationsS(self, nations):
        return self.flashObject.as_setNations(nations) if self._isDAAPIInited() else None

    def as_completeInitS(self):
        return self.flashObject.as_completeInit() if self._isDAAPIInited() else None

    def as_updateS(self):
        return self.flashObject.as_update() if self._isDAAPIInited() else None

    def as_setFilterTypeS(self, data):
        return self.flashObject.as_setFilterType(data) if self._isDAAPIInited() else None

    def as_setSubFilterS(self, data):
        return self.flashObject.as_setSubFilter(data) if self._isDAAPIInited() else None

    def as_setFilterOptionsS(self, attrs):
        return self.flashObject.as_setFilterOptions(attrs) if self._isDAAPIInited() else None
