# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StoreTableMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class StoreTableMeta(BaseDAAPIComponent):

    def refreshStoreTableDataProvider(self):
        self._printOverrideError('refreshStoreTableDataProvider')

    def as_getTableDataProviderS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_getTableDataProvider()

    def as_setTableTypeS(self, type):
        if self._isDAAPIInited():
            return self.flashObject.as_setTableType(type)

    def as_scrollToFirstS(self, level, disabled, currency):
        if self._isDAAPIInited():
            return self.flashObject.as_scrollToFirst(level, disabled, currency)

    def as_setGoldS(self, gold):
        if self._isDAAPIInited():
            return self.flashObject.as_setGold(gold)

    def as_setCreditsS(self, credits):
        if self._isDAAPIInited():
            return self.flashObject.as_setCredits(credits)
