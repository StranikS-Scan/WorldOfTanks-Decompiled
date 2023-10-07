# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/tooltips/training_level_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel
from gui.impl.gen.view_models.views.lobby.crew.tooltips.training_level_modifiers_model import TrainingLevelModifiersModel

class TrainingLevelTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(TrainingLevelTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def currentVehicle(self):
        return self._getViewModel(0)

    @staticmethod
    def getCurrentVehicleType():
        return VehicleInfoModel

    @property
    def nativeVehicle(self):
        return self._getViewModel(1)

    @staticmethod
    def getNativeVehicleType():
        return VehicleInfoModel

    def getIsFemale(self):
        return self._getBool(2)

    def setIsFemale(self, value):
        self._setBool(2, value)

    def getNation(self):
        return self._getString(3)

    def setNation(self, value):
        self._setString(3, value)

    def getRoles(self):
        return self._getArray(4)

    def setRoles(self, value):
        self._setArray(4, value)

    @staticmethod
    def getRolesType():
        return unicode

    def getModifiers(self):
        return self._getArray(5)

    def setModifiers(self, value):
        self._setArray(5, value)

    @staticmethod
    def getModifiersType():
        return TrainingLevelModifiersModel

    def _initialize(self):
        super(TrainingLevelTooltipModel, self)._initialize()
        self._addViewModelProperty('currentVehicle', VehicleInfoModel())
        self._addViewModelProperty('nativeVehicle', VehicleInfoModel())
        self._addBoolProperty('isFemale', False)
        self._addStringProperty('nation', '')
        self._addArrayProperty('roles', Array())
        self._addArrayProperty('modifiers', Array())
