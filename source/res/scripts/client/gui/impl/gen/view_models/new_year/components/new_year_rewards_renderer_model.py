# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/new_year/components/new_year_rewards_renderer_model.py
import typing
from frameworks.wulf import Resource
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.new_year.components.ny_reward_renderer.ny_tank_reward_renderer_model import NyTankRewardRendererModel
from gui.impl.gen.view_models.new_year.components.ny_reward_renderer.ny_tankwoman_reward_renderer_model import NyTankwomanRewardRendererModel

class NewYearRewardsRendererModel(ViewModel):
    __slots__ = ()

    @property
    def tankReward(self):
        return self._getViewModel(0)

    @property
    def tankwomanReward(self):
        return self._getViewModel(1)

    @property
    def rewardsGroup(self):
        return self._getViewModel(2)

    def getIdx(self):
        return self._getNumber(3)

    def setIdx(self, value):
        self._setNumber(3, value)

    def getLevelIcon(self):
        return self._getResource(4)

    def setLevelIcon(self, value):
        self._setResource(4, value)

    def getLevelText(self):
        return self._getString(5)

    def setLevelText(self, value):
        self._setString(5, value)

    def getIsLevelAchieved(self):
        return self._getBool(6)

    def setIsLevelAchieved(self, value):
        self._setBool(6, value)

    def getIsCurrentLevel(self):
        return self._getBool(7)

    def setIsCurrentLevel(self, value):
        self._setBool(7, value)

    def getIsLastLevel(self):
        return self._getBool(8)

    def setIsLastLevel(self, value):
        self._setBool(8, value)

    def getIsNextAfterCurrentLevel(self):
        return self._getBool(9)

    def setIsNextAfterCurrentLevel(self, value):
        self._setBool(9, value)

    def getShowTankwoman(self):
        return self._getBool(10)

    def setShowTankwoman(self, value):
        self._setBool(10, value)

    def getIsNewYearEnabled(self):
        return self._getBool(11)

    def setIsNewYearEnabled(self, value):
        self._setBool(11, value)

    def _initialize(self):
        super(NewYearRewardsRendererModel, self)._initialize()
        self._addViewModelProperty('tankReward', NyTankRewardRendererModel())
        self._addViewModelProperty('tankwomanReward', NyTankwomanRewardRendererModel())
        self._addViewModelProperty('rewardsGroup', UserListModel())
        self._addNumberProperty('idx', 0)
        self._addResourceProperty('levelIcon', Resource.INVALID)
        self._addStringProperty('levelText', '')
        self._addBoolProperty('isLevelAchieved', False)
        self._addBoolProperty('isCurrentLevel', False)
        self._addBoolProperty('isLastLevel', False)
        self._addBoolProperty('isNextAfterCurrentLevel', False)
        self._addBoolProperty('showTankwoman', False)
        self._addBoolProperty('isNewYearEnabled', False)
