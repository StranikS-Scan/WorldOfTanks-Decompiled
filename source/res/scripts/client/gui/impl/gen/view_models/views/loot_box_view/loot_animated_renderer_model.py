# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/loot_box_view/loot_animated_renderer_model.py
from gui.impl.gen import R
from gui.impl.gen.view_models.views.loot_box_view.loot_def_renderer_model import LootDefRendererModel

class LootAnimatedRendererModel(LootDefRendererModel):
    __slots__ = ()
    SWF_ANIMATION = 0
    MC_ANIMATION = 1

    def __init__(self, properties=17, commands=0):
        super(LootAnimatedRendererModel, self).__init__(properties=properties, commands=commands)

    def getAnimationType(self):
        return self._getNumber(14)

    def setAnimationType(self, value):
        self._setNumber(14, value)

    def getAnimation(self):
        return self._getResource(15)

    def setAnimation(self, value):
        self._setResource(15, value)

    def getAnimationSound(self):
        return self._getResource(16)

    def setAnimationSound(self, value):
        self._setResource(16, value)

    def _initialize(self):
        super(LootAnimatedRendererModel, self)._initialize()
        self._addNumberProperty('animationType', 0)
        self._addResourceProperty('animation', R.invalid())
        self._addResourceProperty('animationSound', R.invalid())
