# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/festival/festival_info_view_model.py
from frameworks.wulf import ViewModel

class FestivalInfoViewModel(ViewModel):
    __slots__ = ('onVideoClicked',)

    def getFullRandomCost(self):
        return self._getNumber(0)

    def setFullRandomCost(self, value):
        self._setNumber(0, value)

    def getRandomCost(self):
        return self._getNumber(1)

    def setRandomCost(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(FestivalInfoViewModel, self)._initialize()
        self._addNumberProperty('fullRandomCost', 5)
        self._addNumberProperty('randomCost', 25)
        self.onVideoClicked = self._addCommand('onVideoClicked')
