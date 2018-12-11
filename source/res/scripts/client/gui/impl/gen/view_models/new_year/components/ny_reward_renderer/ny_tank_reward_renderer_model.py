# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/new_year/components/ny_reward_renderer/ny_tank_reward_renderer_model.py
from frameworks.wulf import Resource
from gui.impl.gen.view_models.new_year.components.ny_reward_renderer.ny_main_reward_renderer_model import NyMainRewardRendererModel

class NyTankRewardRendererModel(NyMainRewardRendererModel):
    __slots__ = ()

    def getRewardImage(self):
        return self._getResource(1)

    def setRewardImage(self, value):
        self._setResource(1, value)

    def getTierText(self):
        return self._getString(2)

    def setTierText(self, value):
        self._setString(2, value)

    def getNameText(self):
        return self._getString(3)

    def setNameText(self, value):
        self._setString(3, value)

    def getDiscountText(self):
        return self._getString(4)

    def setDiscountText(self, value):
        self._setString(4, value)

    def getIsGifted(self):
        return self._getBool(5)

    def setIsGifted(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(NyTankRewardRendererModel, self)._initialize()
        self._addResourceProperty('rewardImage', Resource.INVALID)
        self._addStringProperty('tierText', '')
        self._addStringProperty('nameText', '')
        self._addStringProperty('discountText', '')
        self._addBoolProperty('isGifted', False)
