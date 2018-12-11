# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/new_year/components/ny_reward_renderer/ny_main_reward_renderer_model.py
from frameworks.wulf import ViewModel

class NyMainRewardRendererModel(ViewModel):
    __slots__ = ()

    def getIsApplied(self):
        return self._getBool(0)

    def setIsApplied(self, value):
        self._setBool(0, value)

    def _initialize(self):
        super(NyMainRewardRendererModel, self)._initialize()
        self._addBoolProperty('isApplied', False)
