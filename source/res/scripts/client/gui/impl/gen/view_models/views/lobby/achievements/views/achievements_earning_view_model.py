# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/achievements/views/achievements_earning_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.achievements.advanced_achievement_model import AdvancedAchievementModel

class AchievementsEarningViewModel(ViewModel):
    __slots__ = ('onShown', 'onGoToAchievement')

    def __init__(self, properties=2, commands=2):
        super(AchievementsEarningViewModel, self).__init__(properties=properties, commands=commands)

    def getIsAnimationPlaying(self):
        return self._getBool(0)

    def setIsAnimationPlaying(self, value):
        self._setBool(0, value)

    def getAchievements(self):
        return self._getArray(1)

    def setAchievements(self, value):
        self._setArray(1, value)

    @staticmethod
    def getAchievementsType():
        return AdvancedAchievementModel

    def _initialize(self):
        super(AchievementsEarningViewModel, self)._initialize()
        self._addBoolProperty('isAnimationPlaying', False)
        self._addArrayProperty('achievements', Array())
        self.onShown = self._addCommand('onShown')
        self.onGoToAchievement = self._addCommand('onGoToAchievement')
