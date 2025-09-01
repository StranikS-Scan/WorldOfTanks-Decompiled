# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/widgets/hangar_progression_view_model.py
from frameworks.wulf import ViewModel

class HangarProgressionViewModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=4, commands=1):
        super(HangarProgressionViewModel, self).__init__(properties=properties, commands=commands)

    def getAllCollected(self):
        return self._getBool(0)

    def setAllCollected(self, value):
        self._setBool(0, value)

    def getIsNewItem(self):
        return self._getBool(1)

    def setIsNewItem(self, value):
        self._setBool(1, value)

    def getCurrentProgression(self):
        return self._getNumber(2)

    def setCurrentProgression(self, value):
        self._setNumber(2, value)

    def getTotalProgression(self):
        return self._getNumber(3)

    def setTotalProgression(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(HangarProgressionViewModel, self)._initialize()
        self._addBoolProperty('allCollected', False)
        self._addBoolProperty('isNewItem', False)
        self._addNumberProperty('currentProgression', 0)
        self._addNumberProperty('totalProgression', 0)
        self.onClick = self._addCommand('onClick')
