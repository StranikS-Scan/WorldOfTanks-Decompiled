# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StoreMeta.py
from gui.Scaleform.framework.entities.View import View

class StoreMeta(View):

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
        if self._isDAAPIInited():
            return self.flashObject.as_setNations(nations)

    def as_completeInitS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_completeInit()

    def as_updateS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_update()

    def as_setFilterTypeS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setFilterType(data)

    def as_setSubFilterS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setSubFilter(data)

    def as_setFilterOptionsS(self, attrs):
        if self._isDAAPIInited():
            return self.flashObject.as_setFilterOptions(attrs)
