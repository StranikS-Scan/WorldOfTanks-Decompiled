# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ChristmasMainViewMeta.py
from gui.Scaleform.framework.entities.View import View

class ChristmasMainViewMeta(View):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends View
    """

    def installItem(self, itemId, slotId):
        self._printOverrideError('installItem')

    def moveItem(self, srcSlotId, targetSlotId):
        self._printOverrideError('moveItem')

    def uninstallItem(self, slotId):
        self._printOverrideError('uninstallItem')

    def showConversion(self):
        self._printOverrideError('showConversion')

    def switchOffNewItem(self, itemId):
        self._printOverrideError('switchOffNewItem')

    def applyRankFilter(self, filterId):
        self._printOverrideError('applyRankFilter')

    def applyTypeFilter(self, filterId):
        self._printOverrideError('applyTypeFilter')

    def onChangeTab(self, tabId):
        self._printOverrideError('onChangeTab')

    def onEmptyListBtnClick(self):
        self._printOverrideError('onEmptyListBtnClick')

    def closeWindow(self):
        self._printOverrideError('closeWindow')

    def showRules(self):
        self._printOverrideError('showRules')

    def switchCamera(self):
        self._printOverrideError('switchCamera')

    def convertItems(self):
        self._printOverrideError('convertItems')

    def cancelConversion(self):
        self._printOverrideError('cancelConversion')

    def onConversionAnimationComplete(self):
        self._printOverrideError('onConversionAnimationComplete')

    def as_setStaticDataS(self, data):
        """
        :param data: Represented by MainViewStaticDataVO (AS)
        """
        return self.flashObject.as_setStaticData(data) if self._isDAAPIInited() else None

    def as_setFiltersS(self, ranks, types):
        """
        :param ranks: Represented by ChristmasFiltersVO (AS)
        :param types: Represented by ChristmasFiltersVO (AS)
        """
        return self.flashObject.as_setFilters(ranks, types) if self._isDAAPIInited() else None

    def as_setProgressS(self, data):
        """
        :param data: Represented by ProgressBarVO (AS)
        """
        return self.flashObject.as_setProgress(data) if self._isDAAPIInited() else None

    def as_selectSlotsTabS(self, index):
        return self.flashObject.as_selectSlotsTab(index) if self._isDAAPIInited() else None

    def as_showSlotsViewS(self, linkage):
        return self.flashObject.as_showSlotsView(linkage) if self._isDAAPIInited() else None

    def as_setSlotsDataS(self, data):
        """
        :param data: Represented by SlotsDataClassVO (AS)
        """
        return self.flashObject.as_setSlotsData(data) if self._isDAAPIInited() else None

    def as_updateSlotS(self, data):
        """
        :param data: Represented by SlotVO (AS)
        """
        return self.flashObject.as_updateSlot(data) if self._isDAAPIInited() else None

    def as_scrollToItemS(self, index):
        return self.flashObject.as_scrollToItem(index) if self._isDAAPIInited() else None

    def as_getDecorationsDPS(self):
        return self.flashObject.as_getDecorationsDP() if self._isDAAPIInited() else None

    def as_setEmptyListDataS(self, visible, data):
        """
        :param data: Represented by InfoMessageVO (AS)
        """
        return self.flashObject.as_setEmptyListData(visible, data) if self._isDAAPIInited() else None

    def as_updateConversionBtnS(self, enabled, icon):
        return self.flashObject.as_updateConversionBtn(enabled, icon) if self._isDAAPIInited() else None
