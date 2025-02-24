# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/messenger/formatters/token_quest_subformatters.py
from comp7.gui.impl.lobby.comp7_helpers import comp7_quest_helpers
from comp7.gui.impl.lobby.comp7_helpers import comp7_shared, comp7_i18n_helpers
from comp7.messenger.formatters.service_channel import Comp7QualificationRewardsFormatter
from comp7_common_const import Comp7QuestType, qualificationQuestIDBySeasonNumber
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events.bonuses import getMergedBonusesFromDicts
from helpers import dependency
from helpers import time_utils
from messenger import g_settings
from messenger.formatters import TimeFormatter
from messenger.formatters.service_channel_helpers import MessageData
from messenger.formatters.token_quest_subformatters import SyncTokenQuestsSubFormatter
from skeletons.gui.game_control import IComp7Controller

class Comp7RewardsFormatter(SyncTokenQuestsSubFormatter):
    __PERIODIC_REWARD_MESSAGE_TEMPLATE = 'comp7PeriodicRewardMessage'
    __REGULAR_REWARD_MESSAGE_TEMPLATE = 'comp7RegularRewardMessage'
    __QUALIFICATION_REWARD_MESSAGE_TEMPLATE = 'comp7QualificationRewardMessage'
    __R_SYS_MESSAGES = R.strings.comp7_ext.system_messages
    __RANK_NAME_KEYS = ('sixth', 'fifth', 'fourth', 'third', 'second', 'first')
    __comp7Ctrl = dependency.descriptor(IComp7Controller)

    def __init__(self):
        super(Comp7RewardsFormatter, self).__init__()
        self.__questTypeFormatters = {Comp7QuestType.PERIODIC: self.__formatPeriodicRewardMessage,
         Comp7QuestType.RANKS: self.__formatRegularRewardMessage,
         Comp7QuestType.TOKENS: self.__formatTokensRewardMessage}

    def format(self, message, *_):
        if message.data:
            messageData = []
            settings = self._getGuiSettings(message)
            completedIDs = self.getQuestOfThisGroup(message.data.get('completedQuestIDs', set()))
            if self.__getQualificationQuestID() in completedIDs:
                formattedMessage = self.__formatQualificationRewardMessage(message, completedIDs)
                messageData.append(MessageData(formattedMessage, settings))
            for questID in completedIDs:
                questType = comp7_quest_helpers.getComp7QuestType(questID)
                formattedMessage = None
                formatter = self.__questTypeFormatters.get(questType)
                if formatter is not None:
                    formattedMessage = formatter(message, questID)
                if formattedMessage is not None:
                    messageData.append(MessageData(formattedMessage, settings))

            if messageData:
                return messageData
        return [MessageData(None, None)]

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        actualSeasonNumber = cls.__comp7Ctrl.getActualSeasonNumber()
        return comp7_quest_helpers.isComp7Quest(questID, actualSeasonNumber)

    def __formatPeriodicRewardMessage(self, message, questID):
        division = comp7_quest_helpers.parseComp7PeriodicQuestID(questID)
        rank = comp7_shared.getRankEnumValue(division)
        rewardsData = message.data.get('detailedRewards', {}).get(questID, {})
        if not rewardsData:
            return None
        else:
            formattedRewards = self._achievesFormatter.formatQuestAchieves(rewardsData, asBattleFormatter=False, processCustomizations=False, processTokens=False)
            formattedMessage = g_settings.msgTemplates.format(self.__PERIODIC_REWARD_MESSAGE_TEMPLATE, ctx={'title': backport.text(self.__R_SYS_MESSAGES.periodicReward.title()),
             'body': backport.text(self.__R_SYS_MESSAGES.periodicReward.body(), rank=comp7_i18n_helpers.getRankLocale(rank), rewards=formattedRewards)})
            return formattedMessage

    def __formatRegularRewardMessage(self, message, questID):
        rewardsData = message.data.get('detailedRewards', {}).get(questID, {})
        return self.__formatRegularMessage(message, rewardsData, 'regularReward')

    def __formatTokensRewardMessage(self, message, questID):
        rewardsData = message.data.get('detailedRewards', {}).get(questID, {})
        dossierData = rewardsData.get('dossier', {})
        popUpRecords = message.data.get('popUpRecords', set())
        popUps = self._getDossierPopUps(dossierData, popUpRecords)
        if popUps:
            rewardsData.update({'popUpRecords': popUps})
        return self.__formatRegularMessage(message, rewardsData, 'tokenWeeklyReward')

    def __formatRegularMessage(self, message, rewardsData, rewardType):
        if not rewardsData:
            return None
        else:
            formattedRewards = self._achievesFormatter.formatQuestAchieves(rewardsData, asBattleFormatter=False)
            return g_settings.msgTemplates.format(self.__REGULAR_REWARD_MESSAGE_TEMPLATE, ctx={'title': backport.text(self.__R_SYS_MESSAGES.dyn(rewardType).title()),
             'body': backport.text(self.__R_SYS_MESSAGES.dyn(rewardType).body(), at=TimeFormatter.getLongDatetimeFormat(time_utils.makeLocalServerTime(message.sentTime)), rewards=formattedRewards)})

    def __formatQualificationRewardMessage(self, message, questIDs):
        ranksQuests = set([ q for q in questIDs if comp7_quest_helpers.getComp7QuestType(q) == Comp7QuestType.RANKS ])
        questIDs -= ranksQuests
        sortedQuests = sorted(list(ranksQuests))
        detailedRewards = message.data.get('detailedRewards', {})
        mergedRewards = getMergedBonusesFromDicts([ detailedRewards.get(qID, {}) for qID in sortedQuests ])
        formattedRewards = Comp7QualificationRewardsFormatter.formatQuestAchieves(mergedRewards, False)
        rankNames = self.__getQualificationRanks(ranksQuests)
        return g_settings.msgTemplates.format(self.__QUALIFICATION_REWARD_MESSAGE_TEMPLATE, ctx={'title': backport.text(self.__R_SYS_MESSAGES.qualificationReward.title()),
         'body': backport.text(self.__R_SYS_MESSAGES.qualificationReward.body(), maxRank=rankNames[-1], ranks=backport.text(R.strings.comp7_ext.listSeparator()).join(rankNames), rewards=formattedRewards)})

    def __getQualificationRanks(self, quests):
        ranks = list({comp7_quest_helpers.parseComp7RanksQuestID(questID).rank for questID in quests})
        ranks.sort(reverse=True)
        return [ self.__getRankName(r) for r in ranks ]

    def __getRankName(self, rankIndex):
        rankKey = self.__RANK_NAME_KEYS[rankIndex - 1]
        return backport.text(R.strings.comp7_ext.rank.dyn(rankKey)())

    def __getQualificationQuestID(self):
        actualSeasonNumber = self.__comp7Ctrl.getActualSeasonNumber()
        return qualificationQuestIDBySeasonNumber(actualSeasonNumber) if actualSeasonNumber else None
