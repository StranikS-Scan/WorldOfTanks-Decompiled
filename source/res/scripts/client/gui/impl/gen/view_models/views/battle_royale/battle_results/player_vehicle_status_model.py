# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle_royale/battle_results/player_vehicle_status_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.user_name_model import UserNameModel

class PlayerVehicleStatusModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(PlayerVehicleStatusModel, self).__init__(properties=properties, commands=commands)

    @property
    def user(self):
        return self._getViewModel(0)

    @property
    def killer(self):
        return self._getViewModel(1)

    def getReason(self):
        return self._getResource(2)

    def setReason(self, value):
        self._setResource(2, value)

    def _initialize(self):
        super(PlayerVehicleStatusModel, self)._initialize()
        self._addViewModelProperty('user', UserNameModel())
        self._addViewModelProperty('killer', UserNameModel())
        self._addResourceProperty('reason', R.invalid())
