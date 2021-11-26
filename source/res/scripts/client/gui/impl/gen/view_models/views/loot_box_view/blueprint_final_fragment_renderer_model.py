# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/loot_box_view/blueprint_final_fragment_renderer_model.py
from gui.impl.gen.view_models.views.loot_box_view.blueprint_congrats_model import BlueprintCongratsModel
from gui.impl.gen.view_models.views.loot_box_view.loot_animated_renderer_model import LootAnimatedRendererModel

class BlueprintFinalFragmentRendererModel(LootAnimatedRendererModel):
    __slots__ = ()

    def __init__(self, properties=17, commands=0):
        super(BlueprintFinalFragmentRendererModel, self).__init__(properties=properties, commands=commands)

    @property
    def congratsViewModel(self):
        return self._getViewModel(16)

    def _initialize(self):
        super(BlueprintFinalFragmentRendererModel, self)._initialize()
        self._addViewModelProperty('congratsViewModel', BlueprintCongratsModel())
