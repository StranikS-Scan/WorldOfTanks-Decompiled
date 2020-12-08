# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/ny_reward_renderer/ny_main_reward_renderer_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class NyMainRewardRendererModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(NyMainRewardRendererModel, self).__init__(properties=properties, commands=commands)

    def getIsApplied(self):
        return self._getBool(0)

    def setIsApplied(self, value):
        self._setBool(0, value)

    def getRewardImage(self):
        return self._getResource(1)

    def setRewardImage(self, value):
        self._setResource(1, value)

    def _initialize(self):
        super(NyMainRewardRendererModel, self)._initialize()
        self._addBoolProperty('isApplied', False)
        self._addResourceProperty('rewardImage', R.invalid())
