# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/dialogs/role_change_dialog_model.py
from gui.impl.gen.view_models.views.dialogs.dialog_template_view_model import DialogTemplateViewModel
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel

class RoleChangeDialogModel(DialogTemplateViewModel):
    __slots__ = ()

    def __init__(self, properties=15, commands=2):
        super(RoleChangeDialogModel, self).__init__(properties=properties, commands=commands)

    @property
    def currentVehicle(self):
        return self._getViewModel(6)

    @staticmethod
    def getCurrentVehicleType():
        return VehicleModel

    @property
    def newVehicle(self):
        return self._getViewModel(7)

    @staticmethod
    def getNewVehicleType():
        return VehicleModel

    @property
    def currentSpecializationVehicle(self):
        return self._getViewModel(8)

    @staticmethod
    def getCurrentSpecializationVehicleType():
        return VehicleModel

    def getIconName(self):
        return self._getString(9)

    def setIconName(self, value):
        self._setString(9, value)

    def getCurrentRole(self):
        return self._getString(10)

    def setCurrentRole(self, value):
        self._setString(10, value)

    def getNewRole(self):
        return self._getString(11)

    def setNewRole(self, value):
        self._setString(11, value)

    def getIsSkin(self):
        return self._getBool(12)

    def setIsSkin(self, value):
        self._setBool(12, value)

    def getIsTankChange(self):
        return self._getBool(13)

    def setIsTankChange(self, value):
        self._setBool(13, value)

    def getIsSpecializationChange(self):
        return self._getBool(14)

    def setIsSpecializationChange(self, value):
        self._setBool(14, value)

    def _initialize(self):
        super(RoleChangeDialogModel, self)._initialize()
        self._addViewModelProperty('currentVehicle', VehicleModel())
        self._addViewModelProperty('newVehicle', VehicleModel())
        self._addViewModelProperty('currentSpecializationVehicle', VehicleModel())
        self._addStringProperty('iconName', '')
        self._addStringProperty('currentRole', '')
        self._addStringProperty('newRole', '')
        self._addBoolProperty('isSkin', False)
        self._addBoolProperty('isTankChange', False)
        self._addBoolProperty('isSpecializationChange', False)
