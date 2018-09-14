# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BaseRallyListViewMeta.py
from gui.Scaleform.daapi.view.lobby.rally.BaseRallyView import BaseRallyView

class BaseRallyListViewMeta(BaseRallyView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseRallyView
    """

    def getRallyDetails(self, index):
        self._printOverrideError('getRallyDetails')

    def as_selectByIndexS(self, index):
        return self.flashObject.as_selectByIndex(index) if self._isDAAPIInited() else None

    def as_selectByIDS(self, rallyID):
        return self.flashObject.as_selectByID(rallyID) if self._isDAAPIInited() else None

    def as_getSearchDPS(self):
        return self.flashObject.as_getSearchDP() if self._isDAAPIInited() else None

    def as_setDetailsS(self, value):
        return self.flashObject.as_setDetails(value) if self._isDAAPIInited() else None

    def as_setVehiclesTitleS(self, value):
        return self.flashObject.as_setVehiclesTitle(value) if self._isDAAPIInited() else None
