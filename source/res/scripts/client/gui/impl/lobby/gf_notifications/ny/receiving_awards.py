# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/gf_notifications/ny/receiving_awards.py
from CurrentVehicle import g_currentVehicle
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import dependency, isPlayerAccount
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.lobby.new_year.notifications.receiving_rewards_model import ReceivingRewardsModel
from gui.impl.lobby.gf_notifications.ny.award_notification_base import AwardNotificationBase, bonusesSortOrder, splitHugeBonuses, customSplitBonuses, fromRawBonusWithListsToBonuses
from gui.impl.lobby.new_year.tooltips.ny_gift_machine_token_tooltip import NyGiftMachineTokenTooltip
from gui.impl.lobby.new_year.tooltips.ny_guest_dog_token_tooltip import NyGuestDogTokenTooltip
from gui.impl.lobby.new_year.tooltips.ny_marketplace_token_tooltip import NyMarketplaceTokenTooltip
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
from gui.impl.new_year.navigation import ViewAliases
from gui.impl.new_year.new_year_bonus_packer import getChallengeBonusPacker
from gui.impl.new_year.new_year_helper import backportTooltipDecorator
from new_year.ny_constants import NYObjects
from shared_utils import findFirst, first
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
_FIRST_LVL = 1

class ReceivingAwards(AwardNotificationBase):
    __itemsCache = dependency.descriptor(IItemsCache)
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, resId, *args, **kwargs):
        model = ReceivingRewardsModel()
        super(ReceivingAwards, self).__init__(resId, model, *args, **kwargs)
        self.__rewards = []
        self.__currentLevel = 0

    @property
    def viewModel(self):
        return super(ReceivingAwards, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        data = self.linkageData.toDict()
        self.__rewards = fromRawBonusWithListsToBonuses(data.get('bonuses', []))
        self.__currentLevel = data.get('completedLevel', 0)
        battleCount = self.__itemsCache.items.getAccountDossier().getTotalStats().getBattlesCount()
        if self.__currentLevel == _FIRST_LVL and self._isPopUp:
            g_eventBus.handleEvent(events.NyInitialNotificationEvent(eventType=events.NyInitialNotificationEvent.INITIAL_NOTIFICATION_SHOWN), scope=EVENT_BUS_SCOPE.LOBBY)
            if battleCount > 0:
                self.__processVehicleChange()
        super(ReceivingAwards, self)._onLoading(self)

    def _canNavigate(self):
        return super(ReceivingAwards, self)._canNavigate() and self._nyController.isEnabled()

    def _update(self):
        self.__setRewards()

    def _getEvents(self):
        return super(ReceivingAwards, self)._getEvents() + ((self.viewModel.onClick, self._onClick), (self.viewModel.onGoToRewards, self.__onGoToRewards))

    def createToolTipContent(self, event, ctID):
        if ctID == R.views.lobby.tooltips.AdditionalRewardsTooltip():
            showCount = int(event.getArgument('showedCount'))
            bonuses = customSplitBonuses(self.__rewards)
            _, secondaryBonuses = splitHugeBonuses(bonuses)
            bonuses = sorted(secondaryBonuses, key=bonusesSortOrder)[showCount:]
            bonusPackers = getChallengeBonusPacker()
            packedBonuses = []
            for bonus in bonuses:
                if bonus.isShowInGUI():
                    bonusList = bonusPackers.pack(bonus)
                    for item in bonusList:
                        packedBonuses.append(item)

            return AdditionalRewardsTooltip(packedBonuses)
        if ctID == R.views.lobby.new_year.tooltips.NyMarketplaceTokenTooltip():
            return NyMarketplaceTokenTooltip()
        if ctID == R.views.lobby.new_year.tooltips.NyGuestDogTokenTooltip():
            return NyGuestDogTokenTooltip()
        return NyGiftMachineTokenTooltip() if ctID == R.views.lobby.new_year.tooltips.NyGiftMachineTokenTooltip() else super(ReceivingAwards, self).createToolTipContent(event, ctID)

    @backportTooltipDecorator()
    def createToolTip(self, event):
        return super(ReceivingAwards, self).createToolTip(event)

    def __processVehicleChange(self):
        if not isPlayerAccount():
            return
        else:
            vehicleBonus = findFirst(lambda bonus: bonus.getName() == 'vehicles', self.__rewards)
            if vehicleBonus is not None:
                vehicle, _ = first(vehicleBonus.getVehicles(), (None, None))
                if vehicle is not None:
                    g_currentVehicle.selectVehicle(vehicle.invID)
            return

    def __setRewards(self):
        bonuses = customSplitBonuses(self.__rewards)
        hugeBonuses, otherBonuses = splitHugeBonuses(bonuses)
        with self.getViewModel().transaction() as model:
            self._tooltips.clear()
            self._fillRewardsList(rewardsList=model.hugeRewards.getItems(), bonuses=hugeBonuses, sortMethod=bonusesSortOrder, packer=getChallengeBonusPacker())
            self._fillRewardsList(rewardsList=model.rewards.getItems(), bonuses=otherBonuses, sortMethod=bonusesSortOrder, packer=getChallengeBonusPacker())
            model.setIsPopUp(self._isPopUp)
            model.setLevel(self.__currentLevel)
            model.setIsButtonDisabled(not self._canNavigate())

    def _onClick(self):
        self._navigateToNy(NYObjects.TOWN, ViewAliases.GLADE_VIEW)

    def __onGoToRewards(self):
        self._navigateToNy(None, ViewAliases.REWARDS_VIEW)
        return
