# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/wt_header_widget_view_model.py
from frameworks.wulf import ViewModel

class WtHeaderWidgetViewModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=6, commands=1):
        super(WtHeaderWidgetViewModel, self).__init__(properties=properties, commands=commands)

    def getAllCollected(self):
        return self._getBool(0)

    def setAllCollected(self, value):
        self._setBool(0, value)

    def getTooltipID(self):
        return self._getNumber(1)

    def setTooltipID(self, value):
        self._setNumber(1, value)

    def getIsFirstShow(self):
        return self._getBool(2)

    def setIsFirstShow(self, value):
        self._setBool(2, value)

    def getIsNewItem(self):
        return self._getBool(3)

    def setIsNewItem(self, value):
        self._setBool(3, value)

    def getCurrentProgression(self):
        return self._getNumber(4)

    def setCurrentProgression(self, value):
        self._setNumber(4, value)

    def getTotalProgression(self):
        return self._getNumber(5)

    def setTotalProgression(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(WtHeaderWidgetViewModel, self)._initialize()
        self._addBoolProperty('allCollected', False)
        self._addNumberProperty('tooltipID', 0)
        self._addBoolProperty('isFirstShow', False)
        self._addBoolProperty('isNewItem', False)
        self._addNumberProperty('currentProgression', 0)
        self._addNumberProperty('totalProgression', 0)
        self.onClick = self._addCommand('onClick')
