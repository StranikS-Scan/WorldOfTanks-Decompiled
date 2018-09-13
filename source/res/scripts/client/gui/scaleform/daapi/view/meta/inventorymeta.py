# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/InventoryMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class InventoryMeta(DAAPIModule):

    def sellItem(self, data):
        self._printOverrideError('sellItem')
