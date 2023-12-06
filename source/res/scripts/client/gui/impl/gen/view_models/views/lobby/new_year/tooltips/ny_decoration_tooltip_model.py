# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_decoration_tooltip_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class NyDecorationTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=13, commands=0):
        super(NyDecorationTooltipModel, self).__init__(properties=properties, commands=commands)

    def getShardsPrice(self):
        return self._getNumber(0)

    def setShardsPrice(self, value):
        self._setNumber(0, value)

    def getRank(self):
        return self._getString(1)

    def setRank(self, value):
        self._setString(1, value)

    def getRankNumber(self):
        return self._getNumber(2)

    def setRankNumber(self, value):
        self._setNumber(2, value)

    def getSetting(self):
        return self._getString(3)

    def setSetting(self, value):
        self._setString(3, value)

    def getName(self):
        return self._getResource(4)

    def setName(self, value):
        self._setResource(4, value)

    def getDescription(self):
        return self._getResource(5)

    def setDescription(self, value):
        self._setResource(5, value)

    def getCount(self):
        return self._getNumber(6)

    def setCount(self, value):
        self._setNumber(6, value)

    def getType(self):
        return self._getString(7)

    def setType(self, value):
        self._setString(7, value)

    def getIcon(self):
        return self._getResource(8)

    def setIcon(self, value):
        self._setResource(8, value)

    def getUsedSlotAtmosphere(self):
        return self._getNumber(9)

    def setUsedSlotAtmosphere(self, value):
        self._setNumber(9, value)

    def getIsMaxAtmosphereLevel(self):
        return self._getBool(10)

    def setIsMaxAtmosphereLevel(self, value):
        self._setBool(10, value)

    def getIsPostNYEnabled(self):
        return self._getBool(11)

    def setIsPostNYEnabled(self, value):
        self._setBool(11, value)

    def getIsFinished(self):
        return self._getBool(12)

    def setIsFinished(self, value):
        self._setBool(12, value)

    def _initialize(self):
        super(NyDecorationTooltipModel, self)._initialize()
        self._addNumberProperty('shardsPrice', 0)
        self._addStringProperty('rank', '')
        self._addNumberProperty('rankNumber', 0)
        self._addStringProperty('setting', '')
        self._addResourceProperty('name', R.invalid())
        self._addResourceProperty('description', R.invalid())
        self._addNumberProperty('count', 0)
        self._addStringProperty('type', '')
        self._addResourceProperty('icon', R.invalid())
        self._addNumberProperty('usedSlotAtmosphere', 0)
        self._addBoolProperty('isMaxAtmosphereLevel', False)
        self._addBoolProperty('isPostNYEnabled', False)
        self._addBoolProperty('isFinished', False)
