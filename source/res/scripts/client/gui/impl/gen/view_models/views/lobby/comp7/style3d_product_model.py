# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/style3d_product_model.py
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel
from gui.impl.gen.view_models.views.lobby.comp7.base_product_model import BaseProductModel

class Style3dProductModel(BaseProductModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
        super(Style3dProductModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleInfo(self):
        return self._getViewModel(8)

    @staticmethod
    def getVehicleInfoType():
        return VehicleModel

    def getName(self):
        return self._getString(9)

    def setName(self, value):
        self._setString(9, value)

    def getCanGoToCustomization(self):
        return self._getBool(10)

    def setCanGoToCustomization(self, value):
        self._setBool(10, value)

    def _initialize(self):
        super(Style3dProductModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', VehicleModel())
        self._addStringProperty('name', '')
        self._addBoolProperty('canGoToCustomization', False)
