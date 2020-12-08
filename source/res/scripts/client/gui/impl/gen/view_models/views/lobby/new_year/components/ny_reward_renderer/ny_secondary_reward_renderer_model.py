# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/ny_reward_renderer/ny_secondary_reward_renderer_model.py
from gui.impl.gen.view_models.ui_kit.reward_renderer_model import RewardRendererModel

class NySecondaryRewardRendererModel(RewardRendererModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
        super(NySecondaryRewardRendererModel, self).__init__(properties=properties, commands=commands)

    def getIdx(self):
        return self._getNumber(8)

    def setIdx(self, value):
        self._setNumber(8, value)

    def getIsHidden(self):
        return self._getBool(9)

    def setIsHidden(self, value):
        self._setBool(9, value)

    def getIsFragments(self):
        return self._getBool(10)

    def setIsFragments(self, value):
        self._setBool(10, value)

    def _initialize(self):
        super(NySecondaryRewardRendererModel, self)._initialize()
        self._addNumberProperty('idx', 0)
        self._addBoolProperty('isHidden', False)
        self._addBoolProperty('isFragments', False)
