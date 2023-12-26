# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/collected_resources_reward_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class CollectedResourcesRewardViewModel(ViewModel):
    __slots__ = ('onStylePreview',)
    LOW_GRAPHICS_PRESET = 4

    def __init__(self, properties=5, commands=1):
        super(CollectedResourcesRewardViewModel, self).__init__(properties=properties, commands=commands)

    def getIsStyle(self):
        return self._getBool(0)

    def setIsStyle(self, value):
        self._setBool(0, value)

    def getRecommendedGraphicsPreset(self):
        return self._getNumber(1)

    def setRecommendedGraphicsPreset(self, value):
        self._setNumber(1, value)

    def getNumberOfCollecting(self):
        return self._getNumber(2)

    def setNumberOfCollecting(self, value):
        self._setNumber(2, value)

    def getIs3dSceneVisible(self):
        return self._getBool(3)

    def setIs3dSceneVisible(self, value):
        self._setBool(3, value)

    def getRewards(self):
        return self._getArray(4)

    def setRewards(self, value):
        self._setArray(4, value)

    @staticmethod
    def getRewardsType():
        return IconBonusModel

    def _initialize(self):
        super(CollectedResourcesRewardViewModel, self)._initialize()
        self._addBoolProperty('isStyle', False)
        self._addNumberProperty('recommendedGraphicsPreset', 0)
        self._addNumberProperty('numberOfCollecting', 0)
        self._addBoolProperty('is3dSceneVisible', True)
        self._addArrayProperty('rewards', Array())
        self.onStylePreview = self._addCommand('onStylePreview')
