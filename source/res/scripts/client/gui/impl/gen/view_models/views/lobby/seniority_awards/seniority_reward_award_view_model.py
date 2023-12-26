# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/seniority_awards/seniority_reward_award_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class ShopOnOpenState(Enum):
    AVAILABLE = 'available'
    NOT_AVAILABLE = 'notAvailable'
    DISABLED = 'disabled'


class SeniorityRewardAwardViewModel(ViewModel):
    __slots__ = ('onOpenBtnClick', 'onShopBtnClick')

    def __init__(self, properties=4, commands=2):
        super(SeniorityRewardAwardViewModel, self).__init__(properties=properties, commands=commands)

    def getCategory(self):
        return self._getString(0)

    def setCategory(self, value):
        self._setString(0, value)

    def getBonuses(self):
        return self._getArray(1)

    def setBonuses(self, value):
        self._setArray(1, value)

    @staticmethod
    def getBonusesType():
        return BonusModel

    def getSpecialCurrencyCount(self):
        return self._getNumber(2)

    def setSpecialCurrencyCount(self, value):
        self._setNumber(2, value)

    def getShopOnOpenState(self):
        return ShopOnOpenState(self._getString(3))

    def setShopOnOpenState(self, value):
        self._setString(3, value.value)

    def _initialize(self):
        super(SeniorityRewardAwardViewModel, self)._initialize()
        self._addStringProperty('category', '')
        self._addArrayProperty('bonuses', Array())
        self._addNumberProperty('specialCurrencyCount', -1)
        self._addStringProperty('shopOnOpenState', ShopOnOpenState.NOT_AVAILABLE.value)
        self.onOpenBtnClick = self._addCommand('onOpenBtnClick')
        self.onShopBtnClick = self._addCommand('onShopBtnClick')
