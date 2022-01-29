# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lunar_ny/progression_level_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.lunar_ny.reward_view_model import RewardViewModel

class ProgressionLevelModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(ProgressionLevelModel, self).__init__(properties=properties, commands=commands)

    def getLevel(self):
        return self._getNumber(0)

    def setLevel(self, value):
        self._setNumber(0, value)

    def getMinEnvelopes(self):
        return self._getNumber(1)

    def setMinEnvelopes(self, value):
        self._setNumber(1, value)

    def getMaxEnvelopes(self):
        return self._getNumber(2)

    def setMaxEnvelopes(self, value):
        self._setNumber(2, value)

    def getRewards(self):
        return self._getArray(3)

    def setRewards(self, value):
        self._setArray(3, value)

    def _initialize(self):
        super(ProgressionLevelModel, self)._initialize()
        self._addNumberProperty('level', 0)
        self._addNumberProperty('minEnvelopes', 0)
        self._addNumberProperty('maxEnvelopes', 0)
        self._addArrayProperty('rewards', Array())
