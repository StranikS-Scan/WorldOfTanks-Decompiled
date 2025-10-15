# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/seniority_awards/vehicle_selector_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.seniority_awards.vehicle_bonus_model import VehicleBonusModel

class VehicleSelectorModel(ViewModel):
    __slots__ = ('onClose', 'onApplySelect', 'onFilterReset', 'onSelectReward')

    def __init__(self, properties=6, commands=4):
        super(VehicleSelectorModel, self).__init__(properties=properties, commands=commands)

    def getIsError(self):
        return self._getBool(0)

    def setIsError(self, value):
        self._setBool(0, value)

    def getAvailableToSelectCount(self):
        return self._getNumber(1)

    def setAvailableToSelectCount(self, value):
        self._setNumber(1, value)

    def getSelectedRewardsCount(self):
        return self._getNumber(2)

    def setSelectedRewardsCount(self, value):
        self._setNumber(2, value)

    def getFinishSelectTimeStamp(self):
        return self._getNumber(3)

    def setFinishSelectTimeStamp(self, value):
        self._setNumber(3, value)

    def getAvailableVehiclesCount(self):
        return self._getNumber(4)

    def setAvailableVehiclesCount(self, value):
        self._setNumber(4, value)

    def getVehicles(self):
        return self._getArray(5)

    def setVehicles(self, value):
        self._setArray(5, value)

    @staticmethod
    def getVehiclesType():
        return VehicleBonusModel

    def _initialize(self):
        super(VehicleSelectorModel, self)._initialize()
        self._addBoolProperty('isError', False)
        self._addNumberProperty('availableToSelectCount', 0)
        self._addNumberProperty('selectedRewardsCount', 0)
        self._addNumberProperty('finishSelectTimeStamp', 0)
        self._addNumberProperty('availableVehiclesCount', 0)
        self._addArrayProperty('vehicles', Array())
        self.onClose = self._addCommand('onClose')
        self.onApplySelect = self._addCommand('onApplySelect')
        self.onFilterReset = self._addCommand('onFilterReset')
        self.onSelectReward = self._addCommand('onSelectReward')
