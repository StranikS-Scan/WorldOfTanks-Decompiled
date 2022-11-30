# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ny_common/GuestsQuestsConfig.py
from typing import Optional, Dict, Callable, List
from ny_common.settings import GuestsQuestsConsts

class GuestsQuestsConfig(object):
    __slots__ = ('_config',)

    def __init__(self, config):
        self._config = config

    def getQuestsByGuest(self, guestName):
        quests = self._config.get(guestName, None)
        return None if quests is None else GuestQuests(quests)

    def getCompletedQuestsByGuest(self, guestName, lastCompletedQuestIndex):
        completedQuests = []
        quests = self.getQuestsByGuest(guestName)
        if quests:
            for questIndex, quest in enumerate(quests.getQuests()):
                if questIndex > lastCompletedQuestIndex:
                    break
                completedQuests.append(quest.getRawQuest())

        return completedQuests


class GuestQuests(object):
    __slots__ = ('_quests',)

    def __init__(self, quests):
        self._quests = quests

    def getQuests(self):
        return map(GuestQuest, self._quests)

    def getQuestByQuestID(self, questID):
        for quest in self.getQuests():
            if questID == quest.getQuestID():
                return quest

        return None

    def getQuestByQuestIndex(self, questIndex):
        quests = self.getQuests()
        return quests[questIndex] if 0 <= questIndex < len(quests) else None


class GuestQuest(object):
    __slots__ = ('_quest',)

    def __init__(self, quest):
        self._quest = quest

    def getRawQuest(self):
        return self._quest

    def getQuestID(self):
        return self._quest.get(GuestsQuestsConsts.QUEST_ID, None)

    def getQuestPrice(self):
        return self._quest.get(GuestsQuestsConsts.QUEST_PRICE, None)

    def getQuestRewards(self):
        return self._quest.get(GuestsQuestsConsts.QUEST_REWARDS, None)

    def getQuestTokensRewards(self, checker=None):
        rewards = self.getQuestRewards()
        checker = checker if checker else (lambda t: True)
        tokens = rewards.get(GuestsQuestsConsts.TOKENS, {})
        return {tokenID:value for tokenID, value in tokens.iteritems() if checker(tokenID)}

    def getQuestDependencies(self):
        return self._quest.get(GuestsQuestsConsts.QUEST_DEPENDENCIES, None)

    def isQuestAvailable(self, dependenciesChecker):
        dependencies = self.getQuestDependencies()
        return True if dependencies is None else dependenciesChecker(dependencies)
