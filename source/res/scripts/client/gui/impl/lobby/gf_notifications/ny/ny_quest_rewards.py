# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/gf_notifications/ny/ny_quest_rewards.py
from gui.impl.gen.view_models.views.lobby.new_year.notifications.ny_challenge_rewards_model import NyChallengeRewardsModel, Type
from gui.impl.gen import R
from gui.impl.lobby.gf_notifications.ny.award_notification_base import AwardNotificationBase
from gui.impl.lobby.new_year.tooltips.ny_decoration_tooltip import NyDecorationTooltip
from gui.impl.lobby.new_year.tooltips.ny_gift_machine_token_tooltip import NyGiftMachineTokenTooltip
from gui.impl.lobby.new_year.tooltips.ny_economic_bonus_tooltip import NyEconomicBonusTooltip
from gui.impl.new_year.new_year_helper import backportTooltipDecorator
from gui.impl.new_year.new_year_bonus_packer import getNYCelebrityGuestRewardBonuses, guestQuestBonusSortOrder
from new_year.ny_constants import GuestsQuestsTokens, NyTabBarChallengeView
from gui.shared.utils import flashObject2Dict
from helpers import dependency
from skeletons.new_year import ICelebrityController
from skeletons.gui.shared import IItemsCache
_TAB_NAME_TO_SERVER_GUEST_ID = {NyTabBarChallengeView.GUEST_A: GuestsQuestsTokens.GUEST_A,
 NyTabBarChallengeView.GUEST_CAT: GuestsQuestsTokens.GUEST_C}
_SERVER_GUEST_ID_TO_TAB_NAME = {v:k for k, v in _TAB_NAME_TO_SERVER_GUEST_ID.iteritems()}

class NyQuestReward(AwardNotificationBase):
    __celebrityController = dependency.descriptor(ICelebrityController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, resId, *args, **kwargs):
        model = NyChallengeRewardsModel()
        super(NyQuestReward, self).__init__(resId, model, *args, **kwargs)
        self.__guestName = ''
        self.__questIndex = 0
        self.__bonuses = {}
        self.__completedQuestsQuantity = 0
        self.__totalQuestsQuantity = 0

    @property
    def viewModel(self):
        return super(NyQuestReward, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if event.contentID == R.views.lobby.new_year.tooltips.NyEconomicBonusTooltip():
            isMaxBonus = event.getArgument('isMaxBonus', False)
            if isMaxBonus or self.__questIndex > -1:
                return NyEconomicBonusTooltip(isMaxBonus, self.__questIndex, self.__guestName)
        if contentID == R.views.lobby.new_year.tooltips.NyGiftMachineTokenTooltip():
            return NyGiftMachineTokenTooltip()
        if contentID == R.views.lobby.new_year.tooltips.NyDecorationTooltip():
            toyID = event.getArgument('toyID')
            return NyDecorationTooltip(toyID)
        return super(NyQuestReward, self).createToolTipContent(event, contentID)

    @backportTooltipDecorator()
    def createToolTip(self, event):
        return super(NyQuestReward, self).createToolTip(event)

    def _canNavigate(self):
        return super(NyQuestReward, self)._canNavigate() and self._canShowStyle()

    def _getEvents(self):
        events = super(NyQuestReward, self)._getEvents()
        return events + ((self.viewModel.onStylePreview, self.__onStylePreview),)

    def _onLoading(self, *args, **kwargs):
        data = self._linkageData.toDict()
        self.__guestName = data.get('guestName')
        self.__questIndex = data.get('questIndex')
        self.__bonuses = flashObject2Dict(data.get('bonuses'))
        self.__completedQuestsQuantity = data.get('completedQuestsQuantity')
        self.__totalQuestsQuantity = data.get('totalQuestsQuantity')
        for key, data in flashObject2Dict(data.get('bonuses', {})).iteritems():
            if isinstance(data, list):
                listOfBonuses = []
                for item in data:
                    listOfBonuses.append(flashObject2Dict(item))

                self.__bonuses[key] = listOfBonuses
            self.__bonuses[key] = data

        super(NyQuestReward, self)._onLoading(self)

    def _update(self):
        self.__setRewards()

    def _finalize(self):
        self.__styleItem = None
        super(NyQuestReward, self)._finalize()
        return

    def __setRewards(self):
        self.viewModel.setCompletedQuestsQuantity(self.__completedQuestsQuantity)
        self.viewModel.setTotalQuestsQuantity(self.__totalQuestsQuantity)
        self.viewModel.setType(Type.QUEST)
        self.viewModel.setCelebrity(self.__guestName)
        self.viewModel.setIsPopUp(self._isPopUp)
        self.viewModel.setIsButtonDisabled(not self._canNavigate())
        rewardsList = self.viewModel.rewards
        rewardsList.clear()
        rewards = getNYCelebrityGuestRewardBonuses(self.__bonuses, sortKey=lambda b: guestQuestBonusSortOrder(*b), excludeTokensChecker=GuestsQuestsTokens.isActionToken)
        for index, (bonus, tooltip) in enumerate(rewards):
            tooltipId = str(index)
            bonus.setTooltipId(tooltipId)
            bonus.setIndex(index)
            rewardsList.addViewModel(bonus)
            self._tooltips[tooltipId] = tooltip

        rewardsList.invalidate()

    def __onStylePreview(self, intCD):
        styleItem = self.__itemsCache.items.getItemByCD(int(intCD.get('intCD')))
        if styleItem is None:
            return
        else:
            self._showStylePreview(styleItem)
            return
