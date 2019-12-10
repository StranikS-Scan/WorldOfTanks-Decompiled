# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/loot_box_view/loot_new_year_fragments_renderer_model.py
from gui.impl.gen.view_models.views.loot_box_view.loot_def_renderer_model import LootDefRendererModel

class LootNewYearFragmentsRendererModel(LootDefRendererModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(LootNewYearFragmentsRendererModel, self).__init__(properties=properties, commands=commands)

    def getCount(self):
        return self._getNumber(9)

    def setCount(self, value):
        self._setNumber(9, value)

    def _initialize(self):
        super(LootNewYearFragmentsRendererModel, self)._initialize()
        self._addNumberProperty('count', 0)
