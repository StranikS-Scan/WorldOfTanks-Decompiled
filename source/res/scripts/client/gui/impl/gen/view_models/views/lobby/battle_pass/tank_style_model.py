# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/tank_style_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel

class TankStyleModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(TankStyleModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleInfo(self):
        return self._getViewModel(0)

    def getStyleId(self):
        return self._getNumber(1)

    def setStyleId(self, value):
        self._setNumber(1, value)

    def getStyleName(self):
        return self._getString(2)

    def setStyleName(self, value):
        self._setString(2, value)

    def getIsInHangar(self):
        return self._getBool(3)

    def setIsInHangar(self, value):
        self._setBool(3, value)

    def getIsObtained(self):
        return self._getBool(4)

    def setIsObtained(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(TankStyleModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', VehicleInfoModel())
        self._addNumberProperty('styleId', 0)
        self._addStringProperty('styleName', '')
        self._addBoolProperty('isInHangar', False)
        self._addBoolProperty('isObtained', False)
