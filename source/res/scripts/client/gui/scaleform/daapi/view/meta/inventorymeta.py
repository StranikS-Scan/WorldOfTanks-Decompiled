# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/InventoryMeta.py
from gui.Scaleform.daapi.view.lobby.store.Store import Store

class InventoryMeta(Store):

    def sellItem(self, data):
        self._printOverrideError('sellItem')
