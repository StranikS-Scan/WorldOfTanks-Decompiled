# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/summer_sale/summer_sale_rewards_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class SummerSaleRewardsViewModel(ViewModel):
    __slots__ = ('onClose', 'onShowVehicleInHangar')

    def __init__(self, properties=2, commands=2):
        super(SummerSaleRewardsViewModel, self).__init__(properties=properties, commands=commands)

    def getMainRewards(self):
        return self._getArray(0)

    def setMainRewards(self, value):
        self._setArray(0, value)

    @staticmethod
    def getMainRewardsType():
        return BonusModel

    def getRewards(self):
        return self._getArray(1)

    def setRewards(self, value):
        self._setArray(1, value)

    @staticmethod
    def getRewardsType():
        return BonusModel

    def _initialize(self):
        super(SummerSaleRewardsViewModel, self)._initialize()
        self._addArrayProperty('mainRewards', Array())
        self._addArrayProperty('rewards', Array())
        self.onClose = self._addCommand('onClose')
        self.onShowVehicleInHangar = self._addCommand('onShowVehicleInHangar')
