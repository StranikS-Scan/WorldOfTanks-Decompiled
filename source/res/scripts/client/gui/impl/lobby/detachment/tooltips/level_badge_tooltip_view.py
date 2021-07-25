# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/tooltips/level_badge_tooltip_view.py
import typing
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.level_badge_model import LevelBadgeModel
from gui.impl.lobby.detachment.rewards import REWARD_TYPES
from gui.impl.pub import ViewImpl
from helpers import dependency
from items.components.detachment_constants import RewardTypes, PROGRESS_MAX
from skeletons.gui.detachment import IDetachmentCache
from uilogging.detachment.loggers import DynamicGroupTooltipLogger
if typing.TYPE_CHECKING:
    from items.detachment import DetachmentDescr
    from gui.shared.gui_items.detachment import Detachment
    from gui.impl.lobby.detachment.rewards import BaseReward

class LevelBadgeTooltipView(ViewImpl):
    detachmentCache = dependency.descriptor(IDetachmentCache)
    _REWARDS_ORDER = (RewardTypes.RANK,
     RewardTypes.BADGE_LEVEL,
     RewardTypes.AUTO_PERKS,
     RewardTypes.SCHOOL_DISCOUNT,
     RewardTypes.ACADEMY_DISCOUNT,
     RewardTypes.VEHICLE_SLOTS,
     RewardTypes.INSTRUCTOR_SLOTS)
    uiLogger = DynamicGroupTooltipLogger()

    def __init__(self, detachmentID, detachment=None):
        settings = ViewSettings(R.views.lobby.detachment.tooltips.LevelBadgeTooltip())
        settings.model = LevelBadgeModel()
        super(LevelBadgeTooltipView, self).__init__(settings)
        self._detachmentID = detachmentID
        if detachment:
            self._detachment = detachment
        else:
            self._detachment = self.detachmentCache.getDetachment(detachmentID)

    @property
    def viewModel(self):
        return super(LevelBadgeTooltipView, self).getViewModel()

    def _onLoading(self):
        super(LevelBadgeTooltipView, self)._onLoading()
        self._updatePersonalInfo()

    def _initialize(self, *args, **kwargs):
        super(LevelBadgeTooltipView, self)._initialize()
        self.uiLogger.tooltipOpened()

    def _finalize(self):
        self.uiLogger.tooltipClosed(self.__class__.__name__)
        self.uiLogger.reset()
        super(LevelBadgeTooltipView, self)._finalize()

    def _updatePersonalInfo(self):
        with self.viewModel.transaction() as vm:
            detDescr = self._detachment.getDescriptor()
            nextMilestoneLevel = self._detachment.nextMilestoneLevel
            vm.setIsConverted(not self._detachmentID)
            vm.setTitle(self._detachment.masteryName)
            nextEliteLevel = nextMilestoneLevel - detDescr.progression.maxLevel
            if nextEliteLevel >= 1:
                vm.setNextEliteLevel(R.strings.detachment.progressionLevel.elite.dyn('c_{}'.format(nextEliteLevel))())
            vm.detachment.setIsElite(self._detachment.hasMaxLevel)
            vm.detachment.setNextLevelIsElite(nextEliteLevel >= 0)
            vm.detachment.setLevel(self._detachment.level)
            vm.detachment.setLevelIconId(self._detachment.levelIconID)
            vm.detachment.setNextLevel(min(nextMilestoneLevel, detDescr.progression.maxLevel))
            vm.detachment.setMaxLevel(detDescr.progression.maxLevel)
            vm.detachment.setProgressValue(detDescr.getCurrentLevelXPProgress() * PROGRESS_MAX)
            vm.detachment.setProgressMax(PROGRESS_MAX)
            self._fillRewards(vm.getCurrentComponents(), self._detachment.currentRewards)
            if not self._detachment.hasMaxMasteryLevel:
                self._fillRewards(vm.getNextComponents(), self._detachment.futureRewards)

    def _fillRewards(self, model, rewards):
        for rewardType in self._REWARDS_ORDER:
            rewardValue = rewards.get(rewardType)
            reward = REWARD_TYPES[rewardType](self._detachment, rewardValue)
            if reward.model:
                model.addViewModel(reward.model)
