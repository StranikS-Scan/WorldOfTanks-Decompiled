# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/popovers/ny_loot_box_statistics_popover.py
from account_helpers.settings_core.settings_constants import NewYearStorageKeys
from frameworks.wulf import ViewSettings
from gui import SystemMessages
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.lobby.new_year.popovers.ny_loot_box_statistics_popover_model import NyLootBoxStatisticsPopoverModel
from gui.impl.gen.view_models.views.lobby.new_year.popovers.ny_loot_box_statistics_reward_model import NyLootBoxStatisticsRewardModel, Type
from gui.impl.lobby.loot_box.loot_box_helper import getLootboxStatisticsKey
from gui.impl.lobby.new_year.tooltips.ny_customizations_statistics_tooltip import NyCustomizationsStatisticsTooltip
from gui.impl.lobby.new_year.tooltips.ny_vehicles_statistics_tooltip import NyVehiclesStatisticsTooltip
from gui.impl.pub import PopOverViewImpl
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils import decorators
from helpers import dependency
from new_year.ny_processor import ResetLootboxStatisticsProcessor
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
_REWARD_ORDER = (Type.VEHICLES,
 Type.CUSTOMIZATIONS,
 Type.PREMIUMPLUS,
 Type.GOLD,
 Type.CREDITS,
 Type.TOYS,
 Type.SHARDS)

class NyLootBoxStatisticsPopover(PopOverViewImpl):
    __slots__ = ('__lootboxID', '__lastStatisticsResetFailed')
    __itemsCache = dependency.descriptor(IItemsCache)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, lootboxID, lastStatisticsResetFailed):
        settings = ViewSettings(R.views.lobby.new_year.popovers.NyLootBoxStatisticsPopover())
        settings.model = NyLootBoxStatisticsPopoverModel()
        super(NyLootBoxStatisticsPopover, self).__init__(settings)
        self.__lootboxID = lootboxID
        self.__lastStatisticsResetFailed = lastStatisticsResetFailed

    @property
    def viewModel(self):
        return super(NyLootBoxStatisticsPopover, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.new_year.tooltips.NyVehiclesStatisticsTooltip():
            return NyVehiclesStatisticsTooltip(self.__lootboxID)
        return NyCustomizationsStatisticsTooltip(self.__lootboxID) if contentID == R.views.lobby.new_year.tooltips.NyCustomizationsStatisticsTooltip() else super(NyLootBoxStatisticsPopover, self).createToolTipContent(event, contentID)

    def _initialize(self, *args, **kwargs):
        super(NyLootBoxStatisticsPopover, self)._initialize(*args, **kwargs)
        self.__settingsCore.serverSettings.saveInNewYearStorage({NewYearStorageKeys.NY_STATISTICS_HINT_SHOWN: True})
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        self.viewModel.onResetClick += self.__onResetClick

    def _finalize(self):
        self.viewModel.onResetClick -= self.__onResetClick
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        super(NyLootBoxStatisticsPopover, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        self.__updateStatistics()

    @decorators.process('newYear/resetLootboxStatistics')
    def __onResetClick(self):
        result = yield ResetLootboxStatisticsProcessor(self.__lootboxID).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType, priority=NotificationPriorityLevel.MEDIUM)
        g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.ON_STATISTICS_RESET, {'serverError': not result.success and bool(result.userMsg)}), EVENT_BUS_SCOPE.LOBBY)

    def __onServerSettingChanged(self, diff):
        if 'lootBoxes_config' in diff:
            self.destroyWindow()

    def __updateStatistics(self):
        with self.viewModel.transaction() as model:
            rewardsData, boxesCount = self.__getStatistics(self.__lootboxID)
            model.setCount(boxesCount)
            model.setIsResetFailed(self.__lastStatisticsResetFailed)
            self.__updateRewards(model, rewardsData)

    def __getStatistics(self, lootboxID):
        rewardsData, boxesCount = {}, 0
        statsKey = getLootboxStatisticsKey(lootboxID)
        return (rewardsData, boxesCount) if statsKey is None else self.__itemsCache.items.tokens.getLootBoxesStats().get(statsKey, (rewardsData, boxesCount))

    def __updateRewards(self, model, rewardsData):
        rewards = model.getRewards()
        rewards.clear()
        for rewardType in _REWARD_ORDER:
            rewardData = rewardsData.get(rewardType.value)
            reward = self.__getRewardModel(rewardType, rewardData)
            if reward is not None:
                rewards.addViewModel(reward)

        rewards.invalidate()
        return

    @staticmethod
    def __getRewardModel(rewardType, rewardData):
        if rewardData is None:
            return
        else:
            if rewardType in (Type.SHARDS,
             Type.GOLD,
             Type.CREDITS,
             Type.PREMIUMPLUS):
                count = rewardData
            elif rewardType == Type.TOYS:
                count = sum((v.get('count', 0) for v in rewardData.itervalues()))
            elif rewardType == Type.VEHICLES:
                count = sum((v.get('compensatedNumber', 1) for r in rewardData for v in r.itervalues()))
            elif rewardType == Type.CUSTOMIZATIONS:
                count = len(rewardData)
            else:
                count = 0
            if not count:
                return
            reward = NyLootBoxStatisticsRewardModel()
            reward.setType(rewardType)
            reward.setCount(count)
            return reward
