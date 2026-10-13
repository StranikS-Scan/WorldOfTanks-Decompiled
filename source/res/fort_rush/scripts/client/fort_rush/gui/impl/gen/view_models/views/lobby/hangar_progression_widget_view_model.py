# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/gen/view_models/views/lobby/hangar_progression_widget_view_model.py
from frameworks.wulf import ViewModel

class HangarProgressionWidgetViewModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=6, commands=1):
        super(HangarProgressionWidgetViewModel, self).__init__(properties=properties, commands=commands)

    def getIsAvailable(self):
        return self._getBool(0)

    def setIsAvailable(self, value):
        self._setBool(0, value)

    def getAllCollected(self):
        return self._getBool(1)

    def setAllCollected(self, value):
        self._setBool(1, value)

    def getIsNewItem(self):
        return self._getBool(2)

    def setIsNewItem(self, value):
        self._setBool(2, value)

    def getCurrentProgression(self):
        return self._getNumber(3)

    def setCurrentProgression(self, value):
        self._setNumber(3, value)

    def getTotalProgression(self):
        return self._getNumber(4)

    def setTotalProgression(self, value):
        self._setNumber(4, value)

    def getCurrentProgressionStage(self):
        return self._getNumber(5)

    def setCurrentProgressionStage(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(HangarProgressionWidgetViewModel, self)._initialize()
        self._addBoolProperty('isAvailable', False)
        self._addBoolProperty('allCollected', False)
        self._addBoolProperty('isNewItem', False)
        self._addNumberProperty('currentProgression', 0)
        self._addNumberProperty('totalProgression', 0)
        self._addNumberProperty('currentProgressionStage', 0)
        self.onClick = self._addCommand('onClick')
