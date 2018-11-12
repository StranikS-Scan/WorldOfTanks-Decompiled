# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StorageCategoryPersonalReservesViewMeta.py
from gui.Scaleform.daapi.view.lobby.storage.category_view import BaseCategoryView

class StorageCategoryPersonalReservesViewMeta(BaseCategoryView):

    def navigateToStore(self):
        self._printOverrideError('navigateToStore')

    def activateReserve(self, boosterId):
        self._printOverrideError('activateReserve')

    def resetFilter(self):
        self._printOverrideError('resetFilter')

    def onFiltersChange(self, filters):
        self._printOverrideError('onFiltersChange')

    def as_initS(self, data):
        return self.flashObject.as_init(data) if self._isDAAPIInited() else None

    def as_initFilterS(self, typeFiltersVO, durationFiltersVO):
        return self.flashObject.as_initFilter(typeFiltersVO, durationFiltersVO) if self._isDAAPIInited() else None

    def as_resetFilterS(self, resetData):
        return self.flashObject.as_resetFilter(resetData) if self._isDAAPIInited() else None

    def as_updateCounterS(self, shouldShow, displayString, isZeroCount):
        return self.flashObject.as_updateCounter(shouldShow, displayString, isZeroCount) if self._isDAAPIInited() else None
