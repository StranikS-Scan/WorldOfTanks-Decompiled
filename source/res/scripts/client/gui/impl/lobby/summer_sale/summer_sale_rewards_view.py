# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/summer_sale/summer_sale_rewards_view.py
from copy import deepcopy
from constants import LOOTBOX_TOKEN_PREFIX
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.summer_sale.summer_sale_rewards_view_model import SummerSaleRewardsViewModel
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.loot_box.loot_box_helper import createTooltipLootBoxContentDecorator
from gui.impl.lobby.promo_code_reward_screen.bonuses import getRewardsBonusPacker
from gui.impl.pub import ViewImpl, WindowImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.server_events.bonuses import getNonQuestBonuses, mergeBonuses, splitBonuses, VehiclesBonus
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from gui.shared.event_dispatcher import selectVehicleInHangar
from gui.shared.money import Currency
from gui.summer_sale.common import getBonusName, MAIN_COIN, ADDITIONAL_COIN
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.shared import IItemsCache
_BONUSES_ORDER = {bonusName:order for order, bonusName in enumerate((VehiclesBonus.VEHICLES_BONUS,
 ADDITIONAL_COIN,
 MAIN_COIN,
 'lootBoxToken',
 Currency.CREDITS))}

class SummerSaleRewardsView(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__tooltipData', '__rewards', '__mainVehicleCd')

    def __init__(self, layoutID, rewards):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = SummerSaleRewardsViewModel()
        self.__rewards = deepcopy(rewards)
        self.__tooltipData = {}
        self.__mainVehicleCd = None
        super(SummerSaleRewardsView, self).__init__(settings)
        for token, value in self.__rewards.get('tokens', {}).items():
            if token.startswith(LOOTBOX_TOKEN_PREFIX) and value.get('count') < 0:
                self.__rewards['tokens'].pop(token)

        self.__rewards.pop('slots', None)
        return

    @createTooltipLootBoxContentDecorator()
    def createToolTipContent(self, event, contentID):
        return super(SummerSaleRewardsView, self).createToolTipContent(event=event, contentID=contentID)

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(SummerSaleRewardsView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipData.get(tooltipId)

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose), (self.viewModel.onShowVehicleInHangar, self.__showVehicleInHangar))

    def _onLoading(self, *args, **kwargs):
        super(SummerSaleRewardsView, self)._onLoading(*args, **kwargs)
        self.__fillRewardsModel()

    def __onClose(self):
        g_eventBus.handleEvent(events.SummerSaleViewEvent(events.SummerSaleViewEvent.ON_CLOSE_REWARD_VIEW), scope=EVENT_BUS_SCOPE.LOBBY)
        self.destroyWindow()

    @property
    def viewModel(self):
        return super(SummerSaleRewardsView, self).getViewModel()

    @replaceNoneKwargsModel
    def __fillRewardsModel(self, model=None):
        rewardsList = model.getRewards()
        mainRewardsList = model.getMainRewards()
        rewardsList.clear()
        mainRewardsList.clear()
        rewards = []
        for bonusType, bonusValue in self.__rewards.iteritems():
            rewards.extend(getNonQuestBonuses(bonusType, bonusValue))

        rewards = splitBonuses(mergeBonuses(rewards))
        rewards = sorted(rewards, key=lambda b: _BONUSES_ORDER.get(getBonusName(b), -1))
        vehicleBonus = findFirst(lambda bonus: bonus.getName() == 'vehicles', rewards)
        if vehicleBonus:
            vehicle, _ = vehicleBonus.getVehicles()[0]
            self.__mainVehicleCd = vehicle.intCD
        mainRewards = rewards[:3]
        rewards = rewards[3:]
        if len(mainRewards) == 3:
            mainRewards[0], mainRewards[1] = mainRewards[1], mainRewards[0]
        packBonusModelAndTooltipData(mainRewards, mainRewardsList, self.__tooltipData, getRewardsBonusPacker())
        packBonusModelAndTooltipData(rewards, rewardsList, self.__tooltipData, getRewardsBonusPacker(), len(mainRewardsList))
        rewardsList.invalidate()
        mainRewardsList.invalidate()

    def __showVehicleInHangar(self):
        if self.__mainVehicleCd is not None:
            self.destroyWindow()
            selectVehicleInHangar(self.__mainVehicleCd)
        return


class SummerSaleRewardsViewWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, rewards, parent=None):
        super(SummerSaleRewardsViewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=SummerSaleRewardsView(R.views.lobby.summer_sale.SummerSaleRewardsView(), rewards), layer=WindowLayer.FULLSCREEN_WINDOW, parent=parent)
