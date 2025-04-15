# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/impl/gen/view_models/views/lobby/award_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel

class AwardViewModel(ViewModel):
    __slots__ = ('showInHangar', 'close')

    def __init__(self, properties=3, commands=2):
        super(AwardViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleInfoType():
        return VehicleInfoModel

    def getPersonalNumber(self):
        return self._getString(1)

    def setPersonalNumber(self, value):
        self._setString(1, value)

    def getRewardIndex(self):
        return self._getNumber(2)

    def setRewardIndex(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(AwardViewModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', VehicleInfoModel())
        self._addStringProperty('personalNumber', '')
        self._addNumberProperty('rewardIndex', 0)
        self.showInHangar = self._addCommand('showInHangar')
        self.close = self._addCommand('close')
