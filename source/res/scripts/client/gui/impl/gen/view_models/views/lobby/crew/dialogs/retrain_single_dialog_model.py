# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/dialogs/retrain_single_dialog_model.py
from gui.impl.gen import R
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel
from gui.impl.gen.view_models.views.dialogs.dialog_template_view_model import DialogTemplateViewModel
from gui.impl.gen.view_models.views.lobby.crew.dialogs.dialog_tankman_model import DialogTankmanModel
from gui.impl.gen.view_models.views.lobby.crew.dialogs.role_change_model import RoleChangeModel

class RetrainSingleDialogModel(DialogTemplateViewModel):
    __slots__ = ('onRoleCheckChanged', 'onRoleSelected')

    def __init__(self, properties=13, commands=4):
        super(RetrainSingleDialogModel, self).__init__(properties=properties, commands=commands)

    @property
    def tankmanBefore(self):
        return self._getViewModel(6)

    @staticmethod
    def getTankmanBeforeType():
        return DialogTankmanModel

    @property
    def tankmanAfter(self):
        return self._getViewModel(7)

    @staticmethod
    def getTankmanAfterType():
        return DialogTankmanModel

    @property
    def targetVehicle(self):
        return self._getViewModel(8)

    @staticmethod
    def getTargetVehicleType():
        return VehicleInfoModel

    @property
    def roleChange(self):
        return self._getViewModel(9)

    @staticmethod
    def getRoleChangeType():
        return RoleChangeModel

    def getTitle(self):
        return self._getResource(10)

    def setTitle(self, value):
        self._setResource(10, value)

    def getWarning(self):
        return self._getResource(11)

    def setWarning(self, value):
        self._setResource(11, value)

    def getIsPriceSelected(self):
        return self._getBool(12)

    def setIsPriceSelected(self, value):
        self._setBool(12, value)

    def _initialize(self):
        super(RetrainSingleDialogModel, self)._initialize()
        self._addViewModelProperty('tankmanBefore', DialogTankmanModel())
        self._addViewModelProperty('tankmanAfter', DialogTankmanModel())
        self._addViewModelProperty('targetVehicle', VehicleInfoModel())
        self._addViewModelProperty('roleChange', RoleChangeModel())
        self._addResourceProperty('title', R.invalid())
        self._addResourceProperty('warning', R.invalid())
        self._addBoolProperty('isPriceSelected', False)
        self.onRoleCheckChanged = self._addCommand('onRoleCheckChanged')
        self.onRoleSelected = self._addCommand('onRoleSelected')
