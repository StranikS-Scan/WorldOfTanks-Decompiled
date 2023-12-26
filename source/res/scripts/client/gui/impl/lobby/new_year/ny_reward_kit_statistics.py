# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/ny_reward_kit_statistics.py
from helpers import dependency
from account_helpers.settings_core.settings_constants import NewYearStorageKeys
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.lobby_context import ILobbyContext
from gui import SystemMessages
from skeletons.gui.shared import IItemsCache
from gui.impl.lobby.loot_box.loot_box_helper import getLootboxStatisticsKey
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from new_year.ny_processor import ResetLootboxStatisticsProcessor
from gui.shared.utils import decorators
from gui.shared.notifications import NotificationPriorityLevel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_resource_model import NyResourceModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_reward_kit_statistics_reward_model import NyRewardKitStatisticsRewardModel, Type
from items.vehicles import getItemByCompactDescr
from new_year.ny_constants import GuestsQuestsTokens, RESOURCES_ORDER
from items.components.ny_constants import CurrentNYConstants
_REWARD_ORDER = (Type.VEHICLES,
 Type.CUSTOMIZATIONS,
 Type.MODERNIZEDEQUIPMENT,
 Type.NYTOYS,
 Type.GUESTC,
 Type.PREMIUMPLUS,
 Type.GOLD,
 Type.CREDITS)

class NyRewardKitStatistics(object):
    __itemsCache = dependency.descriptor(IItemsCache)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def updateLastSeen(self):
        self.__settingsCore.serverSettings.saveInNewYearStorage({NewYearStorageKeys.NY_STATISTICS_HINT_SHOWN: True})

    def updateStatistics(self, model, lootboxID, lastStatisticsResetFailed):
        rewardsData, boxesCount = self.getStatistics(lootboxID)
        model.setCount(boxesCount)
        model.setIsResetFailed(lastStatisticsResetFailed)
        self.updateRewards(model, rewardsData)
        self.updateCurrencies(model, rewardsData)

    def getStatistics(self, lootboxID):
        rewardsData, boxesCount = {}, 0
        statsKey = getLootboxStatisticsKey(lootboxID)
        return (rewardsData, boxesCount) if statsKey is None else self.__itemsCache.items.tokens.getLootBoxesStats().get(statsKey, (rewardsData, boxesCount))

    def updateRewards(self, model, rewardsData):
        rewards = model.getRewards()
        rewards.clear()
        for rewardType in _REWARD_ORDER:
            if rewardType == Type.GUESTC:
                tokens = rewardsData.get('tokens')
                if tokens is not None:
                    rewardData = tokens.get(GuestsQuestsTokens.TOKEN_CAT)
            elif rewardType == Type.MODERNIZEDEQUIPMENT:
                rewardData = rewardsData.get('items')
            elif rewardType == Type.NYTOYS:
                rewardData = rewardsData.get(CurrentNYConstants.TOYS)
            else:
                rewardData = rewardsData.get(rewardType.value)
            reward = self.getRewardModel(rewardType, rewardData)
            if reward is not None:
                rewards.addViewModel(reward)

        rewards.invalidate()
        return

    def updateCurrencies(self, model, resourcesData):
        totalCount = 0
        resources = model.getResources()
        resources.clear()
        resourceData = resourcesData.get(Type.CURRENCIES.value)
        for resourceType in RESOURCES_ORDER:
            resourceModel = self.getResourceModel(resourceType.value, resourceData)
            if resourceModel is not None:
                totalCount += resourceModel.getValue()
                resources.addViewModel(resourceModel)

        resources.invalidate()
        model.setTotalResourcesCount(totalCount)
        return

    @staticmethod
    def getResourceModel(resourceType, resourceData):
        if resourceData is None:
            return
        else:
            currentResourceData = resourceData.get(resourceType)
            resource = NyResourceModel()
            resource.setType(resourceType)
            if currentResourceData is None:
                resource.setValue(0)
            else:
                resource.setValue(currentResourceData.get('count'))
            return resource

    @staticmethod
    def getRewardModel(rewardType, rewardData):
        count = 0
        if rewardData is None:
            return
        else:
            if rewardType in (Type.GOLD, Type.CREDITS, Type.PREMIUMPLUS):
                count = rewardData
            elif rewardType == Type.VEHICLES:
                count = sum((v.get('compensatedNumber', 1) for r in rewardData for v in r.itervalues()))
            elif rewardType == Type.CUSTOMIZATIONS:
                count = len(rewardData)
            elif rewardType == Type.GUESTC:
                count = 1
            elif rewardType == Type.MODERNIZEDEQUIPMENT:
                count = 0
                for item in rewardData:
                    if getItemByCompactDescr(item).isModernized:
                        count += rewardData.get(item, 0)

            elif rewardType == Type.NYTOYS:
                count = sum((toysCount for toysData in rewardData.itervalues() for toysCount in toysData.itervalues()))
            if not count:
                return
            reward = NyRewardKitStatisticsRewardModel()
            reward.setType(rewardType)
            reward.setCount(count)
            return reward

    @decorators.adisp_process('newYear/resetLootboxStatistics')
    def resetStatistics(self, boxID):
        result = yield ResetLootboxStatisticsProcessor(boxID).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType, priority=NotificationPriorityLevel.MEDIUM)
        g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.ON_STATISTICS_RESET, {'serverError': not result.success and bool(result.userMsg)}), EVENT_BUS_SCOPE.LOBBY)
