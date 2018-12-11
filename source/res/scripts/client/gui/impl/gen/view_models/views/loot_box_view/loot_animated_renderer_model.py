# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/loot_box_view/loot_animated_renderer_model.py
from frameworks.wulf import Resource
from gui.impl.gen.view_models.views.loot_box_view.loot_def_renderer_model import LootDefRendererModel

class LootAnimatedRendererModel(LootDefRendererModel):
    __slots__ = ()
    SWF_ANIMATION = 0
    MC_ANIMATION = 1

    def getAnimationType(self):
        return self._getNumber(9)

    def setAnimationType(self, value):
        self._setNumber(9, value)

    def getAnimation(self):
        return self._getString(10)

    def setAnimation(self, value):
        self._setString(10, value)

    def getAnimationSound(self):
        return self._getResource(11)

    def setAnimationSound(self, value):
        self._setResource(11, value)

    def _initialize(self):
        super(LootAnimatedRendererModel, self)._initialize()
        self._addNumberProperty('animationType', 0)
        self._addStringProperty('animation', '')
        self._addResourceProperty('animationSound', Resource.INVALID)
