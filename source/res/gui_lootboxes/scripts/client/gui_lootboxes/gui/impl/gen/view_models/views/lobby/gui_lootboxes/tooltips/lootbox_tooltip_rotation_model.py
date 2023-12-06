# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/tooltips/lootbox_tooltip_rotation_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.vehicle_bonus_model import VehicleBonusModel

class LootboxTooltipRotationModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(LootboxTooltipRotationModel, self).__init__(properties=properties, commands=commands)

    @property
    def compensation(self):
        return self._getViewModel(0)

    @staticmethod
    def getCompensationType():
        return BonusModel

    def getStageRotation(self):
        return self._getNumber(1)

    def setStageRotation(self, value):
        self._setNumber(1, value)

    def getVehicleStageList(self):
        return self._getArray(2)

    def setVehicleStageList(self, value):
        self._setArray(2, value)

    @staticmethod
    def getVehicleStageListType():
        return VehicleBonusModel

    def _initialize(self):
        super(LootboxTooltipRotationModel, self)._initialize()
        self._addViewModelProperty('compensation', BonusModel())
        self._addNumberProperty('stageRotation', 1)
        self._addArrayProperty('vehicleStageList', Array())
