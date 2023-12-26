# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_piggy_bank_helper.py
import typing
from typing import List, Set
from helpers import dependency
from ny_common.settings import GuestsQuestsConsts
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from ny_common.NYPiggyBankConfig import NYPiggyBankConfig
_COLLECTION_TOKEN = 'ny_piggy_bank_resource_collecting'

@dependency.replace_none_kwargs(lobbyCtx=ILobbyContext, itemsCache=IItemsCache, eventsCache=IEventsCache)
def getPiggyBankStatus(lobbyCtx=None, itemsCache=None, eventsCache=None):
    config = lobbyCtx.getServerSettings().getNewYearPiggyBank()
    configItem = config.getItemByIndex(0)
    piggyBankProgressToken = configItem.getDependencies().get('token', {}).keys()[0]
    if not piggyBankProgressToken:
        return (None, None, None, None)
    else:
        hiddenQuests = eventsCache.getHiddenQuests()
        completedQuestsCount = 0
        maxProgressValue = 0
        receivedRewardsCount = 0
        tokenCount = itemsCache.items.tokens.getTokenCount(piggyBankProgressToken)
        for configItem in config.getItems():
            conditions = configItem.getDependencies().get('token', {}).values()
            rewardsTokenQuest = None
            if conditions:
                maxProgressValue = max(maxProgressValue, conditions[0])
                rewardTokens = configItem.getRewards().get('tokens', {})
                if rewardTokens:
                    rewardsTokenQuest = hiddenQuests.get(rewardTokens.keys()[0])
            if rewardsTokenQuest and rewardsTokenQuest.isCompleted():
                receivedRewardsCount += 1
            if tokenCount >= conditions[0]:
                completedQuestsCount += 1

        return (tokenCount,
         completedQuestsCount,
         receivedRewardsCount,
         maxProgressValue)


class PiggyBankConfigHelper(object):
    __slots__ = ()

    @staticmethod
    @dependency.replace_none_kwargs(lobbyCtx=ILobbyContext)
    def getNYGuestsQuestsConfig(lobbyCtx=None):
        return lobbyCtx.getServerSettings().getNewYearPiggyBank()

    @classmethod
    def getTokensRewardsIDs(cls):
        tokens = []
        config = cls.getNYGuestsQuestsConfig()
        for item in config.getItems():
            rewards = item.getRewards() or {}
            tokens.extend(rewards.get(GuestsQuestsConsts.TOKENS, {}).keys())

        return tokens

    @classmethod
    def questsFilter(cls, quests):
        return quests & set(cls.getTokensRewardsIDs())

    @classmethod
    def getMaxCollectingResources(cls, questsTokens):
        collectings = []
        config = cls.getNYGuestsQuestsConfig()
        for item in config.getItems():
            rewards = item.getRewards() or {}
            tokens = set(rewards.get(GuestsQuestsConsts.TOKENS, {}).keys()) & questsTokens
            if not tokens:
                continue
            dependencies = item.getDependencies() or {}
            dependenciesTokens = dependencies.get(GuestsQuestsConsts.TOKEN, {})
            collectings.append(dependenciesTokens.get(_COLLECTION_TOKEN, 0))

        return max(collectings)
