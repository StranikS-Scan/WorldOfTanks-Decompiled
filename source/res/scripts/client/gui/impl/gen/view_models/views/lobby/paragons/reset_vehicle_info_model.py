# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/paragons/reset_vehicle_info_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel
from gui.impl.gen.view_models.views.lobby.paragons.returned_items_model import ReturnedItemsModel

class ResetVehicleInfoModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(ResetVehicleInfoModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleInfoType():
        return VehicleModel

    def getProgressPoints(self):
        return self._getNumber(1)

    def setProgressPoints(self, value):
        self._setNumber(1, value)

    def getBlueprintFragments(self):
        return self._getNumber(2)

    def setBlueprintFragments(self, value):
        self._setNumber(2, value)

    def getCredits(self):
        return self._getNumber(3)

    def setCredits(self, value):
        self._setNumber(3, value)

    def getReturnedItems(self):
        return self._getArray(4)

    def setReturnedItems(self, value):
        self._setArray(4, value)

    @staticmethod
    def getReturnedItemsType():
        return ReturnedItemsModel

    def _initialize(self):
        super(ResetVehicleInfoModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', VehicleModel())
        self._addNumberProperty('progressPoints', 0)
        self._addNumberProperty('blueprintFragments', 0)
        self._addNumberProperty('credits', 0)
        self._addArrayProperty('returnedItems', Array())
