# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/new_year_rewards_renderer_model.py
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.new_year.components.level_rewards_group_model import LevelRewardsGroupModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_with_roman_numbers_model import NyWithRomanNumbersModel

class NewYearRewardsRendererModel(NyWithRomanNumbersModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(NewYearRewardsRendererModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewardsGroup(self):
        return self._getViewModel(1)

    @staticmethod
    def getRewardsGroupType():
        return LevelRewardsGroupModel

    def getIdx(self):
        return self._getNumber(2)

    def setIdx(self, value):
        self._setNumber(2, value)

    def getLevelText(self):
        return self._getString(3)

    def setLevelText(self, value):
        self._setString(3, value)

    def getIsLevelAchieved(self):
        return self._getBool(4)

    def setIsLevelAchieved(self, value):
        self._setBool(4, value)

    def getIsCurrentLevel(self):
        return self._getBool(5)

    def setIsCurrentLevel(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(NewYearRewardsRendererModel, self)._initialize()
        self._addViewModelProperty('rewardsGroup', UserListModel())
        self._addNumberProperty('idx', 0)
        self._addStringProperty('levelText', '')
        self._addBoolProperty('isLevelAchieved', False)
        self._addBoolProperty('isCurrentLevel', False)
