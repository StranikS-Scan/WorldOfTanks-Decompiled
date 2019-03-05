# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StorageCarouselEnvironmentMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class StorageCarouselEnvironmentMeta(BaseDAAPIComponent):

    def resetFilter(self):
        self._printOverrideError('resetFilter')

    def showItemInfo(self, itemId):
        self._printOverrideError('showItemInfo')

    def changeSearchNameVehicle(self, inputText):
        self._printOverrideError('changeSearchNameVehicle')

    def as_updateSearchS(self, searchInputLabel, searchInputName, searchInputTooltip, searchInputMaxChars):
        return self.flashObject.as_updateSearch(searchInputLabel, searchInputName, searchInputTooltip, searchInputMaxChars) if self._isDAAPIInited() else None

    def as_updateCounterS(self, shouldShow, displayString, isZeroCount):
        return self.flashObject.as_updateCounter(shouldShow, displayString, isZeroCount) if self._isDAAPIInited() else None
