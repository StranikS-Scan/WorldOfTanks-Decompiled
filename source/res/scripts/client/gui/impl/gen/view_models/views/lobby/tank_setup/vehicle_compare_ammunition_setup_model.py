# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/vehicle_compare_ammunition_setup_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel
from gui.impl.gen.view_models.views.lobby.tank_setup.main_tank_setup_model import MainTankSetupModel

class VehicleCompareAmmunitionSetupModel(ViewModel):
    __slots__ = ('onClose', 'onResized', 'onViewRendered', 'onAnimationEnd')

    def __init__(self, properties=4, commands=4):
        super(VehicleCompareAmmunitionSetupModel, self).__init__(properties=properties, commands=commands)

    @property
    def tankSetup(self):
        return self._getViewModel(0)

    @property
    def vehicleInfo(self):
        return self._getViewModel(1)

    def getShow(self):
        return self._getBool(2)

    def setShow(self, value):
        self._setBool(2, value)

    def getSelectedSlot(self):
        return self._getNumber(3)

    def setSelectedSlot(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(VehicleCompareAmmunitionSetupModel, self)._initialize()
        self._addViewModelProperty('tankSetup', MainTankSetupModel())
        self._addViewModelProperty('vehicleInfo', VehicleInfoModel())
        self._addBoolProperty('show', False)
        self._addNumberProperty('selectedSlot', -1)
        self.onClose = self._addCommand('onClose')
        self.onResized = self._addCommand('onResized')
        self.onViewRendered = self._addCommand('onViewRendered')
        self.onAnimationEnd = self._addCommand('onAnimationEnd')
