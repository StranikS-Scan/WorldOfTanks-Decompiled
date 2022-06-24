# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/loot_box_view/blueprint_fragment_renderer_model.py
from gui.impl.gen.view_models.views.loot_box_view.blueprint_congrats_model import BlueprintCongratsModel
from gui.impl.gen.view_models.views.loot_box_view.loot_def_renderer_model import LootDefRendererModel

class BlueprintFragmentRendererModel(LootDefRendererModel):
    __slots__ = ()

    def __init__(self, properties=14, commands=0):
        super(BlueprintFragmentRendererModel, self).__init__(properties=properties, commands=commands)

    @property
    def congratsViewModel(self):
        return self._getViewModel(13)

    @staticmethod
    def getCongratsViewModelType():
        return BlueprintCongratsModel

    def _initialize(self):
        super(BlueprintFragmentRendererModel, self)._initialize()
        self._addViewModelProperty('congratsViewModel', BlueprintCongratsModel())
