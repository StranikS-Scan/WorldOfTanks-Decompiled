# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StoreTableMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class StoreTableMeta(BaseDAAPIComponent):

    def refreshStoreTableDataProvider(self):
        self._printOverrideError('refreshStoreTableDataProvider')

    def as_getTableDataProviderS(self):
        return self.flashObject.as_getTableDataProvider() if self._isDAAPIInited() else None

    def as_setDataS(self, data):
        """
        :param data: Represented by StoreTableVO (AS)
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
