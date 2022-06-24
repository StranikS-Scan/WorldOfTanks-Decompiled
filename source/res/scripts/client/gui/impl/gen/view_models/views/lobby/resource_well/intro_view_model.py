# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/resource_well/intro_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel

class IntroViewModel(ViewModel):
    __slots__ = ('showVideo', 'onClose')

    def __init__(self, properties=3, commands=2):
        super(IntroViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleInfo(self):
        return self._getViewModel(0)

    def getTopRewardPlayersCount(self):
        return self._getNumber(1)

    def setTopRewardPlayersCount(self, value):
        self._setNumber(1, value)

    def getRegularRewardVehiclesCount(self):
        return self._getNumber(2)

    def setRegularRewardVehiclesCount(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(IntroViewModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', VehicleInfoModel())
        self._addNumberProperty('topRewardPlayersCount', 0)
        self._addNumberProperty('regularRewardVehiclesCount', 0)
        self.showVideo = self._addCommand('showVideo')
        self.onClose = self._addCommand('onClose')
