# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CustomizationMainViewMeta.py
from gui.Scaleform.framework.entities.View import View

class CustomizationMainViewMeta(View):

    def showBuyWindow(self):
        self._printOverrideError('showBuyWindow')

    def closeWindow(self):
        self._printOverrideError('closeWindow')

    def installCustomizationElement(self, itemIntCD, areaId, slotId, regionId, season):
        self._printOverrideError('installCustomizationElement')

    def switchToCustom(self):
        self._printOverrideError('switchToCustom')

    def switchToStyle(self):
        self._printOverrideError('switchToStyle')

    def showGroupFromTab(self, groupId):
        self._printOverrideError('showGroupFromTab')

    def fadeOutAnchors(self, value):
        self._printOverrideError('fadeOutAnchors')

    def getPropertySheetData(self, itemID):
        self._printOverrideError('getPropertySheetData')

    def clearFilter(self):
        self._printOverrideError('clearFilter')

    def refreshFilterData(self):
        self._printOverrideError('refreshFilterData')

    def clearCustomizationItem(self, areaId, slotId, regionId, season):
        self._printOverrideError('clearCustomizationItem')

    def changeSeason(self, season):
        self._printOverrideError('changeSeason')

    def itemContextMenuDisplayed(self):
        self._printOverrideError('itemContextMenuDisplayed')

    def onPropertySheetLoaded(self):
        self._printOverrideError('onPropertySheetLoaded')

    def getHistoricalPopoverData(self):
        self._printOverrideError('getHistoricalPopoverData')

    def updatePropertySheetButtons(self, areOaId, slotId, regionId):
        self._printOverrideError('updatePropertySheetButtons')

    def onLobbyClick(self):
        self._printOverrideError('onLobbyClick')

    def setEnableMultiselectRegions(self, value):
        self._printOverrideError('setEnableMultiselectRegions')

    def onSelectItem(self, index):
        self._printOverrideError('onSelectItem')

    def resetFilter(self):
        self._printOverrideError('resetFilter')

    def onChangeSize(self):
        self._printOverrideError('onChangeSize')

    def as_showBuyingPanelS(self):
        return self.flashObject.as_showBuyingPanel() if self._isDAAPIInited() else None

    def as_hideBuyingPanelS(self):
        return self.flashObject.as_hideBuyingPanel() if self._isDAAPIInited() else None

    def as_setHeaderDataS(self, data):
        """
        :param data: Represented by CustomizationHeaderVO (AS)
        """
        return self.flashObject.as_setHeaderData(data) if self._isDAAPIInited() else None

    def as_setSeasonPanelDataS(self, data):
        """
        :param data: Represented by CustomizationSeasonPanelVO (AS)
        """
        return self.flashObject.as_setSeasonPanelData(data) if self._isDAAPIInited() else None

    def as_setAnchorPositionsS(self, data):
        """
        :param data: Represented by CustomizationAnchorsSetVO (AS)
        """
        return self.flashObject.as_setAnchorPositions(data) if self._isDAAPIInited() else None

    def as_setAnchorInitS(self, data):
        """
        :param data: Represented by CustomizationAnchorInitVO (AS)
        """
        return self.flashObject.as_setAnchorInit(data) if self._isDAAPIInited() else None

    def as_updateAnchorDataS(self, data):
        """
        :param data: Represented by CustomizationAnchorInitVO (AS)
        """
        return self.flashObject.as_updateAnchorData(data) if self._isDAAPIInited() else None

    def as_setCarouselDataS(self, data):
        """
        :param data: Represented by CustomizationCarouselDataVO (AS)
        """
        return self.flashObject.as_setCarouselData(data) if self._isDAAPIInited() else None

    def as_setFilterDataS(self, data):
        """
        :param data: Represented by CustomizationCarouselFilterVO (AS)
        """
        return self.flashObject.as_setFilterData(data) if self._isDAAPIInited() else None

    def as_setBottomPanelHeaderS(self, data):
        """
        :param data: Represented by BottomPanelVO (AS)
        """
        return self.flashObject.as_setBottomPanelHeader(data) if self._isDAAPIInited() else None

    def as_setBottomPanelInitDataS(self, data):
        """
        :param data: Represented by CustomizationBottomPanelInitVO (AS)
        """
        return self.flashObject.as_setBottomPanelInitData(data) if self._isDAAPIInited() else None

    def as_setBottomPanelTabsDataS(self, data):
        """
        :param data: Represented by CustomizationTabNavigatorVO (AS)
        """
        return self.flashObject.as_setBottomPanelTabsData(data) if self._isDAAPIInited() else None

    def as_getDataProviderS(self):
        return self.flashObject.as_getDataProvider() if self._isDAAPIInited() else None

    def as_onRegionHighlightedS(self, slotId):
        """
        :param slotId: Represented by CustomizationSlotIdVO (AS)
        """
        return self.flashObject.as_onRegionHighlighted(slotId) if self._isDAAPIInited() else None

    def as_refreshAnchorPropertySheetS(self):
        return self.flashObject.as_refreshAnchorPropertySheet() if self._isDAAPIInited() else None

    def as_hideAnchorPropertySheetS(self):
        return self.flashObject.as_hideAnchorPropertySheet() if self._isDAAPIInited() else None

    def as_updateHistoricStatusS(self, data):
        """
        :param data: Represented by HistoricIndicatorVO (AS)
        """
        return self.flashObject.as_updateHistoricStatus(data) if self._isDAAPIInited() else None

    def as_updateSelectedRegionsS(self, slotId):
        """
        :param slotId: Represented by CustomizationSlotIdVO (AS)
        """
        return self.flashObject.as_updateSelectedRegions(slotId) if self._isDAAPIInited() else None
