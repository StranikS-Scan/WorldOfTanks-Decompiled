# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle_royale/BR_reward_renderer_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class BRRewardRendererModel(ViewModel):
    __slots__ = ()

    def getImage(self):
        return self._getResource(0)

    def setImage(self, value):
        self._setResource(0, value)

    def getRewardValue(self):
        return self._getNumber(1)

    def setRewardValue(self, value):
        self._setNumber(1, value)

    def getId(self):
        return self._getNumber(2)

    def setId(self, value):
        self._setNumber(2, value)

    def getTooltip(self):
        return self._getString(3)

    def setTooltip(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(BRRewardRendererModel, self)._initialize()
        self._addResourceProperty('image', R.invalid())
        self._addNumberProperty('rewardValue', 0)
        self._addNumberProperty('id', -1)
        self._addStringProperty('tooltip', '')
