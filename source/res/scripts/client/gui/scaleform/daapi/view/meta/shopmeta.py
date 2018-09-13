# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ShopMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ShopMeta(DAAPIModule):

    def buyItem(self, data):
        self._printOverrideError('buyItem')
