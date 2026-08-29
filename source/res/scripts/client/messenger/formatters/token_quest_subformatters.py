# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/formatters/token_quest_subformatters.py
import logging
import re
from itertools import chain
import typing
import constants
from adisp import adisp_async, adisp_process
from shared_utils import first
from helpers import dependency, time_utils
from account_helpers import AccountSettings
from account_helpers.AccountSettings import RANKED_YEAR_POSITION
from chat_shared import SYS_MESSAGE_TYPE
from dossiers2.custom.records import DB_ID_TO_RECORD, RECORD_DB_IDS
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK, BADGES_BLOCK
from gui.Scaleform.genConsts.RANKEDBATTLES_CONSTS import RANKEDBATTLES_CONSTS
from gui.impl import backport
from gui.impl.gen import R
from gui.ranked_battles import ranked_helpers
from gui.ranked_battles.constants import YEAR_POINTS_TOKEN, RankedDossierKeys
from gui.ranked_battles.ranked_helpers.web_season_provider import TOP_LEAGUE_ID, UNDEFINED_LEAGUE_ID
from gui.server_events.bonuses import getBonuses, getMergedBonusesFromDicts
from gui.server_events.events_helpers import getIdxFromQuestID, isACEmailConfirmationQuest
from gui.server_events.recruit_helper import getSourceIdFromQuest
from gui.shared.formatters import text_styles
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.money import Currency
from messenger import g_settings
from messenger.formatters import TimeFormatter
from messenger.formatters.service_channel import BattleMattersQuestAchievesFormatter, BattlePassQuestAchievesFormatter, CollectionsFormatter, InvoiceReceivedFormatter, QuestAchievesFormatter, RankedQuestAchievesFormatter, SeniorityAwardsQuestAchievesFormatter, ServiceChannelFormatter, WaitItemsSyncFormatter, WinbackQuestAchievesFormatter
from messenger.formatters.service_channel_helpers import EOL, MessageData, getCustomizationItemData, getRewardsForQuests, popCollectionEntitlements
from messenger.proto.bw.wrappers import ServiceChannelMessage
from skeletons.gui.battle_matters import IBattleMattersController
from skeletons.gui.game_control import ICollectionsSystemController, IRankedBattlesController, ISeniorityAwardsController, IWinbackController, IWotPlusController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.system_messages import ISystemMessages
_logger = logging.getLogger(__name__)

class ITokenQuestsSubFormatter(object):

    def getPopUps(self, message):
        pass

    @classmethod
    def getQuestOfThisGroup(cls, questIDs):
        pass

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        pass

    def _getDossierPopUps(self, dossierData, popUpRecords):
        pass


class TokenQuestsSubFormatter(ITokenQuestsSubFormatter):

    def getPopUps(self, message):
        data = message.data or {}
        questsPopUP = set()
        for achievesID, achievesCount in data.get('popUpRecords', set()):
            achievesRecord = DB_ID_TO_RECORD[achievesID]
            for questID, questData in data.get('detailedRewards', {}).iteritems():
                for dossierRecord in chain.from_iterable(questData.get('dossier', {}).values()):
                    if achievesRecord == dossierRecord and self._isQuestOfThisGroup(questID):
                        questsPopUP.add((achievesID, achievesCount))

        return questsPopUP

    def _getDossierPopUps(self, dossierData, popUpRecords):
        popUps = set()
        for dossierRecord in chain.from_iterable(dossierData.values()):
            if dossierRecord[0] in ACHIEVEMENT_BLOCK.ALL:
                achievementID = RECORD_DB_IDS.get(dossierRecord, None)
                popUps.update((popUp for popUp in popUpRecords if popUp[0] == achievementID))

        return popUps

    @classmethod
    def getQuestOfThisGroup(cls, questIDs):
        return set((quest for quest in questIDs if cls._isQuestOfThisGroup(quest)))


class AsyncTokenQuestsSubFormatter(WaitItemsSyncFormatter, TokenQuestsSubFormatter):

    def __init__(self):
        super(AsyncTokenQuestsSubFormatter, self).__init__()
        self._achievesFormatter = QuestAchievesFormatter()


class SyncTokenQuestsSubFormatter(ServiceChannelFormatter, TokenQuestsSubFormatter):

    def __init__(self):
        super(SyncTokenQuestsSubFormatter, self).__init__()
        self._achievesFormatter = QuestAchievesFormatter()


class RecruitQuestsFormatter(AsyncTokenQuestsSubFormatter):
    __eventsCache = dependency.descriptor(IEventsCache)
    __TEMPLATE_NAME = 'goldDataInvoiceReceived'

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        formatted, settings = (None, None)
        if isSynced:
            data = message.data or {}
            completedQuestIDs = self.getQuestOfThisGroup(data.get('completedQuestIDs', set()))
            questsData = getRewardsForQuests(message, self.getQuestOfThisGroup(completedQuestIDs))
            questsData['popUpRecords'] = self.getPopUps(message)
            fmt = self._achievesFormatter.formatQuestAchieves(questsData, asBattleFormatter=False)
            if fmt is not None:
                operationTime = message.sentTime
                if operationTime:
                    fDatetime = TimeFormatter.getLongDatetimeFormat(time_utils.makeLocalServerTime(operationTime))
                else:
                    fDatetime = 'N/A'
                formatted = g_settings.msgTemplates.format(self.__TEMPLATE_NAME, ctx={'at': fDatetime,
                 'desc': '',
                 'op': fmt})
                settings = self._getGuiSettings(message, self.__TEMPLATE_NAME)
        callback([MessageData(formatted, settings)])
        return

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return getSourceIdFromQuest(questID) is not None


class RankedTokenQuestFormatter(AsyncTokenQuestsSubFormatter):

    def __init__(self):
        super(RankedTokenQuestFormatter, self).__init__()
        self._achievesFormatter = RankedQuestAchievesFormatter()

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return ranked_helpers.isRankedQuestID(questID)


class RankedSeasonTokenQuestFormatter(RankedTokenQuestFormatter):
    __rankedController = dependency.descriptor(IRankedBattlesController)
    __eventsCache = dependency.descriptor(IEventsCache)
    __R_NOTIFICATIONS = R.strings.system_messages.ranked.notifications
    __seasonAwardsFormatters = (('badge', lambda b: b),
     ('badges', lambda b: b),
     ('style', lambda b: b),
     ('styles', lambda b: b))

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        if isSynced:
            completedQuestIDs = self.getQuestOfThisGroup(message.data.get('completedQuestIDs', set()))
            questsData = getRewardsForQuests(message, self.getQuestOfThisGroup(completedQuestIDs))
            messages = self.__formatTokenQuests(completedQuestIDs, questsData)
            callback([ MessageData(formattedMessage, self._getGuiSettings(message)) for formattedMessage in messages ])
        else:
            callback([MessageData(None, self._getGuiSettings(message))])
        return

    def getPopUps(self, message):
        return set()

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return ranked_helpers.isSeasonTokenQuest(questID) if super(RankedSeasonTokenQuestFormatter, cls)._isQuestOfThisGroup(questID) else False

    def __getRankedTokens(self, quest):
        result = 0
        for bonus in quest.getBonuses():
            value = bonus.getValue()
            if isinstance(value, dict):
                result += value.get(YEAR_POINTS_TOKEN, {}).get('count', 0)

        return result

    def __packSeasonExtra(self, data):
        extraAwards = dict()
        badges = self.__processBadges(data)
        if len(badges) > 1:
            extraAwards['badges'] = EOL.join(badges)
        elif badges:
            extraAwards['badge'] = badges[0]
        styles = self.__processStyles(data)
        if len(styles) > 1:
            extraAwards['styles'] = EOL.join(styles)
        elif styles:
            extraAwards['style'] = styles[0]
        return extraAwards

    def __processBadges(self, data):
        result = list()
        for block in data.get('dossier', {}).values():
            if isinstance(block, dict):
                for record in block.keys():
                    if record[0] == BADGES_BLOCK:
                        result.append(backport.text(R.strings.badge.dyn('badge_{}'.format(record[1]))()))

        return result

    def __processStyles(self, data):
        result = list()
        customizations = data.get('customizations', [])
        for customizationItem in customizations:
            customizationType = customizationItem['custType']
            _, itemUserName = getCustomizationItemData(customizationItem['id'], customizationType)
            if customizationType == 'style':
                result.append(itemUserName)

        return result

    def __formatTokenQuests(self, completedQuestIDs, data):
        formattedMessages = []
        quests = self.__eventsCache.getHiddenQuests()
        for questID in completedQuestIDs:
            quest = quests.get(questID)
            if quest is not None:
                seasonID, league, isSprinter = ranked_helpers.getDataFromSeasonTokenQuestID(questID)
                season = self.__rankedController.getSeason(seasonID)
                if season is not None:
                    isMastered = league != UNDEFINED_LEAGUE_ID
                    seasonProgress = self.__formatSeasonProgress(season, league, isSprinter, data)
                    extraAwards = self.__packSeasonExtra(data) if isMastered else {}
                    formattedMessages.append(g_settings.msgTemplates.format('rankedSeasonQuest', ctx={'title': backport.text(self.__R_NOTIFICATIONS.seasonResults(), seasonNumber=season.getUserName()),
                     'seasonProgress': seasonProgress,
                     'awardsBlock': self.__packSeasonAwards(extraAwards)}, data={'savedData': {'quest': quest,
                                   'awards': data}}))

        return formattedMessages

    def __formatSeasonProgress(self, season, league, isSprinter, data):
        webSeasonInfo = self.__rankedController.getWebSeasonProvider().seasonInfo
        if webSeasonInfo.league == UNDEFINED_LEAGUE_ID:
            webSeasonInfo = self.__rankedController.getClientSeasonInfo()
        resultStrings = []
        rankedQuests = self.__eventsCache.getRankedQuests(lambda q: q.isHidden() and q.isForRank() and q.getSeasonID() == season.getSeasonID() and q.isCompleted())
        rankedQuests = rankedQuests.values()
        if not rankedQuests:
            _logger.error("Ranked season quest completed, but ranked quest isn't completed or found!!!")
        dossier = self._itemsCache.items.getAccountDossier().getSeasonRankedStats(RankedDossierKeys.SEASON % season.getNumber(), season.getSeasonID())
        if league != UNDEFINED_LEAGUE_ID:
            position = 0
            if webSeasonInfo.league == league:
                position = webSeasonInfo.position
            leagueName = self.__R_NOTIFICATIONS.dyn('league{}'.format(league))()
            resultStrings.append(backport.text(self.__R_NOTIFICATIONS.league(), leagueName=text_styles.stats(backport.text(leagueName if leagueName else ''))))
            if position > 0:
                resultStrings.append(backport.text(self.__R_NOTIFICATIONS.position(), position=text_styles.stats(backport.getNiceNumberFormat(position))))
        else:
            rankID = dossier.getAchievedRank()
            division = self.__rankedController.getDivision(rankID)
            resultStrings.append(backport.text(self.__R_NOTIFICATIONS.maxRank(), result=text_styles.stats(backport.text(self.__R_NOTIFICATIONS.maxRankResult(), rankName=division.getRankUserName(rankID), divisionName=division.getUserName()))))
        if isSprinter:
            if league == TOP_LEAGUE_ID:
                sprinterTextID = self.__R_NOTIFICATIONS.sprinterTop()
            else:
                sprinterTextID = self.__R_NOTIFICATIONS.sprinterImproved()
            resultStrings.append(backport.text(sprinterTextID))
        tokens = data.get('tokens', None)
        tokenForLeague = self.__getTokensForLeague(tokens)
        if tokenForLeague > 0:
            resultStrings.append(backport.text(self.__R_NOTIFICATIONS.leaguePoints(), points=text_styles.stats(tokenForLeague)))
        seasonPoints = sum([ self.__getRankedTokens(quest) for quest in rankedQuests ]) + tokenForLeague
        if seasonPoints > 0:
            resultStrings.append(backport.text(self.__R_NOTIFICATIONS.seasonPoints(), points=text_styles.stats(seasonPoints)))
        return EOL.join(resultStrings)

    def __getTokensForLeague(self, tokens):
        tokenForLeague = 0
        if tokens is not None and YEAR_POINTS_TOKEN in tokens:
            yearTokens = tokens.get(YEAR_POINTS_TOKEN)
            tokenForLeague = yearTokens.get('count', 0)
        return tokenForLeague

    def __packSeasonAwards(self, awardsDict):
        result = list()
        if awardsDict:
            result.extend(self._achievesFormatter.packAwards(awardsDict, self.__seasonAwardsFormatters))
        return EOL.join(result)


class RankedFinalTokenQuestFormatter(RankedTokenQuestFormatter):
    __rankedController = dependency.descriptor(IRankedBattlesController)
    __MESSAGE_TEMPLATE_NAME = 'RankedFinalYearAwardQuest'
    __MESSAGE_TEMPLATE_WITHOUT_AWARDS_NAME = 'RankedFinalYearWithoutAwardQuest'
    __HTML_POINTS_TEMPLATE = 'rankedFinalYearPoints'
    __HTML_COMPENSATION_TEMPLATE = 'rankedFinalYearCompensation'

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        messageData = MessageData(None, None)
        if isSynced:
            data = message.data or {}
            completedQuestIDs = data.get('completedQuestIDs', set())
            finalQuests = self.getQuestOfThisGroup(completedQuestIDs)
            if not finalQuests:
                callback([messageData])
                return
            if len(finalQuests) > 1:
                _logger.error('There can not be 2 or more ranked final quests at the same time')
            questID = finalQuests.pop()
            points = ranked_helpers.getDataFromFinalTokenQuestID(questID)
            detailedRewards = data.get('detailedRewards', {})
            questData = detailedRewards.get(questID, {}).copy()
            pointsTemplate = self.__generatePointsTemplate(points, questData)
            awardType = self.__rankedController.getAwardTypeByPoints(points)
            if awardType is not None:
                fmt = self._achievesFormatter.formatQuestAchieves(questData, asBattleFormatter=False)
                rServiceChannelMessages = R.strings.messenger.serviceChannelMessages
                awardsTitle = rServiceChannelMessages.rankedFinaleAwardsNotification.dyn(awardType).awardsTitle()
                formatted = g_settings.msgTemplates.format(self.__MESSAGE_TEMPLATE_NAME, ctx={'pointsTemplate': pointsTemplate,
                 'awardsTitle': backport.text(awardsTitle) if awardsTitle else '',
                 'awardsBlock': fmt if fmt else ''}, data={'savedData': {'questID': questID,
                               'awards': detailedRewards.get(questID, {})}})
            else:
                formatted = g_settings.msgTemplates.format(self.__MESSAGE_TEMPLATE_WITHOUT_AWARDS_NAME, ctx={'pointsTemplate': pointsTemplate})
            messageData = MessageData(formatted, self._getGuiSettings(message))
        callback([messageData])
        return

    def getPopUps(self, message):
        return set()

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return ranked_helpers.isFinalTokenQuest(questID) if super(RankedFinalTokenQuestFormatter, cls)._isQuestOfThisGroup(questID) else False

    def __generatePointsTemplate(self, points, questData):
        surplusPoints = self.__rankedController.getCompensation(points)
        rate = self.__rankedController.getCurrentPointToCrystalRate()
        result = [g_settings.htmlTemplates.format(self.__HTML_POINTS_TEMPLATE, ctx={'points': points})]
        count = 0
        if surplusPoints and rate:
            count = surplusPoints * rate
            result.append(g_settings.htmlTemplates.format(self.__HTML_COMPENSATION_TEMPLATE, ctx={'surplusPoints': surplusPoints,
             'count': count}))
        if surplusPoints and rate and questData is not None:
            allCrystal = questData.get(Currency.CRYSTAL, 0)
            if allCrystal >= count:
                questData[Currency.CRYSTAL] = allCrystal - count
            else:
                _logger.error('Awards crystals less that compensated crystals')
                questData[Currency.CRYSTAL] = 0
        return '<br/>'.join(result)


class SeniorityAwardsFormatter(AsyncTokenQuestsSubFormatter):
    _MESSAGE_TEMPLATE = 'SeniorityAwardsQuest'
    _MESSAGE_TEMPLATE_WITH_SELECTION = 'SeniorityAwardsQuestWithSelection'
    _seniorityAwardCtrl = dependency.descriptor(ISeniorityAwardsController)

    def __init__(self):
        super(SeniorityAwardsFormatter, self).__init__()
        self._achievesFormatter = SeniorityAwardsQuestAchievesFormatter()

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        messageDataList = []
        if isSynced:
            data = message.data or {}
            completedQuestIDs = self.getQuestOfThisGroup(data.get('completedQuestIDs', set()))
            detailedRewards = data.get('detailedRewards', {})
            mergedRewards = getMergedBonusesFromDicts((detailedRewards.get(qID, {}) for qID in completedQuestIDs))
            messageData = self._buildMessage(mergedRewards, message)
            if messageData is not None:
                messageDataList.append(messageData)
        if messageDataList:
            callback(messageDataList)
        else:
            callback([MessageData(None, None)])
        return

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        questPrefix = cls._seniorityAwardCtrl.seniorityQuestPrefix
        return questID.startswith(questPrefix) if questPrefix else False

    def _buildMessage(self, rewards, message):
        data = message.data or {}
        questData = {}
        dossierData = rewards.get('dossier', {})
        popUpRecords = data.get('popUpRecords', set())
        popUps = self._getDossierPopUps(dossierData, popUpRecords)
        if popUps:
            questData['popUpRecords'] = popUps
        questData.update(rewards)
        fmt = self._achievesFormatter.formatQuestAchieves(questData, asBattleFormatter=False)
        if fmt is not None:
            templateParams = {'achieves': fmt}
            template = self._MESSAGE_TEMPLATE_WITH_SELECTION if self._seniorityAwardCtrl.isVehicleSelectionAvailable else self._MESSAGE_TEMPLATE
            settings = self._getGuiSettings(message, template)
            formatted = g_settings.msgTemplates.format(template, templateParams)
            return MessageData(formatted, settings)
        else:
            return


class SeniorityAwardsVehicleSelectedFormatter(SeniorityAwardsFormatter):

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        questPrefix = cls._seniorityAwardCtrl.vehicleSelectionQuestPrefix
        return questID.startswith(questPrefix) if questPrefix else False

    def _buildMessage(self, rewards, message):
        fmt = self._achievesFormatter.formatQuestAchieves(rewards, asBattleFormatter=False)
        if fmt is not None:
            templateParams = {'achieves': fmt}
            settings = self._getGuiSettings(message, self._MESSAGE_TEMPLATE)
            formatted = g_settings.msgTemplates.format(self._MESSAGE_TEMPLATE, templateParams)
            return MessageData(formatted, settings)
        else:
            return


class BattleMattersAwardsFormatterBase(ServiceChannelFormatter, TokenQuestsSubFormatter):
    __battleMattersController = dependency.descriptor(IBattleMattersController)
    __MESSAGE_TEMPLATE = 'BattleMatters{}'
    __TOKEN_TYPE = 'TokenQuest'
    __AWARD_TYPE = 'AwardsQuest'

    def __init__(self):
        super(BattleMattersAwardsFormatterBase, self).__init__()
        self._achievesFormatter = BattleMattersQuestAchievesFormatter()

    def _format(self, message, *args):
        messageDataList = []
        data = message.data or {}
        completedQuestIDs = sorted(self.getQuestOfThisGroup(data.get('completedQuestIDs', set())), key=getIdxFromQuestID)
        for qID in completedQuestIDs:
            messageData = self.__buildMessage(qID, message)
            if messageData is not None:
                messageDataList.append(messageData)

        return messageDataList if messageDataList else [MessageData(None, None)]

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return cls.__battleMattersController.isBattleMattersQuestID(questID)

    def __buildMessage(self, questID, message):
        data = message.data or {}
        isWithButton = self._achievesFormatter.isWithSelectableReward(data)
        rewards = data.get('detailedRewards', {}).get(questID, {})
        fmt = self._achievesFormatter.formatQuestAchieves(rewards, asBattleFormatter=False)
        if fmt is not None:
            questIdx = getIdxFromQuestID(questID)
            finalQuest = self.__battleMattersController.getFinalQuest()
            if finalQuest and finalQuest.getID() == questID:
                body = backport.text(R.strings.messenger.serviceChannelMessages.battleMatters.awards.done.body())
            elif self.__battleMattersController.isIntermediateBattleMattersQuestID(questID):
                body = backport.text(R.strings.messenger.serviceChannelMessages.battleMatters.awards.medium.body(), count=text_styles.stats(str(questIdx)))
            else:
                quest = self.__battleMattersController.getQuestByIdx(questIdx - 1)
                awardText = R.strings.messenger.serviceChannelMessages.battleMatters.awards
                body = backport.text(awardText.body(), questIdx=text_styles.stats(backport.text(awardText.questIdx(), questIdx=str(questIdx))), questName=text_styles.stats(quest.getUserName() if quest else ''))
            templateParams = {'achieves': fmt or '',
             'body': body}
            template = self.__MESSAGE_TEMPLATE.format(self.__TOKEN_TYPE if isWithButton else self.__AWARD_TYPE)
            settings = self._getGuiSettings(message, template)
            formatted = g_settings.msgTemplates.format(template, templateParams)
            return MessageData(formatted, settings)
        else:
            return


class BattleMattersAwardsFormatter(AsyncTokenQuestsSubFormatter, BattleMattersAwardsFormatterBase):

    def __init__(self):
        AsyncTokenQuestsSubFormatter.__init__(self)
        BattleMattersAwardsFormatterBase.__init__(self)

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        messageDataList = []
        if isSynced:
            messageDataList = self._format(message)
        if messageDataList:
            callback(messageDataList)
        callback([MessageData(None, None)])
        return


class BattleMattersClientAwardsFormatter(BattleMattersAwardsFormatterBase):

    def format(self, message, *args):
        return self._format(message, *args)


class LootBoxTokenQuestFormatter(AsyncTokenQuestsSubFormatter):
    __TEMPLATE_NAME = 'tokenQuestLootbox'

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        result = yield InvoiceReceivedFormatter().format(self.__getInvoiceFormatMessage(message))
        callback(result)

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return cls.__TEMPLATE_NAME in questID

    def __getInvoiceFormatMessage(self, message):
        data = {'active': message.active,
         'createdAt': message.createdAt,
         'finishedAt': message.finishedAt,
         'importance': message.importance,
         'isHighImportance': message.isHighImportance,
         'messageId': message.messageId,
         'personal': message.personal,
         'sentTime': message.sentTime,
         'startedAt': message.startedAt,
         'type': message.type,
         'userId': message.userId,
         'data': {'data': {'assetType': constants.INVOICE_ASSET.DATA,
                           'at': message.sentTime,
                           'data': message.data}}}
        return ServiceChannelMessage.fromChatAction(data, message.personal)


class BattlePassDefaultAwardsFormatter(WaitItemsSyncFormatter, TokenQuestsSubFormatter):
    __MESSAGE_TEMPLATE = 'BattlePassDefaultRewardMessage'
    __COLLECTION_ITEMS_TEMPLATE = 'CollectionItemsSysMessage'
    __BATTLE_PASS_TOKEN_QUEST_PATTERN = 'battle_pass'
    __collectionsSystem = dependency.descriptor(ICollectionsSystemController)

    def __init__(self):
        super(BattlePassDefaultAwardsFormatter, self).__init__()
        self._achievesFormatter = BattlePassQuestAchievesFormatter()

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        messageDataList = []
        if isSynced:
            data = message.data or {}
            completedQuestIDs = self.getQuestOfThisGroup(data.get('completedQuestIDs', set()))
            for qID in completedQuestIDs:
                messageData = self.__buildMessage(qID, message)
                if messageData:
                    messageDataList.extend(messageData)

        if messageDataList:
            callback(messageDataList)
        callback([MessageData(None, None)])
        return

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return cls.__BATTLE_PASS_TOKEN_QUEST_PATTERN in questID

    def __buildMessage(self, questID, message):
        result = []
        data = message.data or {}
        questData = {}
        rewards = data.get('detailedRewards', {}).get(questID, {})
        collectionEntitlements = popCollectionEntitlements(rewards)
        questData.update(rewards)
        header = backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.header.voted())
        fmt = self._achievesFormatter.formatQuestAchieves(questData, asBattleFormatter=False)
        if fmt is not None:
            templateParams = {'text': fmt,
             'header': header}
            settings = self._getGuiSettings(message, self.__MESSAGE_TEMPLATE)
            settings.priorityLevel = NotificationPriorityLevel.LOW
            formatted = g_settings.msgTemplates.format(self.__MESSAGE_TEMPLATE, templateParams)
            result.append(MessageData(formatted, settings))
        if collectionEntitlements and self.__collectionsSystem.isEnabled():
            result.append(self.__makeCollectionMessage(collectionEntitlements, message))
        return result

    def __makeCollectionMessage(self, entitlements, message):
        messages = R.strings.collections.notifications
        collectionID = int(first(entitlements).split('_')[-2])
        collection = self.__collectionsSystem.getCollection(collectionID).name
        feature = backport.text(messages.feature.dyn(collection)())
        season = backport.text(messages.season.dyn(collection)())
        title = backport.text(messages.title.collectionName(), feature=feature, season=season)
        text = backport.text(messages.newItemsReceived.text(), items=CollectionsFormatter.formatQuestAchieves({'entitlements': entitlements}, False))
        formatted = g_settings.msgTemplates.format(self.__COLLECTION_ITEMS_TEMPLATE, ctx={'title': title,
         'text': text}, data={'savedData': {'collectionId': collectionID}})
        return MessageData(formatted, self._getGuiSettings(message, self.__COLLECTION_ITEMS_TEMPLATE, messageType=SYS_MESSAGE_TYPE.collectionsItems.index()))


class BattlePassAutoSelectRewardsFormatter(WaitItemsSyncFormatter, TokenQuestsSubFormatter):
    __MESSAGE_TEMPLATE = 'BattlePassDefaultRewardMessage'
    __BATTLE_PASS_AUTOSELECT_TOKEN_QUEST_PREFIX = 'bp_autoselect'

    def __init__(self):
        super(BattlePassAutoSelectRewardsFormatter, self).__init__()
        self._achievesFormatter = BattlePassQuestAchievesFormatter()

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        if isSynced:
            data = message.data or {}
            completedQuestIDs = self.getQuestOfThisGroup(data.get('completedQuestIDs', set()))
            messageData = self.__buildMessage(completedQuestIDs, message)
            if messageData:
                callback(messageData)
        callback([MessageData(None, None)])
        return

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return questID.startswith(cls.__BATTLE_PASS_AUTOSELECT_TOKEN_QUEST_PREFIX)

    def __buildMessage(self, questIDs, message):
        result = []
        data = message.data or {}
        detailedRewards = data.get('detailedRewards') or {}
        mergedRewards = getMergedBonusesFromDicts((detailedRewards.get(qID, {}) for qID in questIDs))
        header = backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.header.autoSelectReward())
        fmt = self._achievesFormatter.formatQuestAchieves(mergedRewards, asBattleFormatter=False)
        if fmt is not None:
            templateParams = {'text': fmt,
             'header': header}
            settings = self._getGuiSettings(message, self.__MESSAGE_TEMPLATE)
            formatted = g_settings.msgTemplates.format(self.__MESSAGE_TEMPLATE, templateParams)
            result.append(MessageData(formatted, settings))
        return result


class RankedYearLeaderFormatter(RankedTokenQuestFormatter):

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        formattedMessage = None
        if isSynced:
            yearPosition = AccountSettings.getSettings(RANKED_YEAR_POSITION)
            completedIDs = message.data.get('completedQuestIDs', set())
            rewardsData = getRewardsForQuests(message, self.getQuestOfThisGroup(completedIDs))
            if yearPosition is not None and rewardsData:
                formattedMessage = self.__formatFullMessage(yearPosition, rewardsData)
            else:
                formattedMessage = self.__formatShortMessage()
        callback([MessageData(formattedMessage, self._getGuiSettings(message))])
        return

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return ranked_helpers.isLeaderTokenQuest(questID)

    def __formatFullMessage(self, yearPosition, rewardsData):
        return g_settings.msgTemplates.format('rankedLeaderPositiveQuest', ctx={'title': backport.text(R.strings.system_messages.ranked.notification.yearLB.positive.title()),
         'body': backport.text(R.strings.system_messages.ranked.notification.yearLB.positive.body(), playerPosition=text_styles.stats(str(yearPosition)))}, data={'savedData': {'yearPosition': yearPosition,
                       'rewardsData': rewardsData}})

    def __formatShortMessage(self):
        return g_settings.msgTemplates.format('rankedLeaderNegativeQuest', ctx={'title': backport.text(R.strings.system_messages.ranked.notification.yearLB.negative.title()),
         'body': backport.text(R.strings.system_messages.ranked.notification.yearLB.negative.body())}, data={'savedData': {'ctx': {'selectedItemID': RANKEDBATTLES_CONSTS.RANKED_BATTLES_YEAR_RATING_ID}}})


class WotPlusAttendanceRewardsFormatter(SyncTokenQuestsSubFormatter):
    __systemMessages = dependency.descriptor(ISystemMessages)
    __wotPlusCtrl = dependency.descriptor(IWotPlusController)
    __eventsCache = dependency.descriptor(IEventsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    _STEP_PREFIX = 'step'
    _BIG_TEMPLATE = 'WotPlusAttendanceRewardsBig'
    _BIG_TEMPLATE_LVL_1 = 'WotPlusAttendanceRewardsBigLvl1'
    _SMALL_TEMPLATE = 'WotPlusAttendanceRewardsSmall'
    _STEP_DAILY_ATTENDANCE = re.compile('attendance_reward:step_(\\d)+')
    _WOT_PLUS_CONST = constants.WoTPlusDailyAttendance

    def format(self, message, *args):
        if not message:
            return []
        else:
            formattedUiRewards = self._collectDailyAttendanceBonuses(message)
            if not formattedUiRewards:
                return []
            self.__wotPlusCtrl.onDailyAttendanceUpdate()
            messageDataList = []
            for reward in formattedUiRewards:
                if reward.get('smallRewardData'):
                    formattedMessage = self.__getSmallRewardData(reward)
                elif reward.get('bigRewardData'):
                    formattedMessage = self.__getBigRewardData(reward)
                else:
                    _logger.error("Either 'smallRewardData' or 'bigRewardData' must be passed in the data!")
                    continue
                messageDataList.append(MessageData(formattedMessage, self._getGuiSettings(reward, None)))

            return messageDataList

    def _collectDailyAttendanceBonuses(self, message):
        allQuests = self.__eventsCache.getAllQuests(lambda q: self._isQuestOfThisGroup(q.getID()))
        detailedRewards = message.data.get('detailedRewards', {})
        formattedUiRewards = []
        for questID in detailedRewards:
            if self._isQuestOfThisGroup(questID):
                uiReward = {}
                currentQuest = allQuests[questID]
                level, isInitQuest = self.__getNotificationType(questID)
                uiReward['level'] = level
                questDataRewards = detailedRewards[questID]
                if isInitQuest or level not in range(self._WOT_PLUS_CONST.INITIAL_CYCLE_STEP, self._WOT_PLUS_CONST.CYCLE_STEPS):
                    questBonuses = [ getBonuses(currentQuest, bonusName, questDataRewards[bonusName], ctx={'isPacked': True}) for bonusName in questDataRewards ]
                    chainedBonuses = chain.from_iterable(questBonuses)
                    bonuses = [ bonus for bonus in chainedBonuses if bonus.getName() != 'battleToken' ]
                    uiReward['bigRewardData'] = self.__wotPlusCtrl.getFormattedDailyAttendanceBonuses(bonuses)
                else:
                    uiReward['smallRewardData'] = self._achievesFormatter.getFormattedAchieves(questDataRewards, False, processTokens=False)
                formattedUiRewards.append(uiReward)

        return formattedUiRewards

    def __getSmallRewardData(self, formattedUiRewards):
        descrs = []
        for descr in formattedUiRewards['smallRewardData']:
            descrs.append('{}<br/>'.format(descr))

        return g_settings.msgTemplates.format(self._SMALL_TEMPLATE, ctx={'rewards': ''.join(descrs)}, bgIconSource='{}{}'.format(self._STEP_PREFIX, formattedUiRewards['level']))

    def __getBigRewardData(self, formattedUiRewards):
        r = R.strings.messenger.serviceChannelMessages.wotPlus.dailyAttendanceRewarded.big
        startText = backport.text(r.cycleEnded.startText())
        endText = backport.text(r.cycleEnded.endText())
        bigTemplateName = self._BIG_TEMPLATE
        if formattedUiRewards['level'] == self._WOT_PLUS_CONST.INITIAL_CYCLE_STEP:
            startText = backport.text(r.cycleStarted.startText())
            endText = backport.text(r.cycleStarted.endText())
            bigTemplateName = self._BIG_TEMPLATE_LVL_1
        endTextFormatted = g_settings.htmlTemplates.format('wotPlusSimpleText', ctx={'text': endText})
        return g_settings.msgTemplates.format(bigTemplateName, ctx={'startText': startText}, bgIconSource='{}{}'.format(self._STEP_PREFIX, formattedUiRewards['level']), data={'linkageData': {'endText': endTextFormatted,
                         'rewards': formattedUiRewards['bigRewardData']}})

    def __getNotificationType(self, questID):
        matchObject = self._STEP_DAILY_ATTENDANCE.search(questID)
        return (int(matchObject.group(1)), False) if matchObject else (self._WOT_PLUS_CONST.INITIAL_CYCLE_STEP, True)

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return cls.__wotPlusCtrl.isDailyAttendanceQuest(questID)


class WotPlusAttendanceRewardsFormatterTestSMViewer(WotPlusAttendanceRewardsFormatter):

    def _collectDailyAttendanceBonuses(self, message):
        data = message.data
        return [{'level': data['level'],
          'bigRewardData': data['complexData'],
          'smallRewardData': data['textDataList']}]

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return questID == 'test_attendance_reward'


class WinbackRewardFormatterBase(ServiceChannelFormatter, TokenQuestsSubFormatter):
    __MESSAGE_TEMPLATE = 'Winback{}Award'
    __TOKEN_TYPE = 'SelectableToken'
    __AWARD_TYPE = 'Quest'
    __SIMPLE = 'Simple'
    _winbackController = dependency.descriptor(IWinbackController)

    def __init__(self):
        super(WinbackRewardFormatterBase, self).__init__()
        self._achievesFormatter = WinbackQuestAchievesFormatter()

    def _format(self, message, *args):
        messageDataList = []
        data = message.data or {}
        completedQuestIDs = self.getQuestOfThisGroup(data.get('completedQuestIDs', set()))
        for qID in completedQuestIDs:
            messageData = self.__buildMessage(qID, message)
            if messageData is not None:
                messageDataList.append(messageData)

        return messageDataList if messageDataList else [MessageData(None, None)]

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return cls._winbackController.isWinbackQuest(questID)

    def __buildMessage(self, questID, message):
        data = message.data or {}
        rewards = data.get('detailedRewards', {}).get(questID, {})
        isWithButton = bool(self._achievesFormatter.getSelectableRewards(rewards))
        fmt = self._achievesFormatter.formatQuestAchieves(rewards, asBattleFormatter=False)
        if fmt is not None:
            templateParams = {'achieves': fmt or ''}
            questType = self.__AWARD_TYPE
            if self._winbackController.getQuestIdx(questID) < 0:
                questType = self.__SIMPLE
            elif isWithButton:
                questType = self.__TOKEN_TYPE
            template = self.__MESSAGE_TEMPLATE.format(questType)
            settings = self._getGuiSettings(message, template)
            formatted = g_settings.msgTemplates.format(template, templateParams)
            return MessageData(formatted, settings)
        else:
            return


class WinbackRewardFormatter(AsyncTokenQuestsSubFormatter, WinbackRewardFormatterBase):

    def __init__(self):
        AsyncTokenQuestsSubFormatter.__init__(self)
        WinbackRewardFormatterBase.__init__(self)

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        messageDataList = []
        if isSynced:
            messageDataList = self._format(message)
        if messageDataList:
            callback(messageDataList)
        callback([MessageData(None, None)])
        return


class WinbackClientRewardFormatter(WinbackRewardFormatterBase):

    def format(self, message, *args):
        return self._format(message, *args)


class CrewPerksFormatter(AsyncTokenQuestsSubFormatter):
    __MESSAGE_TEMPLATE = 'SimpleGiftSysMessage'
    __QUEST_PREFIX = 'Crew22_'

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        messageData = MessageData(None, None)
        if isSynced:
            data = message.data or {}
            dataQuestIDs = data.get('completedQuestIDs', set())
            dataQuestIDs.update(data.get('rewardsGottenQuestIDs', set()))
            completedQuestIDs = self.getQuestOfThisGroup(dataQuestIDs)
            questsData = getRewardsForQuests(message, self.getQuestOfThisGroup(completedQuestIDs))
            formattedRewards = self._achievesFormatter.formatQuestAchieves(questsData, asBattleFormatter=False, processCustomizations=True, processTokens=True)
            formattedMessage = g_settings.msgTemplates.format(self.__MESSAGE_TEMPLATE, {'text': formattedRewards})
            settings = self._getGuiSettings(message, self.__MESSAGE_TEMPLATE)
            messageData = MessageData(formattedMessage, settings)
        callback([messageData])
        return

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return questID.startswith(cls.__QUEST_PREFIX)


class SteamCompletionFormatter(AsyncTokenQuestsSubFormatter):
    __MESSAGE_TEMPLATE = 'SteamEmailCompletionAward'

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        messageDataList = []
        if isSynced:
            data = message.data or {}
            completedQuestID = first(self.getQuestOfThisGroup(data.get('completedQuestIDs', set())))
            detailedRewards = data.get('detailedRewards', {}).get(completedQuestID, {})
            messageData = self.__buildMessage(detailedRewards, message)
            if messageData is not None:
                messageDataList.append(messageData)
        if messageDataList:
            callback(messageDataList)
        else:
            callback([MessageData(None, None)])
        return

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return isACEmailConfirmationQuest(questID)

    def __buildMessage(self, rewards, message):
        fmt = self._achievesFormatter.formatQuestAchieves(rewards, asBattleFormatter=False)
        if fmt is not None:
            templateParams = {'achieves': fmt}
            settings = self._getGuiSettings(message, self.__MESSAGE_TEMPLATE)
            formatted = g_settings.msgTemplates.format(self.__MESSAGE_TEMPLATE, templateParams)
            return MessageData(formatted, settings)
        else:
            return


class SkipNotificationFormatter(ServiceChannelFormatter, TokenQuestsSubFormatter):
    __NOTIFICATION_QUEST_POSTFIX = '_skip_notification'

    def format(self, message, *args):
        return [MessageData(None, None)]

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return questID.endswith(cls.__NOTIFICATION_QUEST_POSTFIX)
