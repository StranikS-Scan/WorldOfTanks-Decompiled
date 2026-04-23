# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/front_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class FrontStateType(Enum):
    SOON = 'soon'
    AVAILABLE = 'available'
    COUNTDOWN = 'countdown'


class FrontModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(FrontModel, self).__init__(properties=properties, commands=commands)

    def getFrontName(self):
        return self._getString(0)

    def setFrontName(self, value):
        self._setString(0, value)

    def getCountDownSeconds(self):
        return self._getNumber(1)

    def setCountDownSeconds(self, value):
        self._setNumber(1, value)

    def getFrontState(self):
        return FrontStateType(self._getString(2))

    def setFrontState(self, value):
        self._setString(2, value.value)

    def _initialize(self):
        super(FrontModel, self)._initialize()
        self._addStringProperty('frontName', '')
        self._addNumberProperty('countDownSeconds', 0)
        self._addStringProperty('frontState')
