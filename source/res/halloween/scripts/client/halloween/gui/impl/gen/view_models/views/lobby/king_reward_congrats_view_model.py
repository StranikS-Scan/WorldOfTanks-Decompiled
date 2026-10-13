# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/king_reward_congrats_view_model.py
from frameworks.wulf import Array, ViewModel
from halloween.gui.impl.gen.view_models.views.common.bonus_item_view_model import BonusItemViewModel
from halloween.gui.impl.gen.view_models.views.lobby.vehicle_title_view_model import VehicleTitleViewModel

class KingRewardCongratsViewModel(ViewModel):
    __slots__ = ('onClose', 'onToGarageClick', 'onToOutroClick')

    def __init__(self, properties=2, commands=3):
        super(KingRewardCongratsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def mainGiftVehicle(self):
        return self._getViewModel(0)

    @staticmethod
    def getMainGiftVehicleType():
        return VehicleTitleViewModel

    def getRewards(self):
        return self._getArray(1)

    def setRewards(self, value):
        self._setArray(1, value)

    @staticmethod
    def getRewardsType():
        return BonusItemViewModel

    def _initialize(self):
        super(KingRewardCongratsViewModel, self)._initialize()
        self._addViewModelProperty('mainGiftVehicle', VehicleTitleViewModel())
        self._addArrayProperty('rewards', Array())
        self.onClose = self._addCommand('onClose')
        self.onToGarageClick = self._addCommand('onToGarageClick')
        self.onToOutroClick = self._addCommand('onToOutroClick')
