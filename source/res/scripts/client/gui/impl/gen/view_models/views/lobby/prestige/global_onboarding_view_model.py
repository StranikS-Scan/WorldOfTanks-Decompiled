# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/prestige/global_onboarding_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.prestige.prestige_vehicle_model import PrestigeVehicleModel

class GlobalOnboardingViewModel(ViewModel):
    __slots__ = ('onClose', 'onGoToVehicleStatistic')

    def __init__(self, properties=2, commands=2):
        super(GlobalOnboardingViewModel, self).__init__(properties=properties, commands=commands)

    def getEliteVehicleAmount(self):
        return self._getNumber(0)

    def setEliteVehicleAmount(self, value):
        self._setNumber(0, value)

    def getVehicles(self):
        return self._getArray(1)

    def setVehicles(self, value):
        self._setArray(1, value)

    @staticmethod
    def getVehiclesType():
        return PrestigeVehicleModel

    def _initialize(self):
        super(GlobalOnboardingViewModel, self)._initialize()
        self._addNumberProperty('eliteVehicleAmount', 0)
        self._addArrayProperty('vehicles', Array())
        self.onClose = self._addCommand('onClose')
        self.onGoToVehicleStatistic = self._addCommand('onGoToVehicleStatistic')
