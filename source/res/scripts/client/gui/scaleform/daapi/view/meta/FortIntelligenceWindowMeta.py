# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortIntelligenceWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class FortIntelligenceWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    """

    def requestClanFortInfo(self, index):
        self._printOverrideError('requestClanFortInfo')

    def as_setStatusTextS(self, statusText):
        return self.flashObject.as_setStatusText(statusText) if self._isDAAPIInited() else None

    def as_getSearchDPS(self):
        return self.flashObject.as_getSearchDP() if self._isDAAPIInited() else None

    def as_getCurrentListIndexS(self):
        return self.flashObject.as_getCurrentListIndex() if self._isDAAPIInited() else None

    def as_selectByIndexS(self, index):
        return self.flashObject.as_selectByIndex(index) if self._isDAAPIInited() else None

    def as_setTableHeaderS(self, data):
        """
        :param data: Represented by NormalSortingTableHeaderVO (AS)
        """
        return self.flashObject.as_setTableHeader(data) if self._isDAAPIInited() else None
