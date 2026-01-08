# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CustomizationFiltersPopoverMeta.py
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView

class CustomizationFiltersPopoverMeta(SmartPopOverView):

    def changeGroup(self, itemId):
        self._printOverrideError('changeGroup')

    def changeDisplayMethod(self, itemId):
        self._printOverrideError('changeDisplayMethod')

    def setDefaultFilter(self):
        self._printOverrideError('setDefaultFilter')

    def setShowOnlyHistoric(self, value):
        self._printOverrideError('setShowOnlyHistoric')

    def setShowOnlyAcquired(self, value):
        self._printOverrideError('setShowOnlyAcquired')

    def setHideOnAnotherVeh(self, value):
        self._printOverrideError('setHideOnAnotherVeh')

    def setShowOnlyProgressionDecals(self, value):
        self._printOverrideError('setShowOnlyProgressionDecals')

    def setShowOnlyEditableStyles(self, value):
        self._printOverrideError('setShowOnlyEditableStyles')

    def setShowOnlyProgressionStyles(self, value):
        self._printOverrideError('setShowOnlyProgressionStyles')

    def onFilterChange(self, groupId, index, value):
        self._printOverrideError('onFilterChange')

    def onFormChange(self, index, value):
        self._printOverrideError('onFormChange')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_enableDefBtnS(self, value):
        return self.flashObject.as_enableDefBtn(value) if self._isDAAPIInited() else None

    def as_updateCounterS(self, current, total, newHiddenElementsCount):
        return self.flashObject.as_updateCounter(current, total, newHiddenElementsCount) if self._isDAAPIInited() else None
