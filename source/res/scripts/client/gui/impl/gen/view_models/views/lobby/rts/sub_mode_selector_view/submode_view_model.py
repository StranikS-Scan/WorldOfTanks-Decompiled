# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/rts/sub_mode_selector_view/submode_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.rts.rts_currency_view_model import RtsCurrencyViewModel

class SubModesEnum(Enum):
    STRATEGIST1X1 = 'rts1x1'
    STRATEGIST1X7 = 'rts1x7'
    TANKER = 'rtsTanker'


class SubModeStateEnum(Enum):
    LOCKED = 'locked'
    FREE = 'free'
    NORMAL = 'normal'
    UNAVAILABLE = 'unavailable'


class SubmodeViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(SubmodeViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def currency(self):
        return self._getViewModel(0)

    def getSubMode(self):
        return SubModesEnum(self._getString(1))

    def setSubMode(self, value):
        self._setString(1, value.value)

    def getState(self):
        return SubModeStateEnum(self._getString(2))

    def setState(self, value):
        self._setString(2, value.value)

    def getDate(self):
        return self._getNumber(3)

    def setDate(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(SubmodeViewModel, self)._initialize()
        self._addViewModelProperty('currency', RtsCurrencyViewModel())
        self._addStringProperty('subMode')
        self._addStringProperty('state')
        self._addNumberProperty('date', 0)
