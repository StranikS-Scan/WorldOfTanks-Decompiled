# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/subscription/wot_plus_tooltip_model.py
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


class WotPlusTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(WotPlusTooltipModel, self).__init__(properties=properties, commands=commands)

    def getNextCharge(self):
        return self._getString(0)

    def setNextCharge(self, value):
        self._setString(0, value)

    def getState(self):
        return SubscriptionState(self._getNumber(1))

    def setState(self, value):
        self._setNumber(1, value.value)

    def getBonuses(self):
        return self._getArray(2)

    def setBonuses(self, value):
        self._setArray(2, value)

    @staticmethod
    def getBonusesType():
        return BonusModel

    def _initialize(self):
        super(WotPlusTooltipModel, self)._initialize()
        self._addStringProperty('nextCharge', '')
        self._addNumberProperty('state')
        self._addArrayProperty('bonuses', Array())
