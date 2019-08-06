# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/ui_kit/reward_renderer_model.py
from gui.impl.gen.view_models.ui_kit.base_reward_renderer_model import BaseRewardRendererModel

class RewardRendererModel(BaseRewardRendererModel):
    __slots__ = ()

    def getIcon(self):
        return self._getString(7)

    def setIcon(self, value):
        self._setString(7, value)

    def _initialize(self):
        super(RewardRendererModel, self)._initialize()
        self._addStringProperty('icon', '')
