# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/prestige/views/prestige_reward_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.prestige.prestige_vehicle_model import PrestigeVehicleModel

class PrestigeRewardViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=1, commands=1):
        super(PrestigeRewardViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicle(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleType():
        return PrestigeVehicleModel

    def _initialize(self):
        super(PrestigeRewardViewModel, self)._initialize()
        self._addViewModelProperty('vehicle', PrestigeVehicleModel())
        self.onClose = self._addCommand('onClose')
