# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/dialogs/retrain_premium_vehicle_dialog_model.py
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel
from gui.impl.gen.view_models.views.dialogs.dialog_template_view_model import DialogTemplateViewModel

class RetrainPremiumVehicleDialogModel(DialogTemplateViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=2):
        super(RetrainPremiumVehicleDialogModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicle(self):
        return self._getViewModel(6)

    @staticmethod
    def getVehicleType():
        return VehicleInfoModel

    def getIsMassRetrain(self):
        return self._getBool(7)

    def setIsMassRetrain(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(RetrainPremiumVehicleDialogModel, self)._initialize()
        self._addViewModelProperty('vehicle', VehicleInfoModel())
        self._addBoolProperty('isMassRetrain', False)
