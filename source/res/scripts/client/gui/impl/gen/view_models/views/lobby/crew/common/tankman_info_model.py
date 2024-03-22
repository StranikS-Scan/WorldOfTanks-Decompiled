# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/common/tankman_info_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel

class TankmanInfoModel(ViewModel):
    __slots__ = ('onPlayUniqueVoice', 'onChangeVehicle', 'onRetrain')

    def __init__(self, properties=13, commands=3):
        super(TankmanInfoModel, self).__init__(properties=properties, commands=commands)

    @property
    def nativeVehicle(self):
        return self._getViewModel(0)

    @staticmethod
    def getNativeVehicleType():
        return VehicleModel

    @property
    def currentVehicle(self):
        return self._getViewModel(1)

    @staticmethod
    def getCurrentVehicleType():
        return VehicleModel

    def getInvId(self):
        return self._getNumber(2)

    def setInvId(self, value):
        self._setNumber(2, value)

    def getIconName(self):
        return self._getString(3)

    def setIconName(self, value):
        self._setString(3, value)

    def getFullName(self):
        return self._getString(4)

    def setFullName(self, value):
        self._setString(4, value)

    def getDescription(self):
        return self._getString(5)

    def setDescription(self, value):
        self._setString(5, value)

    def getRole(self):
        return self._getString(6)

    def setRole(self, value):
        self._setString(6, value)

    def getSkillsEfficiency(self):
        return self._getReal(7)

    def setSkillsEfficiency(self, value):
        self._setReal(7, value)

    def getHasRetrainDiscount(self):
        return self._getBool(8)

    def setHasRetrainDiscount(self, value):
        self._setBool(8, value)

    def getIsInSkin(self):
        return self._getBool(9)

    def setIsInSkin(self, value):
        self._setBool(9, value)

    def getIsFemale(self):
        return self._getBool(10)

    def setIsFemale(self, value):
        self._setBool(10, value)

    def getIsCrewLocked(self):
        return self._getBool(11)

    def setIsCrewLocked(self, value):
        self._setBool(11, value)

    def getHasUniqueSound(self):
        return self._getBool(12)

    def setHasUniqueSound(self, value):
        self._setBool(12, value)

    def _initialize(self):
        super(TankmanInfoModel, self)._initialize()
        self._addViewModelProperty('nativeVehicle', VehicleModel())
        self._addViewModelProperty('currentVehicle', VehicleModel())
        self._addNumberProperty('invId', 0)
        self._addStringProperty('iconName', '')
        self._addStringProperty('fullName', '')
        self._addStringProperty('description', '')
        self._addStringProperty('role', '')
        self._addRealProperty('skillsEfficiency', 0.0)
        self._addBoolProperty('hasRetrainDiscount', False)
        self._addBoolProperty('isInSkin', False)
        self._addBoolProperty('isFemale', False)
        self._addBoolProperty('isCrewLocked', False)
        self._addBoolProperty('hasUniqueSound', False)
        self.onPlayUniqueVoice = self._addCommand('onPlayUniqueVoice')
        self.onChangeVehicle = self._addCommand('onChangeVehicle')
        self.onRetrain = self._addCommand('onRetrain')
