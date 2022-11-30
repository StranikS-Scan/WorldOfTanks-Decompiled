# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/loot_box_view/loot_new_year_toy_renderer_model.py
from gui.impl.gen import R
from gui.impl.gen.view_models.views.loot_box_view.loot_def_renderer_model import LootDefRendererModel

class LootNewYearToyRendererModel(LootDefRendererModel):
    __slots__ = ()

    def __init__(self, properties=20, commands=0):
        super(LootNewYearToyRendererModel, self).__init__(properties=properties, commands=commands)

    def getToyID(self):
        return self._getNumber(14)

    def setToyID(self, value):
        self._setNumber(14, value)

    def getDecorationImage(self):
        return self._getResource(15)

    def setDecorationImage(self, value):
        self._setResource(15, value)

    def getRankImage(self):
        return self._getResource(16)

    def setRankImage(self, value):
        self._setResource(16, value)

    def getIsMega(self):
        return self._getBool(17)

    def setIsMega(self, value):
        self._setBool(17, value)

    def getRank(self):
        return self._getNumber(18)

    def setRank(self, value):
        self._setNumber(18, value)

    def getIsNew(self):
        return self._getBool(19)

    def setIsNew(self, value):
        self._setBool(19, value)

    def _initialize(self):
        super(LootNewYearToyRendererModel, self)._initialize()
        self._addNumberProperty('toyID', 0)
        self._addResourceProperty('decorationImage', R.invalid())
        self._addResourceProperty('rankImage', R.invalid())
        self._addBoolProperty('isMega', False)
        self._addNumberProperty('rank', 0)
        self._addBoolProperty('isNew', False)
