# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/header/battle_selector_event_progression_item.py
from battle_selector_extra_item import SelectorExtraItem
from shared_utils import findFirst
from battle_selector_event_progression_providers import EventProgressionDefaultDataProvider

class EventProgressionItem(SelectorExtraItem):

    def __init__(self, *dataProviders):
        self.__dataProviders = dataProviders or []
        self.__dataProvider = None
        self.__switchDataProvider()
        super(EventProgressionItem, self).__init__(label=self.getLabel(), data=self.getData(), order=self.getOrder(), selectorType=self.getSelectorType(), isVisible=self.__dataProvider.isVisible())
        self._isNew = False
        self.__prevSelectorType = self.getSelectorType()
        return

    def getLabel(self):
        return self.__dataProvider.getLabel()

    def getData(self):
        return self.__dataProvider.getData()

    def getOrder(self):
        return self.__dataProvider.getOrder()

    def getSelectorType(self):
        return self.__dataProvider.getSelectorType()

    def getVO(self):
        return self.__dataProvider.getVO()

    def getMainLabel(self):
        return self.__dataProvider.getMainLabel()

    def getInfoLabel(self):
        return self.__dataProvider.getInfoLabel()

    def getRibbonSrc(self):
        return self.__dataProvider.getRibbonSrc()

    def getFormattedLabel(self):
        return self.__dataProvider.getFormattedLabel()

    def isRandomBattle(self):
        return self.__dataProvider.isRandomBattle()

    def isSelected(self):
        return self.__dataProvider.isSelected()

    def isDisabled(self):
        return self.__dataProvider.isDisabled()

    def isSelectorBtnEnabled(self):
        return self.__dataProvider.isSelectorBtnEnabled()

    def select(self):
        self.__dataProvider.select()

    def __updateInternalData(self, provider):
        self.__prevSelectorType = self.getSelectorType()
        self._label = self.__dataProvider.getLabel()
        self._data = self.__dataProvider.getData()
        self._order = self.__dataProvider.getOrder()
        self._selectorType = self.__dataProvider.getSelectorType()
        self._isVisible = self.__dataProvider.isVisible()

    def _update(self, state):
        for dp in self.__dataProviders:
            if dp.isAvailable():
                dp.updateState()

        self.__switchDataProvider()
        if not self.__dataProvider.isDefault():
            if self.__prevSelectorType != self.getSelectorType():
                self.__updateInternalData(self.__dataProvider)
        self.__dataProvider.update(state)
        self._isVisible = self.__dataProvider.isVisible()

    def __switchDataProvider(self):
        self.__dataProvider = findFirst(lambda dp: dp.isVisible(), self.__dataProviders, EventProgressionDefaultDataProvider())
