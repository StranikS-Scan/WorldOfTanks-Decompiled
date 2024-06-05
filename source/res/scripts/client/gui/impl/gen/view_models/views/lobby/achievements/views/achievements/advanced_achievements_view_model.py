# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/achievements/views/achievements/advanced_achievements_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.achievements.subcategory_advanced_achievement_model import SubcategoryAdvancedAchievementModel
from gui.impl.gen.view_models.views.lobby.achievements.views.achievements.upcoming_model import UpcomingModel

class AdvancedAchievementsViewModel(ViewModel):
    __slots__ = ('onOpenTrophies', 'onOpenDetails', 'onCupClick', 'onAnimationInProgress', 'onAllAnimationEnd', 'onAchievementHover')

    def __init__(self, properties=12, commands=6):
        super(AdvancedAchievementsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def trophy(self):
        return self._getViewModel(0)

    @staticmethod
    def getTrophyType():
        return SubcategoryAdvancedAchievementModel

    def getPrevAchievementsScore(self):
        return self._getNumber(1)

    def setPrevAchievementsScore(self, value):
        self._setNumber(1, value)

    def getAchievementsScore(self):
        return self._getNumber(2)

    def setAchievementsScore(self, value):
        self._setNumber(2, value)

    def getMaxAchievementsScore(self):
        return self._getNumber(3)

    def setMaxAchievementsScore(self, value):
        self._setNumber(3, value)

    def getIsOtherPlayer(self):
        return self._getBool(4)

    def setIsOtherPlayer(self, value):
        self._setBool(4, value)

    def getCategoryProgress(self):
        return self._getNumber(5)

    def setCategoryProgress(self, value):
        self._setNumber(5, value)

    def getPrevCategoryProgress(self):
        return self._getNumber(6)

    def setPrevCategoryProgress(self, value):
        self._setNumber(6, value)

    def getCategoryName(self):
        return self._getString(7)

    def setCategoryName(self, value):
        self._setString(7, value)

    def getCategoryBackgroundName(self):
        return self._getString(8)

    def setCategoryBackgroundName(self, value):
        self._setString(8, value)

    def getIsSkipAnimation(self):
        return self._getBool(9)

    def setIsSkipAnimation(self, value):
        self._setBool(9, value)

    def getUpcomingAchievements(self):
        return self._getArray(10)

    def setUpcomingAchievements(self, value):
        self._setArray(10, value)

    @staticmethod
    def getUpcomingAchievementsType():
        return UpcomingModel

    def getSubcategories(self):
        return self._getArray(11)

    def setSubcategories(self, value):
        self._setArray(11, value)

    @staticmethod
    def getSubcategoriesType():
        return SubcategoryAdvancedAchievementModel

    def _initialize(self):
        super(AdvancedAchievementsViewModel, self)._initialize()
        self._addViewModelProperty('trophy', SubcategoryAdvancedAchievementModel())
        self._addNumberProperty('prevAchievementsScore', 0)
        self._addNumberProperty('achievementsScore', 0)
        self._addNumberProperty('maxAchievementsScore', 0)
        self._addBoolProperty('isOtherPlayer', False)
        self._addNumberProperty('categoryProgress', 0)
        self._addNumberProperty('prevCategoryProgress', 0)
        self._addStringProperty('categoryName', '')
        self._addStringProperty('categoryBackgroundName', '')
        self._addBoolProperty('isSkipAnimation', False)
        self._addArrayProperty('upcomingAchievements', Array())
        self._addArrayProperty('subcategories', Array())
        self.onOpenTrophies = self._addCommand('onOpenTrophies')
        self.onOpenDetails = self._addCommand('onOpenDetails')
        self.onCupClick = self._addCommand('onCupClick')
        self.onAnimationInProgress = self._addCommand('onAnimationInProgress')
        self.onAllAnimationEnd = self._addCommand('onAllAnimationEnd')
        self.onAchievementHover = self._addCommand('onAchievementHover')
