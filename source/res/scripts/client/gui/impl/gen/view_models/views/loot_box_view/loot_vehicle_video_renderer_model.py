# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/loot_box_view/loot_vehicle_video_renderer_model.py
from gui.impl.gen.view_models.views.loot_box_view.congrats_view_model import CongratsViewModel
from gui.impl.gen.view_models.views.loot_box_view.loot_video_renderer_model import LootVideoRendererModel

class LootVehicleVideoRendererModel(LootVideoRendererModel):
    __slots__ = ()

    def __init__(self, properties=15, commands=0):
        super(LootVehicleVideoRendererModel, self).__init__(properties=properties, commands=commands)

    @property
    def congratsViewModel(self):
        return self._getViewModel(14)

    @staticmethod
    def getCongratsViewModelType():
        return CongratsViewModel

    def _initialize(self):
        super(LootVehicleVideoRendererModel, self)._initialize()
        self._addViewModelProperty('congratsViewModel', CongratsViewModel())
