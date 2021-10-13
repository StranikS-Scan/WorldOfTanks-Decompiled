# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/yha/yha_awards_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.yha.reward_model import RewardModel

class YhaAwardsViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(YhaAwardsViewModel, self).__init__(properties=properties, commands=commands)

    def getRewards(self):
        return self._getArray(0)

    def setRewards(self, value):
        self._setArray(0, value)

    def _initialize(self):
        super(YhaAwardsViewModel, self)._initialize()
        self._addArrayProperty('rewards', Array())
