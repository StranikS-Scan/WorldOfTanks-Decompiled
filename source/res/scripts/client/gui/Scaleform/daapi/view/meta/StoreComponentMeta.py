# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StoreComponentMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class StoreComponentMeta(BaseDAAPIComponent):

    def requestTableData(self, nation, actionsSelected, type, filters):
        self._printOverrideError('requestTableData')

    def requestFilterData(self, filterType):
        self._printOverrideError('requestFilterData')

    def onShowInfo(self, itemCD):
        self._printOverrideError('onShowInfo')

    def getName(self):
        self._printOverrideError('getName')

    def onAddVehToCompare(self, itemCD):
        self._printOverrideError('onAddVehToCompare')

    def as_initFiltersDataS(self, nations, actionsFilterName):
        """
        :param nations: Represented by Array (AS)
        """
        return self.flashObject.as_initFiltersData(nations, actionsFilterName) if self._isDAAPIInited() else None

    def as_completeInitS(self):
        return self.flashObject.as_completeInit() if self._isDAAPIInited() else None

    def as_updateS(self):
        return self.flashObject.as_update() if self._isDAAPIInited() else None

    def as_setFilterTypeS(self, data):
        """
        :param data: Represented by ShopNationFilterDataVo (AS)
        """
        return self.flashObject.as_setFilterType(data) if self._isDAAPIInited() else None

    def as_setSubFilterS(self, data):
        """
        :param data: Represented by ShopSubFilterData (AS)
        """
        return self.flashObject.as_setSubFilter(data) if self._isDAAPIInited() else None

    def as_setFilterOptionsS(self, data):
        """
        :param data: Represented by FiltersDataVO (AS)
        """
        return self.flashObject.as_setFilterOptions(data) if self._isDAAPIInited() else None

    def as_scrollPositionS(self, index):
        return self.flashObject.as_scrollPosition(index) if self._isDAAPIInited() else None

    def as_setVehicleCompareAvailableS(self, value):
        return self.flashObject.as_setVehicleCompareAvailable(value) if self._isDAAPIInited() else None

    def as_setActionAvailableS(self, value):
        return self.flashObject.as_setActionAvailable(value) if self._isDAAPIInited() else None
