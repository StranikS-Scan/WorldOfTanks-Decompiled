# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/new_year/components/ny_reward_renderer/ny_secondary_reward_renderer_model.py
from gui.impl.gen.view_models.ui_kit.reward_renderer_model import RewardRendererModel

class NySecondaryRewardRendererModel(RewardRendererModel):
    __slots__ = ()

    def getIdx(self):
        return self._getNumber(8)

    def setIdx(self, value):
        self._setNumber(8, value)

    def _initialize(self):
        super(NySecondaryRewardRendererModel, self)._initialize()
        self._addNumberProperty('idx', 0)
