# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/loot_box_view/crew_book_renderer_model.py
from gui.impl.gen.view_models.views.loot_box_view.loot_animated_renderer_model import LootAnimatedRendererModel
from gui.impl.gen.view_models.views.loot_box_view.congrats_view_model import CongratsViewModel

class CrewBookRendererModel(LootAnimatedRendererModel):
    __slots__ = ()

    def __init__(self, properties=13, commands=0):
        super(CrewBookRendererModel, self).__init__(properties=properties, commands=commands)

    @property
    def congratsViewModel(self):
        return self._getViewModel(12)

    def _initialize(self):
        super(CrewBookRendererModel, self)._initialize()
        self._addViewModelProperty('congratsViewModel', CongratsViewModel())
