# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/new_year/components/ny_reward_renderer/ny_tankwoman_reward_renderer_model.py
from frameworks.wulf import Resource
from gui.impl.gen.view_models.new_year.components.ny_reward_renderer.ny_main_reward_renderer_model import NyMainRewardRendererModel

class NyTankwomanRewardRendererModel(NyMainRewardRendererModel):
    __slots__ = ()

    def getRewardImage(self):
        return self._getResource(1)

    def setRewardImage(self, value):
        self._setResource(1, value)

    def _initialize(self):
        super(NyTankwomanRewardRendererModel, self)._initialize()
        self._addResourceProperty('rewardImage', Resource.INVALID)
