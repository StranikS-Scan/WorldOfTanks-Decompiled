# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/game_mode_cell_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel

class GameModeCellModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(GameModeCellModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleInfoType():
        return VehicleInfoModel

    def getText(self):
        return self._getString(1)

    def setText(self, value):
        self._setString(1, value)

    def getPoints(self):
        return self._getNumber(2)

    def setPoints(self, value):
        self._setNumber(2, value)

    def getExternalPoints(self):
        return self._getNumber(3)

    def setExternalPoints(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(GameModeCellModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', VehicleInfoModel())
        self._addStringProperty('text', '')
        self._addNumberProperty('points', 0)
        self._addNumberProperty('externalPoints', 0)
