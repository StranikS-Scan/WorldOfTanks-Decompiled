# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_regular_toy_tooltip_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class NyRegularToyTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(NyRegularToyTooltipModel, self).__init__(properties=properties, commands=commands)

    def getShardsPrice(self):
        return self._getNumber(0)

    def setShardsPrice(self, value):
        self._setNumber(0, value)

    def getAtmospherePoint(self):
        return self._getNumber(1)

    def setAtmospherePoint(self, value):
        self._setNumber(1, value)

    def getRank(self):
        return self._getString(2)

    def setRank(self, value):
        self._setString(2, value)

    def getRankNumber(self):
        return self._getNumber(3)

    def setRankNumber(self, value):
        self._setNumber(3, value)

    def getSetting(self):
        return self._getString(4)

    def setSetting(self, value):
        self._setString(4, value)

    def getName(self):
        return self._getResource(5)

    def setName(self, value):
        self._setResource(5, value)

    def getDescription(self):
        return self._getResource(6)

    def setDescription(self, value):
        self._setResource(6, value)

    def getCount(self):
        return self._getNumber(7)

    def setCount(self, value):
        self._setNumber(7, value)

    def getType(self):
        return self._getString(8)

    def setType(self, value):
        self._setString(8, value)

    def _initialize(self):
        super(NyRegularToyTooltipModel, self)._initialize()
        self._addNumberProperty('shardsPrice', 0)
        self._addNumberProperty('atmospherePoint', 0)
        self._addStringProperty('rank', '')
        self._addNumberProperty('rankNumber', 0)
        self._addStringProperty('setting', '')
        self._addResourceProperty('name', R.invalid())
        self._addResourceProperty('description', R.invalid())
        self._addNumberProperty('count', 0)
        self._addStringProperty('type', '')
