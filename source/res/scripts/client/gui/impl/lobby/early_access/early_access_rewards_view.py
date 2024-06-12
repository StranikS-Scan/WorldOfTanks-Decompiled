# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/early_access/early_access_rewards_view.py
from copy import copy
import constants
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from early_access_common import EARLY_ACCESS_POSTPR_KEY
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.early_access.early_access_rewards_view_model import EarlyAccessRewardsViewModel
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
from gui.impl.pub import ViewImpl, WindowImpl
from gui.server_events.bonuses import getNonQuestBonuses, splitBonuses, mergeBonuses
from gui.shared.bonuses_sorter import bonusesSortKeyFunc
from gui.shared.missions.packers.bonus import getDefaultBonusPackersMap, PremiumDaysBonusPacker, BonusUIPacker
from helpers import dependency
from skeletons.gui.game_control import IEarlyAccessController
from skeletons.gui.shared import IItemsCache
_MAX_MAIN_REWARDS = 3

def _getEarlyAccessDefaultBonusPackerMap():
    mapping = getDefaultBonusPackersMap()
    mapping.update({constants.PREMIUM_ENTITLEMENTS.PLUS: PremiumDaysBonusPacker()})
    return mapping


def _getEarlyAccessRewardsBonusPacker():
    return BonusUIPacker(_getEarlyAccessDefaultBonusPackerMap())


class EarlyAccessRewardsView(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)
    __earlyAccessController = dependency.descriptor(IEarlyAccessController)
    __slots__ = ('__tooltipData', '__rawBonuses')

    def __init__(self, layoutID, bonuses):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = EarlyAccessRewardsViewModel()
        self.__tooltipData = {}
        self.__rawBonuses = copy(bonuses)
        super(EarlyAccessRewardsView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EarlyAccessRewardsView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(EarlyAccessRewardsView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        lootBoxRes = R.views.dyn('gui_lootboxes').dyn('lobby').dyn('gui_lootboxes').dyn('tooltips').dyn('LootboxTooltip')
        if lootBoxRes.exists() and contentID == lootBoxRes():
            from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.lootbox_tooltip import LootboxTooltip
            lootBoxID = self.getTooltipData(event)['lootBoxID']
            lootBox = self.__itemsCache.items.tokens.getLootBoxByID(int(lootBoxID))
            return LootboxTooltip(lootBox)
        if contentID == R.views.lobby.tooltips.AdditionalRewardsTooltip():
            packedBonuses = self.viewModel.getRewards()[self.viewModel.MAX_REWARDS:]
            return AdditionalRewardsTooltip(packedBonuses)
        return super(EarlyAccessRewardsView, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        index = event.getArgument(EarlyAccessRewardsViewModel.ARG_REWARD_INDEX)
        return self.__tooltipData.get(index, None)

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),)

    def _onLoading(self, *args, **kwargs):
        super(EarlyAccessRewardsView, self)._onLoading(*args, **kwargs)
        rewards = []
        for bonusType, bonusValue in self.__rawBonuses.items():
            bonus = getNonQuestBonuses(bonusType, bonusValue)
            rewards.extend(bonus)

        rewards = splitBonuses(mergeBonuses(rewards))
        rewards.sort(key=bonusesSortKeyFunc)
        mainRewards = rewards[:_MAX_MAIN_REWARDS]
        rewards = rewards[_MAX_MAIN_REWARDS:]
        if len(mainRewards) == _MAX_MAIN_REWARDS:
            mainRewards[0], mainRewards[1] = mainRewards[1], mainRewards[0]
        with self.viewModel.transaction() as vm:
            vm.setHasAllRewards(self.__earlyAccessController.isGroupQuestsCompleted(EARLY_ACCESS_POSTPR_KEY))
            packer = _getEarlyAccessRewardsBonusPacker()
            self.__fillRewardsModel(mainRewards, vm.getMainRewards(), packer)
            self.__fillRewardsModel(rewards, vm.getRewards(), packer)

    def __fillRewardsModel(self, rewards, rewardsList, packer):
        rewardsList.clear()
        packBonusModelAndTooltipData(rewards, rewardsList, self.__tooltipData, packer)
        rewardsList.invalidate()

    def __onClose(self):
        self.destroyWindow()


class EarlyAccessRewardsViewWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, bonuses=None, parent=None):
        super(EarlyAccessRewardsViewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=EarlyAccessRewardsView(R.views.lobby.early_access.EarlyAccessRewardsView(), bonuses or {}), parent=parent)
