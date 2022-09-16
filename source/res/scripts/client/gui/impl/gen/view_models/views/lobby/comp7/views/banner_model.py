# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/views/banner_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class State(IntEnum):
    NOTSTARTED = 0
    JUSTSTARTED = 1
    ACTIVE = 2
    ENDSOON = 3
    END = 4
    DISABLED = 5


class BannerModel(ViewModel):
    __slots__ = ('onOpen',)

    def __init__(self, properties=3, commands=1):
        super(BannerModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return State(self._getNumber(0))

    def setState(self, value):
        self._setNumber(0, value.value)

    def getTimestamp(self):
        return self._getNumber(1)

    def setTimestamp(self, value):
        self._setNumber(1, value)

    def getIsSingle(self):
        return self._getBool(2)

    def setIsSingle(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(BannerModel, self)._initialize()
        self._addNumberProperty('state')
        self._addNumberProperty('timestamp', 0)
        self._addBoolProperty('isSingle', True)
        self.onOpen = self._addCommand('onOpen')
