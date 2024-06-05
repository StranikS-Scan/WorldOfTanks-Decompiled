# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/advanced_achievement/logger.py
from typing import TYPE_CHECKING
from advanced_achievements_client.getters import getAchievementByID
from helpers import dependency
from skeletons.gui.game_control import IAchievementsController
from uilogging.base.logger import MetricsLogger
from uilogging.advanced_achievement.logging_constants import FEATURE, AdvancedAchievementActions, AdvancedAchievementInfoKeys, AdvancedAchievementViewKey, AdvancedAchievementKeys, AdvancedAchievementSubcategory, AdvancedAchievementStates
from wotdecorators import noexcept
if TYPE_CHECKING:
    from typing import Optional
    from uilogging.types import ParentScreenType, ItemType, InfoType

class AdvancedAchievementMetricsLoger(MetricsLogger):
    __slots__ = ()

    def __init__(self):
        super(AdvancedAchievementMetricsLoger, self).__init__(FEATURE)

    def logClick(self, item, parentScreen=None, info=None):
        self.log(action=AdvancedAchievementActions.CLICK, item=item, parentScreen=parentScreen, info=info)

    def onViewOpen(self, item, parentScreen=None, info=None):
        self.log(action=AdvancedAchievementActions.DISPLAY, item=item, parentScreen=parentScreen, info=info)


class AdvancedAchievementLogger(AdvancedAchievementMetricsLoger):
    __slots__ = ('_parentViewKey',)
    __achievementsController = dependency.descriptor(IAchievementsController)
    __SUBCATEGORY = {'vehicleAchievements': {1: AdvancedAchievementSubcategory.VEHICLE,
                             2: AdvancedAchievementSubcategory.NATIONS},
     'customizationAchievements': {1: AdvancedAchievementSubcategory.CUSTOMIZATION}}

    def __init__(self, parentViewKey):
        super(AdvancedAchievementLogger, self).__init__()
        self._parentViewKey = parentViewKey

    def logClick(self, item, parentScreen=None, info=None):
        super(AdvancedAchievementLogger, self).logClick(item, parentScreen if parentScreen else self._parentViewKey, info)

    @noexcept
    def logCategoryClick(self, achievementID, category=None):
        info = self.__SUBCATEGORY.get(category).get(achievementID, None)
        item = AdvancedAchievementKeys.SUBCATEGORY if info is not None else AdvancedAchievementKeys.UPCOMING
        super(AdvancedAchievementLogger, self).logClick(item, self._parentViewKey, info)
        return

    @noexcept
    def logCardClick(self, achievementID, category):
        progress = getAchievementByID(achievementID, category).getProgress().getAsPercent()
        info = self.__getStateInfo(progress)
        item = AdvancedAchievementKeys.ACHIEVEMENT_CARD
        super(AdvancedAchievementLogger, self).logClick(item, self._parentViewKey, info)

    @noexcept
    def onViewOpen(self, item, parentScreen=None, info=None, isOtherPlayer=None):
        info = AdvancedAchievementInfoKeys.PLAYER
        if isOtherPlayer:
            info = AdvancedAchievementInfoKeys.ANOTHER_PLAYER
        super(AdvancedAchievementLogger, self).onViewOpen(item, parentScreen if parentScreen else self._parentViewKey, info)

    def __getStateInfo(self, progress):
        if progress == 0:
            return AdvancedAchievementStates.NO_PROGRESS
        return AdvancedAchievementStates.COMPLETED if progress >= 100 else AdvancedAchievementStates.IN_PROGRESS


class AdvancedAchievementEarningLogger(AdvancedAchievementMetricsLoger):

    @noexcept
    def logNotificationClick(self, item, isMultiple):
        info = AdvancedAchievementInfoKeys.MULTIPLE if isMultiple else AdvancedAchievementInfoKeys.SINGLE
        super(AdvancedAchievementEarningLogger, self).logClick(item, parentScreen=AdvancedAchievementViewKey.HANGAR, info=info)

    def onViewOpen(self, item, parentScreen=None, info=None):
        super(AdvancedAchievementEarningLogger, self).onViewOpen(item, parentScreen=AdvancedAchievementViewKey.HANGAR, info=info)


class AdvancedAchievementRewardLogger(AdvancedAchievementMetricsLoger):
    __slots__ = ('_parentViewKey',)

    def __init__(self, parentViewKey):
        super(AdvancedAchievementRewardLogger, self).__init__()
        self._parentViewKey = parentViewKey

    @noexcept
    def logRewardClick(self, item, count):
        info = AdvancedAchievementInfoKeys.MULTIPLE if count > 1 else AdvancedAchievementInfoKeys.SINGLE
        super(AdvancedAchievementRewardLogger, self).logClick(item, parentScreen=self._parentViewKey, info=info)
