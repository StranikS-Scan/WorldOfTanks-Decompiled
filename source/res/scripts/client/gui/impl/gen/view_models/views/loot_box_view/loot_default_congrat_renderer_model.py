# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/loot_box_view/loot_default_congrat_renderer_model.py
from gui.impl.gen.view_models.views.loot_box_view.congrats_view_model import CongratsViewModel
from gui.impl.gen.view_models.views.loot_box_view.loot_def_renderer_model import LootDefRendererModel

class LootDefaultCongratRendererModel(LootDefRendererModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=0):
        super(LootDefaultCongratRendererModel, self).__init__(properties=properties, commands=commands)

    @property
    def congratsViewModel(self):
        return self._getViewModel(11)

    def _initialize(self):
        super(LootDefaultCongratRendererModel, self)._initialize()
        self._addViewModelProperty('congratsViewModel', CongratsViewModel())
