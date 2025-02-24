# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/style3d_product_model.py
from comp7.gui.impl.gen.view_models.views.lobby.base_product_model import BaseProductModel
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel

class Style3dProductModel(BaseProductModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=0):
        super(Style3dProductModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleInfo(self):
        return self._getViewModel(9)

    @staticmethod
    def getVehicleInfoType():
        return VehicleModel

    def getName(self):
        return self._getString(10)

    def setName(self, value):
        self._setString(10, value)

    def getCanGoToCustomization(self):
        return self._getBool(11)

    def setCanGoToCustomization(self, value):
        self._setBool(11, value)

    def _initialize(self):
        super(Style3dProductModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', VehicleModel())
        self._addStringProperty('name', '')
        self._addBoolProperty('canGoToCustomization', False)
