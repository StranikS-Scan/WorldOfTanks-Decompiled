# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CustomizationBottomPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class CustomizationBottomPanelMeta(BaseDAAPIComponent):

    def resetFilter(self):
        self._printOverrideError('resetFilter')

    def showBuyWindow(self):
        self._printOverrideError('showBuyWindow')

    def switchToStyle(self):
        self._printOverrideError('switchToStyle')

    def switchToCustom(self):
        self._printOverrideError('switchToCustom')

    def refreshFilterData(self):
        self._printOverrideError('refreshFilterData')

    def onSelectItem(self, index, intCD):
        self._printOverrideError('onSelectItem')

    def showGroupFromTab(self, groupId):
        self._printOverrideError('showGroupFromTab')

    def onSelectHotFilter(self, index, value):
        self._printOverrideError('onSelectHotFilter')

    def as_showBillS(self):
        return self.flashObject.as_showBill() if self._isDAAPIInited() else None

    def as_hideBillS(self):
        return self.flashObject.as_hideBill() if self._isDAAPIInited() else None

    def as_setBottomPanelInitDataS(self, data):
        return self.flashObject.as_setBottomPanelInitData(data) if self._isDAAPIInited() else None

    def as_setSwitchersDataS(self, data):
        return self.flashObject.as_setSwitchersData(data) if self._isDAAPIInited() else None

    def as_setBottomPanelTabsDataS(self, data):
        return self.flashObject.as_setBottomPanelTabsData(data) if self._isDAAPIInited() else None

    def as_setBottomPanelTabsPlusesS(self, pluses):
        return self.flashObject.as_setBottomPanelTabsPluses(pluses) if self._isDAAPIInited() else None

    def as_setCarouselDataS(self, data):
        return self.flashObject.as_setCarouselData(data) if self._isDAAPIInited() else None

    def as_setFilterDataS(self, data):
        return self.flashObject.as_setFilterData(data) if self._isDAAPIInited() else None

    def as_setBottomPanelPriceStateS(self, data):
        return self.flashObject.as_setBottomPanelPriceState(data) if self._isDAAPIInited() else None

    def as_setCarouselFiltersDataS(self, data):
        return self.flashObject.as_setCarouselFiltersData(data) if self._isDAAPIInited() else None

    def as_showPopoverBtnIconS(self, src, tooltip):
        return self.flashObject.as_showPopoverBtnIcon(src, tooltip) if self._isDAAPIInited() else None

    def as_getDataProviderS(self):
        return self.flashObject.as_getDataProvider() if self._isDAAPIInited() else None

    def as_setItemsPopoverBtnEnabledS(self, value):
        return self.flashObject.as_setItemsPopoverBtnEnabled(value) if self._isDAAPIInited() else None

    def as_setNotificationCountersS(self, data):
        return self.flashObject.as_setNotificationCounters(data) if self._isDAAPIInited() else None

    def as_scrollToSlotS(self, intCD):
        return self.flashObject.as_scrollToSlot(intCD) if self._isDAAPIInited() else None

    def as_playFilterBlinkS(self):
        return self.flashObject.as_playFilterBlink() if self._isDAAPIInited() else None
