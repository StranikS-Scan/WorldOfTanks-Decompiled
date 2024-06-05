# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dog_tags/animated_dog_tag_grade_tooltip.py
from frameworks.wulf import ViewSettings
from advanced_achievements_client.items import SteppedAchievement
from dog_tags_common.components_config import componentConfigAdapter as componentConfig
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.dog_tags.animated_dog_tag_grade_tooltip_model import AnimatedDogTagGradeTooltipModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IAchievementsController

class AnimatedDogTagGradeTooltip(ViewImpl):
    __slots__ = ()
    __achievementsController = dependency.descriptor(IAchievementsController)

    def __init__(self, params, layoutID=R.views.lobby.dog_tags.AnimatedDogTagGradeTooltip()):
        settings = ViewSettings(layoutID)
        settings.model = AnimatedDogTagGradeTooltipModel()
        settings.kwargs = params
        super(AnimatedDogTagGradeTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(AnimatedDogTagGradeTooltip, self).getViewModel()

    def _onLoading(self, backgroundId, engravingId):
        super(AnimatedDogTagGradeTooltip, self)._onLoading()
        with self.viewModel.transaction() as model:
            model.setBackgroundId(backgroundId)
            model.setEngravingId(engravingId)
            achievement = self.__getRequiredAchievement(backgroundId)
            progress = achievement.getProgress()
            model.setRequiredItemsCount(progress.total)
            component = componentConfig.getComponentById(backgroundId)
            _, _, achievementStage = component.unlockKey
            model.setStage(int(achievementStage))

    def __getRequiredAchievement(self, backgroundId):
        component = componentConfig.getComponentById(backgroundId)
        achievementCategory, achievementId, achievementStage = component.unlockKey
        achievement = self.__achievementsController.getAchievementByID(int(achievementId), achievementCategory)
        if isinstance(achievement, SteppedAchievement):
            achievement = achievement.getFakeAchievementForStage(int(achievementStage))
        return achievement
