# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wot_anniversary/intro_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel

class IntroViewModel(ViewModel):
    __slots__ = ('onClose', 'onAccept')

    def __init__(self, properties=3, commands=2):
        super(IntroViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicle(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleType():
        return VehicleInfoModel

    def getStartTime(self):
        return self._getNumber(1)

    def setStartTime(self, value):
        self._setNumber(1, value)

    def getEndTime(self):
        return self._getNumber(2)

    def setEndTime(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(IntroViewModel, self)._initialize()
        self._addViewModelProperty('vehicle', VehicleInfoModel())
        self._addNumberProperty('startTime', 0)
        self._addNumberProperty('endTime', 0)
        self.onClose = self._addCommand('onClose')
        self.onAccept = self._addCommand('onAccept')
