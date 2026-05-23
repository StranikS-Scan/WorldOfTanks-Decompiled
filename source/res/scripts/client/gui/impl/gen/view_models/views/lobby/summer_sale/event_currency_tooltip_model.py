# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/summer_sale/event_currency_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class EventCurrencyTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(EventCurrencyTooltipModel, self).__init__(properties=properties, commands=commands)

    def getRewardsGroup(self):
        return self._getString(0)

    def setRewardsGroup(self, value):
        self._setString(0, value)

    def getRewards(self):
        return self._getArray(1)

    def setRewards(self, value):
        self._setArray(1, value)

    @staticmethod
    def getRewardsType():
        return BonusModel

    def _initialize(self):
        super(EventCurrencyTooltipModel, self)._initialize()
        self._addStringProperty('rewardsGroup', '')
        self._addArrayProperty('rewards', Array())
