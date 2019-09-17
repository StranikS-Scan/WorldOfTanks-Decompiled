# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/race/racing_widget_view_model.py
from frameworks.wulf import ViewModel

class RacingWidgetViewModel(ViewModel):
    __slots__ = ('onWidgetClick',)

    def getTotalCount(self):
        return self._getString(0)

    def setTotalCount(self, value):
        self._setString(0, value)

    def getAvailableCount(self):
        return self._getString(1)

    def setAvailableCount(self, value):
        self._setString(1, value)

    def getTimeout(self):
        return self._getString(2)

    def setTimeout(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(RacingWidgetViewModel, self)._initialize()
        self._addStringProperty('totalCount', '')
        self._addStringProperty('availableCount', '')
        self._addStringProperty('timeout', '')
        self.onWidgetClick = self._addCommand('onWidgetClick')
