# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/paragons/tooltips/blueprint_universal_tooltip_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel

class BlueprintUniversalTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(BlueprintUniversalTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleInfoType():
        return VehicleModel

    def getBlueprintFragments(self):
        return self._getNumber(1)

    def setBlueprintFragments(self, value):
        self._setNumber(1, value)

    def getExperience(self):
        return self._getNumber(2)

    def setExperience(self, value):
        self._setNumber(2, value)

    def getDiscount(self):
        return self._getNumber(3)

    def setDiscount(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(BlueprintUniversalTooltipModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', VehicleModel())
        self._addNumberProperty('blueprintFragments', 0)
        self._addNumberProperty('experience', 0)
        self._addNumberProperty('discount', 0)
