# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/dialogs/recruit_window/recruit_content_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.crew.dialogs.recruit_window.drop_down_item_view_model import DropDownItemViewModel
from gui.impl.gen.view_models.views.lobby.crew.dialogs.recruit_window.vehicle_item_view_model import VehicleItemViewModel

class DropDownState(Enum):
    NORMAL = 'normal'
    DISABLED = 'disabled'
    LOCKED = 'locked'


class RecruitContentViewModel(ViewModel):
    __slots__ = ('onNationChange', 'onVehTypeChange', 'onVehicleChange', 'onSpecializationChange')

    def __init__(self, properties=12, commands=4):
        super(RecruitContentViewModel, self).__init__(properties=properties, commands=commands)

    def getNationState(self):
        return DropDownState(self._getString(0))

    def setNationState(self, value):
        self._setString(0, value.value)

    def getVehTypeState(self):
        return DropDownState(self._getString(1))

    def setVehTypeState(self, value):
        self._setString(1, value.value)

    def getVehicleState(self):
        return DropDownState(self._getString(2))

    def setVehicleState(self, value):
        self._setString(2, value.value)

    def getSpecializationState(self):
        return DropDownState(self._getString(3))

    def setSpecializationState(self, value):
        self._setString(3, value.value)

    def getSelectedNation(self):
        return self._getString(4)

    def setSelectedNation(self, value):
        self._setString(4, value)

    def getNations(self):
        return self._getArray(5)

    def setNations(self, value):
        self._setArray(5, value)

    @staticmethod
    def getNationsType():
        return DropDownItemViewModel

    def getSelectedVehType(self):
        return self._getString(6)

    def setSelectedVehType(self, value):
        self._setString(6, value)

    def getVehTypes(self):
        return self._getArray(7)

    def setVehTypes(self, value):
        self._setArray(7, value)

    @staticmethod
    def getVehTypesType():
        return DropDownItemViewModel

    def getSelectedVehicle(self):
        return self._getString(8)

    def setSelectedVehicle(self, value):
        self._setString(8, value)

    def getVehicles(self):
        return self._getArray(9)

    def setVehicles(self, value):
        self._setArray(9, value)

    @staticmethod
    def getVehiclesType():
        return VehicleItemViewModel

    def getSelectedSpecialization(self):
        return self._getString(10)

    def setSelectedSpecialization(self, value):
        self._setString(10, value)

    def getSpecializations(self):
        return self._getArray(11)

    def setSpecializations(self, value):
        self._setArray(11, value)

    @staticmethod
    def getSpecializationsType():
        return DropDownItemViewModel

    def _initialize(self):
        super(RecruitContentViewModel, self)._initialize()
        self._addStringProperty('nationState')
        self._addStringProperty('vehTypeState')
        self._addStringProperty('vehicleState')
        self._addStringProperty('specializationState')
        self._addStringProperty('selectedNation', '-1')
        self._addArrayProperty('nations', Array())
        self._addStringProperty('selectedVehType', '-1')
        self._addArrayProperty('vehTypes', Array())
        self._addStringProperty('selectedVehicle', '-1')
        self._addArrayProperty('vehicles', Array())
        self._addStringProperty('selectedSpecialization', '-1')
        self._addArrayProperty('specializations', Array())
        self.onNationChange = self._addCommand('onNationChange')
        self.onVehTypeChange = self._addCommand('onVehTypeChange')
        self.onVehicleChange = self._addCommand('onVehicleChange')
        self.onSpecializationChange = self._addCommand('onSpecializationChange')
