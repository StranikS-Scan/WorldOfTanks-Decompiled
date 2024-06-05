# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dog_tags/catalog_animated_dog_tag_tooltip.py
import typing
import BigWorld
from frameworks.wulf import ViewSettings
from advanced_achievements_client.items import SteppedAchievement
from dog_tags_common.components_config import componentConfigAdapter as componentConfig
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.dog_tags.catalog_animated_dog_tag_tooltip_model import CatalogAnimatedDogTagTooltipModel
from gui.impl.lobby.dog_tags.dog_tag_composer import DogTagComposerLobby
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IAchievementsController
from uilogging.dog_tags.logging_constants import DogTagKeys, DogTagsViewKeys
from uilogging.dog_tags.logger import DogTagsTooltipLogger
if typing.TYPE_CHECKING:
    from account_helpers.dog_tags import DogTags as DogTagsAccountHelper
    from advanced_achievements_client.items import _BaseGuiAchievement, _Progress

class CatalogAnimatedDogTagTooltip(ViewImpl):
    __slots__ = ('__dogTagsHelper', '__composer', '__uiLogger', '__backgroundId', '__engravingId')
    __achievementsController = dependency.descriptor(IAchievementsController)

    def __init__(self, params, layoutID=R.views.lobby.dog_tags.CatalogAnimatedDogTagTooltip(), uiParent=DogTagsViewKeys.HANGAR):
        settings = ViewSettings(layoutID)
        settings.model = CatalogAnimatedDogTagTooltipModel()
        settings.kwargs = params
        self.__dogTagsHelper = BigWorld.player().dogTags
        self.__composer = DogTagComposerLobby(self.__dogTagsHelper)
        self.__uiLogger = DogTagsTooltipLogger(DogTagKeys.ANIMATION_TOOLTIP, uiParent)
        self.__backgroundId = None
        self.__engravingId = None
        super(CatalogAnimatedDogTagTooltip, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(CatalogAnimatedDogTagTooltip, self).getViewModel()

    def _onLoading(self, backgroundId, engravingId):
        super(CatalogAnimatedDogTagTooltip, self)._onLoading()
        with self.viewModel.transaction() as model:
            achievement = self.__getRequiredAchievement(backgroundId)
            model.setStage(achievement.getNextOrLastStageID())
            progress = achievement.getProgress()
            model.setRequiredItemsCount(progress.total)
            model.setItemsLeft(progress.total - progress.current)
            self.__backgroundId = backgroundId
            self.__engravingId = engravingId
            dogTag = self.__dogTagsHelper.getDisplayableDTForComponents([backgroundId, engravingId])
            self.__composer.fillModel(model.equippedDogTag, dogTag, isUnlocked=progress.isCompleted())

    def _onLoaded(self, *args, **kwargs):
        self.__uiLogger.viewOpened()
        super(CatalogAnimatedDogTagTooltip, self)._onLoaded()

    def getLogInfo(self):
        unlockedIds = self.__dogTagsHelper.getUnlockedComps()
        isUnlocked = self.__backgroundId in unlockedIds and self.__engravingId in unlockedIds
        return 'available' if isUnlocked else 'unavailable'

    def _finalize(self):
        self.__uiLogger.viewClosed(info=self.getLogInfo())
        self.__dogTagsHelper = None
        self.__composer = None
        self.__backgroundId = None
        self.__engravingId = None
        super(CatalogAnimatedDogTagTooltip, self)._finalize()
        return

    def __getRequiredAchievement(self, backgroundId):
        component = componentConfig.getComponentById(backgroundId)
        achievementCategory, achievementId, achievementStage = component.unlockKey
        achievement = self.__achievementsController.getAchievementByID(int(achievementId), achievementCategory)
        if isinstance(achievement, SteppedAchievement):
            achievement = achievement.getFakeAchievementForStage(int(achievementStage))
        return achievement
