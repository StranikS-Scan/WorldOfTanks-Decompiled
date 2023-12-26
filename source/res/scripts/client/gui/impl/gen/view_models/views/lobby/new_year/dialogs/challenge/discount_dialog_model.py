# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/dialogs/challenge/discount_dialog_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel

class DiscountDialogModel(ViewModel):
    __slots__ = ('onAccept', 'onCancel')

    def __init__(self, properties=2, commands=2):
        super(DiscountDialogModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleInfoType():
        return VehicleInfoModel

    def getDiscountInPercent(self):
        return self._getNumber(1)

    def setDiscountInPercent(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(DiscountDialogModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', VehicleInfoModel())
        self._addNumberProperty('discountInPercent', 0)
        self.onAccept = self._addCommand('onAccept')
        self.onCancel = self._addCommand('onCancel')
