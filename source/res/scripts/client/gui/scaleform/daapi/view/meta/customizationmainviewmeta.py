# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CustomizationMainViewMeta.py
from gui.Scaleform.framework.entities.View import View

class CustomizationMainViewMeta(View):

    def showBuyWindow(self):
        self._printOverrideError('showBuyWindow')

    def closeWindow(self):
        self._printOverrideError('closeWindow')

    def fadeOutAnchors(self, value):
        self._printOverrideError('fadeOutAnchors')

    def changeSeason(self, season):
        self._printOverrideError('changeSeason')

    def itemContextMenuDisplayed(self):
        self._printOverrideError('itemContextMenuDisplayed')

    def onLobbyClick(self):
        self._printOverrideError('onLobbyClick')

    def onSelectAnchor(self, areaID, slotID, regionID):
        self._printOverrideError('onSelectAnchor')

    def onReleaseItem(self):
        self._printOverrideError('onReleaseItem')

    def onClearItem(self):
        self._printOverrideError('onClearItem')

    def onAnchorsShown(self, anchors):
        self._printOverrideError('onAnchorsShown')

    def onPressClearBtn(self):
        self._printOverrideError('onPressClearBtn')

    def as_hideS(self, value):
        return self.flashObject.as_hide(value) if self._isDAAPIInited() else None

    def as_setHeaderDataS(self, data):
        return self.flashObject.as_setHeaderData(data) if self._isDAAPIInited() else None

    def as_setAnchorInitS(self, data):
        return self.flashObject.as_setAnchorInit(data) if self._isDAAPIInited() else None

    def as_updateAnchorDataS(self, data):
        return self.flashObject.as_updateAnchorData(data) if self._isDAAPIInited() else None

    def as_onRegionHighlightedS(self, slotId):
        return self.flashObject.as_onRegionHighlighted(slotId) if self._isDAAPIInited() else None

    def as_updateSelectedRegionsS(self, slotId):
        return self.flashObject.as_updateSelectedRegions(slotId) if self._isDAAPIInited() else None

    def as_cameraAutoRotateChangedS(self, autoRotate):
        return self.flashObject.as_cameraAutoRotateChanged(autoRotate) if self._isDAAPIInited() else None

    def as_setAnchorsDataS(self, data):
        return self.flashObject.as_setAnchorsData(data) if self._isDAAPIInited() else None

    def as_setSeasonsBarDataS(self, dataProvider):
        return self.flashObject.as_setSeasonsBarData(dataProvider) if self._isDAAPIInited() else None

    def as_enableDNDS(self, value):
        return self.flashObject.as_enableDND(value) if self._isDAAPIInited() else None
