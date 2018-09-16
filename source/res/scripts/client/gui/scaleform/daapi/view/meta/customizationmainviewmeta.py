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

    def onSelectAnchor(self, areaID, regionID):
        self._printOverrideError('onSelectAnchor')

    def onPickItem(self):
        self._printOverrideError('onPickItem')

    def onReleaseItem(self):
        self._printOverrideError('onReleaseItem')

    def onSelectHotFilter(self, index, value):
        self._printOverrideError('onSelectHotFilter')

    def onAnchorsShown(self, anchors):
        self._printOverrideError('onAnchorsShown')

    def as_showBuyingPanelS(self):
        return self.flashObject.as_showBuyingPanel() if self._isDAAPIInited() else None

    def as_hideBuyingPanelS(self):
        return self.flashObject.as_hideBuyingPanel() if self._isDAAPIInited() else None

    def as_setHeaderDataS(self, data):
        return self.flashObject.as_setHeaderData(data) if self._isDAAPIInited() else None

    def as_setSeasonPanelDataS(self, data):
        return self.flashObject.as_setSeasonPanelData(data) if self._isDAAPIInited() else None

    def as_setAnchorInitS(self, data):
        return self.flashObject.as_setAnchorInit(data) if self._isDAAPIInited() else None

    def as_updateAnchorDataS(self, data):
        return self.flashObject.as_updateAnchorData(data) if self._isDAAPIInited() else None

    def as_setCarouselDataS(self, data):
        return self.flashObject.as_setCarouselData(data) if self._isDAAPIInited() else None

    def as_setCarouselFiltersInitDataS(self, data):
        return self.flashObject.as_setCarouselFiltersInitData(data) if self._isDAAPIInited() else None

    def as_setCarouselFiltersDataS(self, data):
        return self.flashObject.as_setCarouselFiltersData(data) if self._isDAAPIInited() else None

    def as_setFilterDataS(self, data):
        return self.flashObject.as_setFilterData(data) if self._isDAAPIInited() else None

    def as_setBottomPanelHeaderS(self, data):
        return self.flashObject.as_setBottomPanelHeader(data) if self._isDAAPIInited() else None

    def as_setBottomPanelInitDataS(self, data):
        return self.flashObject.as_setBottomPanelInitData(data) if self._isDAAPIInited() else None

    def as_setBottomPanelTabsDataS(self, data):
        return self.flashObject.as_setBottomPanelTabsData(data) if self._isDAAPIInited() else None

    def as_getDataProviderS(self):
        return self.flashObject.as_getDataProvider() if self._isDAAPIInited() else None

    def as_onRegionHighlightedS(self, slotId):
        return self.flashObject.as_onRegionHighlighted(slotId) if self._isDAAPIInited() else None

    def as_refreshAnchorPropertySheetS(self):
        return self.flashObject.as_refreshAnchorPropertySheet() if self._isDAAPIInited() else None

    def as_hideAnchorPropertySheetS(self):
        return self.flashObject.as_hideAnchorPropertySheet() if self._isDAAPIInited() else None

    def as_updateSelectedRegionsS(self, slotId):
        return self.flashObject.as_updateSelectedRegions(slotId) if self._isDAAPIInited() else None

    def as_cameraAutoRotateChangedS(self, autoRotate):
        return self.flashObject.as_cameraAutoRotateChanged(autoRotate) if self._isDAAPIInited() else None

    def as_setParallaxFlagS(self, isParallaxOn):
        return self.flashObject.as_setParallaxFlag(isParallaxOn) if self._isDAAPIInited() else None

    def as_setAnchorPositionsS(self, data):
        return self.flashObject.as_setAnchorPositions(data) if self._isDAAPIInited() else None
