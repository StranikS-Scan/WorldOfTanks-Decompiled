# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StoreTableMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class StoreTableMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def refreshStoreTableDataProvider(self):
        """
        :return :
        """
        self._printOverrideError('refreshStoreTableDataProvider')

    def as_getTableDataProviderS(self):
        """
        :return Object:
        """
        return self.flashObject.as_getTableDataProvider() if self._isDAAPIInited() else None

    def as_setTableTypeS(self, type):
        """
        :param type:
        :return :
        """
        return self.flashObject.as_setTableType(type) if self._isDAAPIInited() else None

    def as_scrollToFirstS(self, level, disabled, currency):
        """
        :param level:
        :param disabled:
        :param currency:
        :return :
        """
        return self.flashObject.as_scrollToFirst(level, disabled, currency) if self._isDAAPIInited() else None

    def as_setGoldS(self, gold):
        """
        :param gold:
        :return :
        """
        return self.flashObject.as_setGold(gold) if self._isDAAPIInited() else None

    def as_setCreditsS(self, credits):
        """
        :param credits:
        :return :
        """
        return self.flashObject.as_setCredits(credits) if self._isDAAPIInited() else None
