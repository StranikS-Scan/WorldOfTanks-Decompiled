# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_main_view_model.py
from frameworks.wulf import ViewModel

class NewYearMainViewModel(ViewModel):
    __slots__ = ('onSwitchContent',)

    def __init__(self, properties=2, commands=1):
        super(NewYearMainViewModel, self).__init__(properties=properties, commands=commands)

    def getCurrentView(self):
        return self._getString(0)

    def setCurrentView(self, value):
        self._setString(0, value)

    def getNextView(self):
        return self._getString(1)

    def setNextView(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(NewYearMainViewModel, self)._initialize()
        self._addStringProperty('currentView', '')
        self._addStringProperty('nextView', '')
        self.onSwitchContent = self._addCommand('onSwitchContent')
