# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/loot_box_view/loot_vehicle_renderer_model.py
import typing
from gui.impl.gen.view_models.views.loot_box_view.loot_def_renderer_model import LootDefRendererModel
from gui.impl.gen.view_models.views.loot_box_view.loot_box_congrats_view_model import LootBoxCongratsViewModel

class LootVehicleRendererModel(LootDefRendererModel):
    __slots__ = ()

    @property
    def congratsViewModel(self):
        return self._getViewModel(9)

    def _initialize(self):
        super(LootVehicleRendererModel, self)._initialize()
        self._addViewModelProperty('congratsViewModel', LootBoxCongratsViewModel())
