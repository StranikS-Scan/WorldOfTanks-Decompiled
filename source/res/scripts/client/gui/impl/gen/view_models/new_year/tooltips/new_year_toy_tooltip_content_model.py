# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/new_year/tooltips/new_year_toy_tooltip_content_model.py
from frameworks.wulf import ViewModel

class NewYearToyTooltipContentModel(ViewModel):
    __slots__ = ()

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
        return self._getString(3)

    def setRankNumber(self, value):
        self._setString(3, value)

    def getSetting(self):
        return self._getString(4)

    def setSetting(self, value):
        self._setString(4, value)

    def getLocalName(self):
        return self._getString(5)

    def setLocalName(self, value):
        self._setString(5, value)

    def _initialize(self):
        super(NewYearToyTooltipContentModel, self)._initialize()
        self._addNumberProperty('shardsPrice', 0)
        self._addNumberProperty('atmospherePoint', 0)
        self._addStringProperty('rank', '')
        self._addStringProperty('rankNumber', '')
        self._addStringProperty('setting', '')
        self._addStringProperty('localName', '')
