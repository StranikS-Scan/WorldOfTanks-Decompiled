# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/TickerMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class TickerMeta(DAAPIModule):

    def showBrowser(self, entryID):
        self._printOverrideError('showBrowser')

    def as_setItemsS(self, items):
        if self._isDAAPIInited():
            return self.flashObject.as_setItems(items)
