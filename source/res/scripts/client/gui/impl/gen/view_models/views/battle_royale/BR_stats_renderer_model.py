# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle_royale/BR_stats_renderer_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class BRStatsRendererModel(ViewModel):
    __slots__ = ('statsAnimStart',)

    def getImage(self):
        return self._getResource(0)

    def setImage(self, value):
        self._setResource(0, value)

    def getStatValue(self):
        return self._getNumber(1)

    def setStatValue(self, value):
        self._setNumber(1, value)

    def getTotalPlayersValue(self):
        return self._getNumber(2)

    def setTotalPlayersValue(self, value):
        self._setNumber(2, value)

    def getWinner(self):
        return self._getBool(3)

    def setWinner(self, value):
        self._setBool(3, value)

    def getId(self):
        return self._getNumber(4)

    def setId(self, value):
        self._setNumber(4, value)

    def getTooltip(self):
        return self._getString(5)

    def setTooltip(self, value):
        self._setString(5, value)

    def getIsSeparator(self):
        return self._getBool(6)

    def setIsSeparator(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(BRStatsRendererModel, self)._initialize()
        self._addResourceProperty('image', R.invalid())
        self._addNumberProperty('statValue', 0)
        self._addNumberProperty('totalPlayersValue', 0)
        self._addBoolProperty('winner', False)
        self._addNumberProperty('id', -1)
        self._addStringProperty('tooltip', '')
        self._addBoolProperty('isSeparator', False)
        self.statsAnimStart = self._addCommand('statsAnimStart')
