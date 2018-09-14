# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ShopMeta.py
from gui.Scaleform.daapi.view.lobby.store.Store import Store

class ShopMeta(Store):

    def buyItem(self, data):
        self._printOverrideError('buyItem')
