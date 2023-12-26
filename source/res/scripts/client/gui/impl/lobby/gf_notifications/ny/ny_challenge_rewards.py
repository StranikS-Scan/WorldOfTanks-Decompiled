# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/gf_notifications/ny/ny_challenge_rewards.py
from gui.impl.gen.view_models.views.lobby.new_year.notifications.ny_challenge_rewards_model import NyChallengeRewardsModel, Type
from gui.impl.lobby.gf_notifications.ny.award_notification_base import AwardNotificationBase, MAX_HUGE_REWARDS, fromRawBonusesToBonuses
from gui.impl.gen import R
from helpers import dependency
from gui.impl.lobby.new_year.tooltips.ny_economic_bonus_tooltip import NyEconomicBonusTooltip
from gui.impl.lobby.new_year.tooltips.ny_gift_machine_token_tooltip import NyGiftMachineTokenTooltip
from gui.impl.new_year.navigation import ViewAliases, NewYearNavigation
from new_year.ny_constants import NYObjects
from gui.shared.utils import flashObject2Dict
from gui.impl.new_year.new_year_helper import nyCreateToolTipContentDecorator, backportTooltipDecorator, ADDITIONAL_BONUS_NAME_GETTERS
from gui.impl.new_year.new_year_bonus_packer import getChallengeBonusPacker
from gui.shared import event_dispatcher
from gui.server_events.bonuses import NYCoinTokenBonus
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.server_events import IEventsCache
from skeletons.new_year import ICelebritySceneController
_HUGE_BONUSES = ('customizations_style', 'tmanToken', 'vehicles')
BONUSES_ORDER = ('tmanToken', 'customizations_style', 'vehicles', 'playerBadges', 'singleAchievements')

def _splitHugeBonuses(bonuses):
    hugeBonuses = []
    otherBonuses = []
    for bonus in bonuses:
        bonusName = bonus.getName()
        getAdditionalName = ADDITIONAL_BONUS_NAME_GETTERS.get(bonusName)
        if getAdditionalName is not None:
            bonusName = getAdditionalName(bonus)
        if bonusName in _HUGE_BONUSES:
            hugeBonuses.append(bonus)
        otherBonuses.append(bonus)

    if hugeBonuses:
        hugeBonuses.sort(key=_bonusesSortOrder)
        if len(hugeBonuses) > MAX_HUGE_REWARDS:
            otherBonuses.extend(hugeBonuses[MAX_HUGE_REWARDS:])
            hugeBonuses = hugeBonuses[:MAX_HUGE_REWARDS]
    else:
        otherBonuses.sort(key=_bonusesSortOrder)
        delimiter = MAX_HUGE_REWARDS if len(otherBonuses) >= MAX_HUGE_REWARDS else len(otherBonuses)
        hugeBonuses.extend(otherBonuses[:delimiter])
        otherBonuses = otherBonuses[delimiter:]
    return (hugeBonuses, otherBonuses)


def _bonusesSortOrder(bonus):
    bonusName = bonus.getName()
    getAdditionalName = ADDITIONAL_BONUS_NAME_GETTERS.get(bonusName)
    if getAdditionalName is not None:
        bonusName = getAdditionalName(bonus)
    return BONUSES_ORDER.index(bonusName) if bonusName in BONUSES_ORDER else len(BONUSES_ORDER)


class NyChallengeRewards(AwardNotificationBase):
    eventsCache = dependency.descriptor(IEventsCache)
    __celebritySceneController = dependency.descriptor(ICelebritySceneController)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, resId, *args, **kwargs):
        model = NyChallengeRewardsModel()
        super(NyChallengeRewards, self).__init__(resId, model, *args, **kwargs)
        self.__bonuses = []
        self.__additionalBonuses = {}
        self.__guestName = Type.CHALLENGE
        self.__questIndex = 0
        self.__completedQuestsCount = 0

    @property
    def viewModel(self):
        return super(NyChallengeRewards, self).getViewModel()

    def __prepareRawData(self, rawData):
        rewards = {}
        for key, data in rawData.iteritems():
            if isinstance(data, list):
                listOfBonuses = []
                for item in data:
                    listOfBonuses.append(flashObject2Dict(item))

                rewards[key] = listOfBonuses
            rewards[key] = data

        return rewards

    def _onLoading(self, *args, **kwargs):
        data = self._linkageData.toDict()
        self.__questIndex = data.get('questIndex', 0)
        bonuses = fromRawBonusesToBonuses(self.__prepareRawData(flashObject2Dict(data.get('bonuses', {}))))
        additionalBonuses = self.__prepareRawData(flashObject2Dict(data.get('additionalBonuses', {})))
        if bonuses:
            self.__bonuses = bonuses
            self.__completedQuestsCount = data.get('completedQuestsCount', 0)
            if additionalBonuses:
                self.__additionalBonuses = additionalBonuses
        super(NyChallengeRewards, self)._onLoading(self)

    def _update(self):
        self.__setRewards()

    @backportTooltipDecorator()
    def createToolTip(self, event):
        return super(NyChallengeRewards, self).createToolTip(event)

    @nyCreateToolTipContentDecorator
    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.new_year.tooltips.NyGiftMachineTokenTooltip():
            return NyGiftMachineTokenTooltip()
        if event.contentID == R.views.lobby.new_year.tooltips.NyEconomicBonusTooltip():
            isMaxBonus = event.getArgument('isMaxBonus', False)
            if isMaxBonus or self.__questIndex > -1:
                return NyEconomicBonusTooltip(isMaxBonus, self.__questIndex, self.__guestName)
        return super(NyChallengeRewards, self).createToolTipContent(event, contentID)

    def _getEvents(self):
        events = super(NyChallengeRewards, self)._getEvents()
        return events + ((self.viewModel.onClick, self.__onClick), (self.viewModel.onRecruit, self.__onRecruit))

    def __getCoinBonus(self, bonuses):
        for questName in bonuses:
            for bonus in fromRawBonusesToBonuses(bonuses.get(questName, {})):
                if isinstance(bonus, NYCoinTokenBonus):
                    return bonus

    def __setRewards(self):
        coinBonus = self.__getCoinBonus(self.__additionalBonuses)
        bonuses = self.__bonuses
        if coinBonus:
            bonuses.append(coinBonus)
        hugeBonuses, otherBonuses = _splitHugeBonuses(bonuses)
        canNavigate = self._canNavigate() if self.__hasTmanToken(hugeBonuses) else self._canNavigate() and self._nyController.isEnabled()
        with self.getViewModel().transaction() as model:
            self._tooltips.clear()
            self._fillRewardsList(rewardsList=model.hugeRewards.getItems(), bonuses=hugeBonuses, sortMethod=_bonusesSortOrder, packer=getChallengeBonusPacker())
            self._fillRewardsList(rewardsList=model.rewards.getItems(), bonuses=otherBonuses, sortMethod=_bonusesSortOrder, packer=getChallengeBonusPacker())
            model.setIsPopUp(self._isPopUp)
            model.setIsButtonDisabled(not canNavigate)
            model.setCompletedQuestsQuantity(self.__completedQuestsCount)
            model.setTotalQuestsQuantity(self.__celebritySceneController.questsCount)

    def __hasTmanToken(self, bonuses):
        for bonus in bonuses:
            if bonus.getName() == 'tmanToken':
                return True

    def __onClick(self):
        if self._canNavigate() and self._nyController.isEnabled():
            viewName = NewYearNavigation.getCurrentViewName()
            if viewName != ViewAliases.CELEBRITY_VIEW:
                self._navigateToNy(NYObjects.CHALLENGE, ViewAliases.CELEBRITY_VIEW)

    def __onRecruit(self):
        if self._canNavigate():
            event_dispatcher.showBarracks()
