# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/selected_vehicle_view_model.py
from last_stand.gui.impl.gen.view_models.views.lobby.vehicle_title_view_model import VehicleTitleViewModel
from gui.impl.gen.view_models.views.lobby.prestige.prestige_emblem_model import PrestigeEmblemModel

class SelectedVehicleViewModel(VehicleTitleViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(SelectedVehicleViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def emblem(self):
        return self._getViewModel(7)

    @staticmethod
    def getEmblemType():
        return PrestigeEmblemModel

    def _initialize(self):
        super(SelectedVehicleViewModel, self)._initialize()
        self._addViewModelProperty('emblem', PrestigeEmblemModel())
