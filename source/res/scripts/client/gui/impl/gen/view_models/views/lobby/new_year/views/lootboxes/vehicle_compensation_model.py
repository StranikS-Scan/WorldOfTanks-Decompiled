# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/lootboxes/vehicle_compensation_model.py
from gui.impl.gen.view_models.views.lobby.battle_pass.vehicle_bonus_model import VehicleBonusModel

class VehicleCompensationModel(VehicleBonusModel):
    __slots__ = ()

    def __init__(self, properties=21, commands=0):
        super(VehicleCompensationModel, self).__init__(properties=properties, commands=commands)

    @property
    def compensatedItem(self):
        return self._getViewModel(20)

    @staticmethod
    def getCompensatedItemType():
        return VehicleBonusModel

    def _initialize(self):
        super(VehicleCompensationModel, self)._initialize()
        self._addViewModelProperty('compensatedItem', VehicleBonusModel())
