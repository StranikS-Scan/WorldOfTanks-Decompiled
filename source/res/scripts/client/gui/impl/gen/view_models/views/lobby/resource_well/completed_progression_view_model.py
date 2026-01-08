# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/resource_well/completed_progression_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel

class CompletedProgressionViewModel(ViewModel):
    __slots__ = ('onViewLoaded', 'onClose', 'onShowVehicle', 'onAboutClick')

    def __init__(self, properties=5, commands=4):
        super(CompletedProgressionViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleInfoType():
        return VehicleInfoModel

    def getIsTop(self):
        return self._getBool(1)

    def setIsTop(self, value):
        self._setBool(1, value)

    def getPersonalNumber(self):
        return self._getString(2)

    def setPersonalNumber(self, value):
        self._setString(2, value)

    def getVehicleRole(self):
        return self._getString(3)

    def setVehicleRole(self, value):
        self._setString(3, value)

    def getVehicleFullDescription(self):
        return self._getString(4)

    def setVehicleFullDescription(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(CompletedProgressionViewModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', VehicleInfoModel())
        self._addBoolProperty('isTop', False)
        self._addStringProperty('personalNumber', '')
        self._addStringProperty('vehicleRole', '')
        self._addStringProperty('vehicleFullDescription', '')
        self.onViewLoaded = self._addCommand('onViewLoaded')
        self.onClose = self._addCommand('onClose')
        self.onShowVehicle = self._addCommand('onShowVehicle')
        self.onAboutClick = self._addCommand('onAboutClick')
