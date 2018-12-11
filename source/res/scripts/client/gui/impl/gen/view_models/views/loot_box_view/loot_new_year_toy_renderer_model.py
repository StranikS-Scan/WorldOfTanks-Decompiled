# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/loot_box_view/loot_new_year_toy_renderer_model.py
from frameworks.wulf import Resource
from gui.impl.gen.view_models.views.loot_box_view.loot_def_renderer_model import LootDefRendererModel

class LootNewYearToyRendererModel(LootDefRendererModel):
    __slots__ = ()

    def getToyID(self):
        return self._getNumber(9)

    def setToyID(self, value):
        self._setNumber(9, value)

    def getDecorationImage(self):
        return self._getResource(10)

    def setDecorationImage(self, value):
        self._setResource(10, value)

    def getRankImage(self):
        return self._getResource(11)

    def setRankImage(self, value):
        self._setResource(11, value)

    def _initialize(self):
        super(LootNewYearToyRendererModel, self)._initialize()
        self._addNumberProperty('toyID', 0)
        self._addResourceProperty('decorationImage', Resource.INVALID)
        self._addResourceProperty('rankImage', Resource.INVALID)
