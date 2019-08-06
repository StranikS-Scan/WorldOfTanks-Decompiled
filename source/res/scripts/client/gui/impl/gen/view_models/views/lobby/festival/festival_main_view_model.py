# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/festival/festival_main_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from frameworks.wulf import View

class FestivalMainViewModel(ViewModel):
    __slots__ = ('onSwitchContent', 'onCloseBtnClicked', 'onCardInfoClicked')

    def getContent(self):
        return self._getView(0)

    def setContent(self, value):
        self._setView(0, value)

    def getCustomizationCardView(self):
        return self._getView(1)

    def setCustomizationCardView(self, value):
        self._setView(1, value)

    def getTicketsStr(self):
        return self._getString(2)

    def setTicketsStr(self, value):
        self._setString(2, value)

    def getReceivedItems(self):
        return self._getNumber(3)

    def setReceivedItems(self, value):
        self._setNumber(3, value)

    def getTotalItems(self):
        return self._getNumber(4)

    def setTotalItems(self, value):
        self._setNumber(4, value)

    def getViews(self):
        return self._getArray(5)

    def setViews(self, value):
        self._setArray(5, value)

    def getCurrentView(self):
        return self._getString(6)

    def setCurrentView(self, value):
        self._setString(6, value)

    def getStartIndex(self):
        return self._getNumber(7)

    def setStartIndex(self, value):
        self._setNumber(7, value)

    def getFirstEntering(self):
        return self._getBool(8)

    def setFirstEntering(self, value):
        self._setBool(8, value)

    def getTriggerRestoreAlpha(self):
        return self._getBool(9)

    def setTriggerRestoreAlpha(self, value):
        self._setBool(9, value)

    def _initialize(self):
        super(FestivalMainViewModel, self)._initialize()
        self._addViewProperty('content')
        self._addViewProperty('customizationCardView')
        self._addStringProperty('ticketsStr', '')
        self._addNumberProperty('receivedItems', 0)
        self._addNumberProperty('totalItems', 0)
        self._addArrayProperty('views', Array())
        self._addStringProperty('currentView', '')
        self._addNumberProperty('startIndex', -1)
        self._addBoolProperty('firstEntering', False)
        self._addBoolProperty('triggerRestoreAlpha', False)
        self.onSwitchContent = self._addCommand('onSwitchContent')
        self.onCloseBtnClicked = self._addCommand('onCloseBtnClicked')
        self.onCardInfoClicked = self._addCommand('onCardInfoClicked')
