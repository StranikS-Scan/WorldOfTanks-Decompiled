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

    def getMinigamesTries(self):
        return self._getNumber(2)

    def setMinigamesTries(self, value):
        self._setNumber(2, value)

    def getMinigamesTimeout(self):
        return self._getNumber(3)

    def setMinigamesTimeout(self, value):
        self._setNumber(3, value)

    def getIsMiniGamesEnabled(self):
        return self._getBool(4)

    def setIsMiniGamesEnabled(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(FestivalInfoViewModel, self)._initialize()
        self._addNumberProperty('fullRandomCost', 5)
        self._addNumberProperty('randomCost', 25)
        self._addNumberProperty('minigamesTries', 0)
        self._addNumberProperty('minigamesTimeout', 0)
        self._addBoolProperty('isMiniGamesEnabled', False)
        self.onVideoClicked = self._addCommand('onVideoClicked')
