# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/dialogs/retrain_massive_dialog_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel
from gui.impl.gen.view_models.views.dialogs.dialog_template_view_model import DialogTemplateViewModel
from gui.impl.gen.view_models.views.lobby.crew.dialogs.dialog_tankman_model import DialogTankmanModel

class RetrainMassiveDialogModel(DialogTemplateViewModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=2):
        super(RetrainMassiveDialogModel, self).__init__(properties=properties, commands=commands)

    @property
    def targetVehicle(self):
        return self._getViewModel(6)

    @staticmethod
    def getTargetVehicleType():
        return VehicleInfoModel

    def getIsPriceSelected(self):
        return self._getBool(7)

    def setIsPriceSelected(self, value):
        self._setBool(7, value)

    def getIsPriceVisible(self):
        return self._getBool(8)

    def setIsPriceVisible(self, value):
        self._setBool(8, value)

    def getTankmen(self):
        return self._getArray(9)

    def setTankmen(self, value):
        self._setArray(9, value)

    @staticmethod
    def getTankmenType():
        return DialogTankmanModel

    def _initialize(self):
        super(RetrainMassiveDialogModel, self)._initialize()
        self._addViewModelProperty('targetVehicle', VehicleInfoModel())
        self._addBoolProperty('isPriceSelected', False)
        self._addBoolProperty('isPriceVisible', False)
        self._addArrayProperty('tankmen', Array())
