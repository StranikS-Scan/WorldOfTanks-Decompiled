# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/battle_mode_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.common.hb_coin_model import HbCoinModel

class FrontStateType(Enum):
    SOON = 'soon'
    AVAILABLE = 'available'
    HIGHLIGHTED = 'highlighted'
    COUNTDOWN = 'countdown'


class BattleModeModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(BattleModeModel, self).__init__(properties=properties, commands=commands)

    @property
    def earnings(self):
        return self._getViewModel(0)

    @staticmethod
    def getEarningsType():
        return HbCoinModel

    def getFrontName(self):
        return self._getString(1)

    def setFrontName(self, value):
        self._setString(1, value)

    def getCountDownSeconds(self):
        return self._getNumber(2)

    def setCountDownSeconds(self, value):
        self._setNumber(2, value)

    def getFrontState(self):
        return FrontStateType(self._getString(3))

    def setFrontState(self, value):
        self._setString(3, value.value)

    def _initialize(self):
        super(BattleModeModel, self)._initialize()
        self._addViewModelProperty('earnings', HbCoinModel())
        self._addStringProperty('frontName', '')
        self._addNumberProperty('countDownSeconds', 0)
        self._addStringProperty('frontState')
