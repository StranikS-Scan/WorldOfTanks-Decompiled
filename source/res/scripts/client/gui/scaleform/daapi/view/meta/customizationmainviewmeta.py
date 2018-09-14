# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CustomizationMainViewMeta.py
from gui.Scaleform.framework.entities.View import View

class CustomizationMainViewMeta(View):

    def showBuyWindow(self):
        self._printOverrideError('showBuyWindow')

    def closeWindow(self):
        self._printOverrideError('closeWindow')

    def installCustomizationElement(self, id):
        self._printOverrideError('installCustomizationElement')

    def goToTask(self, id):
        self._printOverrideError('goToTask')

    def removeFromShoppingBasket(self, slotId, groupId, id):
        self._printOverrideError('removeFromShoppingBasket')

    def changeCarouselFilter(self):
        self._printOverrideError('changeCarouselFilter')

    def setDurationType(self, id):
        self._printOverrideError('setDurationType')

    def showPurchased(self, value):
        self._printOverrideError('showPurchased')

    def removeSlot(self, groupId, id):
        self._printOverrideError('removeSlot')

    def revertSlot(self, groupId, id):
        self._printOverrideError('revertSlot')

    def showGroup(self, groupId, id):
        self._printOverrideError('showGroup')

    def backToSelectorGroup(self):
        self._printOverrideError('backToSelectorGroup')

    def as_showBuyingPanelS(self):
        return self.flashObject.as_showBuyingPanel() if self._isDAAPIInited() else None

    def as_hideBuyingPanelS(self):
        return self.flashObject.as_hideBuyingPanel() if self._isDAAPIInited() else None

    def as_setHeaderDataS(self, data):
        """
        :param data: Represented by CustomizationHeaderVO (AS)
        """
        return self.flashObject.as_setHeaderData(data) if self._isDAAPIInited() else None

    def as_setBonusPanelDataS(self, data):
        """
        :param data: Represented by CustomizationBonusPanelVO (AS)
        """
        return self.flashObject.as_setBonusPanelData(data) if self._isDAAPIInited() else None

    def as_setCarouselDataS(self, data):
        """
        :param data: Represented by CarouselDataVO (AS)
        """
        return self.flashObject.as_setCarouselData(data) if self._isDAAPIInited() else None

    def as_setCarouselInitS(self, data):
        """
        :param data: Represented by CarouselInitVO (AS)
        """
        return self.flashObject.as_setCarouselInit(data) if self._isDAAPIInited() else None

    def as_setCarouselFilterDataS(self, data):
        """
        :param data: Represented by CustomizationCarouselFilterVO (AS)
        """
        return self.flashObject.as_setCarouselFilterData(data) if self._isDAAPIInited() else None

    def as_setBottomPanelHeaderS(self, data):
        """
        :param data: Represented by BottomPanelVO (AS)
        """
        return self.flashObject.as_setBottomPanelHeader(data) if self._isDAAPIInited() else None

    def as_setSlotsPanelDataS(self, data):
        """
        :param data: Represented by CustomizationSlotsPanelVO (AS)
        """
        return self.flashObject.as_setSlotsPanelData(data) if self._isDAAPIInited() else None

    def as_showSelectorItemS(self, id):
        return self.flashObject.as_showSelectorItem(id) if self._isDAAPIInited() else None

    def as_showSelectorGroupS(self):
        return self.flashObject.as_showSelectorGroup() if self._isDAAPIInited() else None

    def as_updateSlotS(self, data):
        """
        :param data: Represented by CustomizationSlotUpdateVO (AS)
        """
        return self.flashObject.as_updateSlot(data) if self._isDAAPIInited() else None

    def as_setBottomPanelInitDataS(self, data):
        """
        :param data: Represented by CustomizationBottomPanelInitVO (AS)
        """
        return self.flashObject.as_setBottomPanelInitData(data) if self._isDAAPIInited() else None
