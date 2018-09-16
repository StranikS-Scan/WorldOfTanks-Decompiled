# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StorageCategoryPersonalReservesViewMeta.py
from gui.Scaleform.daapi.view.lobby.storage.category_view import BaseCategoryView

class StorageCategoryPersonalReservesViewMeta(BaseCategoryView):

    def navigateToStore(self):
        self._printOverrideError('navigateToStore')

    def activateReserve(self, boosterId):
        self._printOverrideError('activateReserve')

    def as_initS(self, data):
        return self.flashObject.as_init(data) if self._isDAAPIInited() else None
