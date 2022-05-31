# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/dragon_boat/rewards_screen_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel

class RewardsScreenModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=3, commands=1):
        super(RewardsScreenModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleInfo(self):
        return self._getViewModel(0)

    def getMainRewards(self):
        return self._getArray(1)

    def setMainRewards(self, value):
        self._setArray(1, value)

    def getAdditionalRewards(self):
        return self._getArray(2)

    def setAdditionalRewards(self, value):
        self._setArray(2, value)

    def _initialize(self):
        super(RewardsScreenModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', VehicleInfoModel())
        self._addArrayProperty('mainRewards', Array())
        self._addArrayProperty('additionalRewards', Array())
        self.onClose = self._addCommand('onClose')
