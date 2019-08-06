# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/festival/festival_random_congratulation_view_model.py
from frameworks.wulf import ViewModel

class FestivalRandomCongratulationViewModel(ViewModel):
    __slots__ = ()

    def getType(self):
        return self._getString(0)

    def setType(self, value):
        self._setString(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getId(self):
        return self._getNumber(2)

    def setId(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(FestivalRandomCongratulationViewModel, self)._initialize()
        self._addStringProperty('type', '')
        self._addStringProperty('name', '')
        self._addNumberProperty('id', 0)
