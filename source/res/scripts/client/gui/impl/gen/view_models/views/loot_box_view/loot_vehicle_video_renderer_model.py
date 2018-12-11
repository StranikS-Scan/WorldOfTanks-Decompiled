# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/loot_box_view/loot_vehicle_video_renderer_model.py
import typing
from gui.impl.gen.view_models.views.loot_box_view.loot_video_renderer_model import LootVideoRendererModel
from gui.impl.gen.view_models.views.loot_box_view.loot_box_congrats_view_model import LootBoxCongratsViewModel

class LootVehicleVideoRendererModel(LootVideoRendererModel):
    __slots__ = ()

    @property
    def congratsViewModel(self):
        return self._getViewModel(10)

    def _initialize(self):
        super(LootVehicleVideoRendererModel, self)._initialize()
        self._addViewModelProperty('congratsViewModel', LootBoxCongratsViewModel())
