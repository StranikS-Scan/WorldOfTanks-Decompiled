# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CustomizationMainViewMeta.py
from gui.Scaleform.framework.entities.View import View

class CustomizationMainViewMeta(View):

    def showBuyWindow(self):
        self._printOverrideError('showBuyWindow')

    def onCloseWindow(self):
        self._printOverrideError('onCloseWindow')

    def fadeOutAnchors(self, value):
        self._printOverrideError('fadeOutAnchors')

    def changeSeason(self, season, keepSelect):
        self._printOverrideError('changeSeason')

    def itemContextMenuDisplayed(self):
        self._printOverrideError('itemContextMenuDisplayed')

    def onLobbyClick(self):
        self._printOverrideError('onLobbyClick')

    def onSelectAnchor(self, areaID, slotID, regionID):
        self._printOverrideError('onSelectAnchor')

    def onLockedAnchor(self):
        self._printOverrideError('onLockedAnchor')

    def onReleaseItem(self):
        self._printOverrideError('onReleaseItem')

    def onAnchorsShown(self, anchors):
        self._printOverrideError('onAnchorsShown')

    def propertiesSheetSet(self, sheet, width, height, crnterX, centerY):
        self._printOverrideError('propertiesSheetSet')

    def onPressClearBtn(self):
        self._printOverrideError('onPressClearBtn')

    def onPressEscBtn(self):
        self._printOverrideError('onPressEscBtn')

    def onPressSelectNextItem(self, reverse):
        self._printOverrideError('onPressSelectNextItem')

    def playCustomSound(self, sound):
        self._printOverrideError('playCustomSound')

    def onRemoveSelectedItem(self):
        self._printOverrideError('onRemoveSelectedItem')

    def resetC11nItemsNovelty(self, itemsList):
        self._printOverrideError('resetC11nItemsNovelty')

    def as_hideS(self, value):
        return self.flashObject.as_hide(value) if self._isDAAPIInited() else None

    def as_setHeaderDataS(self, data):
        return self.flashObject.as_setHeaderData(data) if self._isDAAPIInited() else None

    def as_setAnchorInitS(self, data):
        return self.flashObject.as_setAnchorInit(data) if self._isDAAPIInited() else None

    def as_updateAnchorDataS(self, data):
        return self.flashObject.as_updateAnchorData(data) if self._isDAAPIInited() else None

    def as_onRegionHighlightedS(self, slotId, highlightingType, highlightingResult):
        return self.flashObject.as_onRegionHighlighted(slotId, highlightingType, highlightingResult) if self._isDAAPIInited() else None

    def as_updateSelectedRegionsS(self, slotId):
        return self.flashObject.as_updateSelectedRegions(slotId) if self._isDAAPIInited() else None

    def as_setAnchorsDataS(self, data):
        return self.flashObject.as_setAnchorsData(data) if self._isDAAPIInited() else None

    def as_setSeasonsBarDataS(self, dataProvider):
        return self.flashObject.as_setSeasonsBarData(dataProvider) if self._isDAAPIInited() else None

    def as_enableDNDS(self, value):
        return self.flashObject.as_enableDND(value) if self._isDAAPIInited() else None

    def as_selectSeasonS(self, value):
        return self.flashObject.as_selectSeason(value) if self._isDAAPIInited() else None

    def as_releaseItemS(self, deselectAnchor=True):
        return self.flashObject.as_releaseItem(deselectAnchor) if self._isDAAPIInited() else None

    def as_showCarouselsArrowsNotificationS(self, text):
        return self.flashObject.as_showCarouselsArrowsNotification(text) if self._isDAAPIInited() else None

    def as_reselectS(self, intCd):
        return self.flashObject.as_reselect(intCd) if self._isDAAPIInited() else None

    def as_setNotificationCountersS(self, counters):
        return self.flashObject.as_setNotificationCounters(counters) if self._isDAAPIInited() else None

    def as_setAnchorsLockStateS(self, data):
        return self.flashObject.as_setAnchorsLockState(data) if self._isDAAPIInited() else None
