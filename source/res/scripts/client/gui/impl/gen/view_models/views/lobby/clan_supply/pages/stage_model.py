# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/clan_supply/pages/stage_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class StageStatus(IntEnum):
    AVAILABLE = 0
    DISABLED = 1
    OPENED = 2


class StageModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(StageModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getStatus(self):
        return StageStatus(self._getNumber(1))

    def setStatus(self, value):
        self._setNumber(1, value.value)

    def getIsPremium(self):
        return self._getBool(2)

    def setIsPremium(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(StageModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addNumberProperty('status')
        self._addBoolProperty('isPremium', False)
