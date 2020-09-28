# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_event_header_widget_view_model.py
from frameworks.wulf import ViewModel

class WtEventHeaderWidgetViewModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=5, commands=1):
        super(WtEventHeaderWidgetViewModel, self).__init__(properties=properties, commands=commands)

    def getAllCollected(self):
        return self._getBool(0)

    def setAllCollected(self, value):
        self._setBool(0, value)

    def getIsSmall(self):
        return self._getBool(1)

    def setIsSmall(self, value):
        self._setBool(1, value)

    def getTooltipID(self):
        return self._getNumber(2)

    def setTooltipID(self, value):
        self._setNumber(2, value)

    def getIsFirstShow(self):
        return self._getBool(3)

    def setIsFirstShow(self, value):
        self._setBool(3, value)

    def getIsNewItem(self):
        return self._getBool(4)

    def setIsNewItem(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(WtEventHeaderWidgetViewModel, self)._initialize()
        self._addBoolProperty('allCollected', False)
        self._addBoolProperty('isSmall', False)
        self._addNumberProperty('tooltipID', 0)
        self._addBoolProperty('isFirstShow', False)
        self._addBoolProperty('isNewItem', False)
        self.onClick = self._addCommand('onClick')
