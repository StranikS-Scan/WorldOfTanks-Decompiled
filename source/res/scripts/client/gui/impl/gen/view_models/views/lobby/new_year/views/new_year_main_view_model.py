# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_main_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class NewYearMainViewModel(ViewModel):
    __slots__ = ('onCloseBtnClick', 'onSwitchContent')

    def __init__(self, properties=3, commands=2):
        super(NewYearMainViewModel, self).__init__(properties=properties, commands=commands)

    def getCurrentView(self):
        return self._getString(0)

    def setCurrentView(self, value):
        self._setString(0, value)

    def getItemsMenu(self):
        return self._getArray(1)

    def setItemsMenu(self, value):
        self._setArray(1, value)

    def getStartIndexMenu(self):
        return self._getNumber(2)

    def setStartIndexMenu(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(NewYearMainViewModel, self)._initialize()
        self._addStringProperty('currentView', '')
        self._addArrayProperty('itemsMenu', Array())
        self._addNumberProperty('startIndexMenu', 0)
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
        self.onSwitchContent = self._addCommand('onSwitchContent')
