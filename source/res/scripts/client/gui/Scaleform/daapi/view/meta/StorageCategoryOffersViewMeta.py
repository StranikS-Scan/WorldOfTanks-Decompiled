# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StorageCategoryOffersViewMeta.py
from gui.Scaleform.daapi.view.lobby.storage.category_view import BaseCategoryView

class StorageCategoryOffersViewMeta(BaseCategoryView):

    def navigateToStore(self):
        self._printOverrideError('navigateToStore')

    def openOfferWindow(self, offerID):
        self._printOverrideError('openOfferWindow')

    def as_setTotalClicksTextS(self, text):
        return self.flashObject.as_setTotalClicksText(text) if self._isDAAPIInited() else None
