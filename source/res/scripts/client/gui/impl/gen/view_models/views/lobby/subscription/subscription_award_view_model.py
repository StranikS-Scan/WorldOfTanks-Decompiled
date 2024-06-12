# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/subscription/subscription_award_view_model.py
from enum import IntEnum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class SubscriptionState(IntEnum):
    INACTIVE = 0
    ACTIVE = 1
    CANCELED = 2
    ERROR = 3
    TRIAL = 4


class SubscriptionAwardViewModel(ViewModel):
    __slots__ = ('onCloseButtonClick', 'onInfoButtonClick')

    def __init__(self, properties=3, commands=2):
        super(SubscriptionAwardViewModel, self).__init__(properties=properties, commands=commands)

    def getNextCharge(self):
        return self._getNumber(0)

    def setNextCharge(self, value):
        self._setNumber(0, value)

    def getState(self):
        return SubscriptionState(self._getNumber(1))

    def setState(self, value):
        self._setNumber(1, value.value)

    def getRewards(self):
        return self._getArray(2)

    def setRewards(self, value):
        self._setArray(2, value)

    @staticmethod
    def getRewardsType():
        return BonusModel

    def _initialize(self):
        super(SubscriptionAwardViewModel, self)._initialize()
        self._addNumberProperty('nextCharge', 0)
        self._addNumberProperty('state')
        self._addArrayProperty('rewards', Array())
        self.onCloseButtonClick = self._addCommand('onCloseButtonClick')
        self.onInfoButtonClick = self._addCommand('onInfoButtonClick')
