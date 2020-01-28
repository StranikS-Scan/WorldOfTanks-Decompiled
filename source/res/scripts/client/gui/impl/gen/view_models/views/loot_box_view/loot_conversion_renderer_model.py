# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/loot_box_view/loot_conversion_renderer_model.py
from gui.impl.gen import R
from gui.impl.gen.view_models.views.loot_box_view.loot_animated_renderer_model import LootAnimatedRendererModel

class LootConversionRendererModel(LootAnimatedRendererModel):
    __slots__ = ()

    def __init__(self, properties=14, commands=0):
        super(LootConversionRendererModel, self).__init__(properties=properties, commands=commands)

    def getIconFrom(self):
        return self._getResource(13)

    def setIconFrom(self, value):
        self._setResource(13, value)

    def _initialize(self):
        super(LootConversionRendererModel, self)._initialize()
        self._addResourceProperty('iconFrom', R.invalid())
