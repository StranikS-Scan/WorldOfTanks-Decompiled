# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/formatters/token_quest_subformatters.py
import logging
import re
from collections import defaultdict
import typing
from itertools import chain
import constants
import personal_missions
from adisp import adisp_async, adisp_process
from account_helpers import AccountSettings
from account_helpers.AccountSettings import RANKED_YEAR_POSITION
from comp7_common import Comp7QuestType
from dossiers2.custom.records import DB_ID_TO_RECORD, RECORD_DB_IDS
from dossiers2.ui.achievements import BADGES_BLOCK, ACHIEVEMENT_BLOCK
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.comp7 import comp7_quest_helpers, comp7_shared
from gui.ranked_battles import ranked_helpers
from gui.ranked_battles.constants import RankedDossierKeys, YEAR_POINTS_TOKEN
from gui.ranked_battles.ranked_helpers.web_season_provider import UNDEFINED_LEAGUE_ID, TOP_LEAGUE_ID
from gui.Scaleform.genConsts.RANKEDBATTLES_CONSTS import RANKEDBATTLES_CONSTS
from gui.server_events.bonuses import getMergedBonusesFromDicts
from gui.server_events.events_helpers import getIdxFromQuestID
from gui.server_events.events_constants import CELEBRITY_MARATHON_PREFIX, CELEBRITY_QUESTS_PREFIX, NY_PIGGY_BANK_MARATHON_PREFIX
from gui.server_events.recruit_helper import getSourceIdFromQuest
from gui.shared.formatters import text_styles
from gui.shared.money import Currency
from gui.shared.notifications import NotificationPriorityLevel
from messenger import g_settings
from messenger.formatters import TimeFormatter
from messenger.formatters.service_channel import WaitItemsSyncFormatter, QuestAchievesFormatter, RankedQuestAchievesFormatter, ServiceChannelFormatter, PersonalMissionsQuestAchievesFormatter, BattlePassQuestAchievesFormatter, InvoiceReceivedFormatter, BattleResultsFormatter, NewYearCollectionFormatter, BattleMattersQuestAchievesFormatter, NewYearAchievesFormatter
from messenger.formatters.service_channel_helpers import getRewardsForQuests, EOL, MessageData, getCustomizationItemData, getDefaultMessage, DEFAULT_MESSAGE
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from messenger.proto.bw.wrappers import ServiceChannelMessage
from new_year.ny_constants import NY_COLLECTION_PREFIXES, NY_LEVEL_PREFIX, NY_COLLECTION_MEGA_PREFIX, NY_OLD_COLLECTION_PREFIX
from shared_utils import findFirst, first
from skeletons.gui.battle_matters import IBattleMattersController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.game_control import IRankedBattlesController, ISeniorityAwardsController
from helpers import dependency
from helpers import time_utils
from skeletons.new_year import INewYearController
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


class PersonalMissionsTokenQuestsFormatter(AsyncTokenQuestsSubFormatter):
    _DEFAULT_TEMPLATE = 'tokenQuests'
    __eventsCache = dependency.descriptor(IEventsCache)
    __PERSONAL_MISSIONS_CUSTOM_TEMPLATE = 'personalMissionsCustom'
    __PM_TOKEN_QUEST_PATTERNS = 'pt_final_s(\\d)_t(\\d)|pt_s(\\d)_t(\\d)_c(\\d)_add_reward|pt_final_badge_s(\\d)'
    __REGEX_PATTERN_BADGE = 'pt_final_s(\\d)_t(\\d)_badge'
    __TOKENS_NAME = (constants.PERSONAL_MISSION_FREE_TOKEN_NAME, constants.PERSONAL_MISSION_2_FREE_TOKEN_NAME)

    def __init__(self):
        super(PersonalMissionsTokenQuestsFormatter, self).__init__()
        self._achievesFormatter = PersonalMissionsQuestAchievesFormatter()

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        messageDataList = []
        templateName = self._DEFAULT_TEMPLATE
        if isSynced:
            data = message.data or {}
            dataQuestIDs = data.get('completedQuestIDs', set())
            dataQuestIDs.update(data.get('rewardsGottenQuestIDs', set()))
            completedQuestIDs = self.getQuestOfThisGroup(dataQuestIDs)
            pmQuestsIDs = set((qID for qID in completedQuestIDs if personal_missions.g_cache.isPersonalMission(qID)))
            rewards = getRewardsForQuests(message, completedQuestIDs)
            potapovQuestID = data.get('potapovQuestID', None)
            if potapovQuestID is not None:
                rewards.update({'potapovQuestID': potapovQuestID})
            rewards['popUpRecords'] = self.getPopUps(message)
            specialMessage = self.__formatSpecialMissions(completedQuestIDs, pmQuestsIDs, message, rewards)
            fmt = self._achievesFormatter.formatQuestAchieves(rewards, asBattleFormatter=False, processCustomizations=not specialMessage)
            if fmt is not None:
                templateParams = {'achieves': fmt}
                campaigns = set()
                for qID in pmQuestsIDs:
                    pmID = personal_missions.g_cache.getPersonalMissionIDByUniqueID(qID)
                    mission = self.__eventsCache.getPersonalMissions().getAllQuests()[pmID]
                    campaigns.add(mission.getCampaignID())

                if campaigns:
                    templateName = self.__PERSONAL_MISSIONS_CUSTOM_TEMPLATE
                    campaignNameKey = 'both' if len(campaigns) == 2 else 'c_{}'.format(first(campaigns))
                    templateParams['text'] = backport.text(R.strings.messenger.serviceChannelMessages.battleResults.personalMissions.dyn(campaignNameKey)())
                settings = self._getGuiSettings(message, templateName)
                formatted = g_settings.msgTemplates.format(templateName, templateParams)
                messageDataList.append(MessageData(formatted, settings))
            messageDataList.extend(specialMessage)
        if messageDataList:
            callback(messageDataList)
        else:
            callback([MessageData(None, None)])
        return

    def __formatSpecialMissions(self, questIDs, pmQuestsIDs, message, rewards):
        result = []
        newAwardListCount = 0
        retAwardListCount = 0
        tankmenAward = False
        camouflageGivenFor = set()
        camouflageUnlockedFor = set()
        for quest in self.__eventsCache.getHiddenQuests(lambda q: q.getID() in questIDs).values():
            camouflageGivenFor.update(self.__getCamouflageGivenFor(quest))
            camouflageUnlockedFor.update(self.__getCamouflageUnlockedFor(quest))

        for qID in pmQuestsIDs:
            pmType = personal_missions.g_cache.questByUniqueQuestID(qID)
            quest = self.__eventsCache.getPersonalMissions().getAllQuests().get(pmType.id)
            if quest and (qID.endswith('_main') or qID.endswith('_main_award_list')):
                tmBonus = quest.getTankmanBonus()
                if tmBonus.tankman:
                    tankmenAward = True
            if qID.endswith('add_award_list'):
                addAwardListQI = pmType.addAwardListQuestInfo
                tokensBonuses = addAwardListQI.get('bonus', {}).get('tokens', {})
                retAwardListCount += sum([ tokensBonuses[token]['count'] for token in self.__TOKENS_NAME if token in tokensBonuses ])
            if qID.endswith('add'):
                addAwardListQI = pmType.addQuestInfo
                tokensBonuses = addAwardListQI.get('bonus', {}).get('tokens', {})
                newAwardListCount += sum([ tokensBonuses[token]['count'] for token in self.__TOKENS_NAME if token in tokensBonuses ])

        if retAwardListCount > 0:
            text = backport.text(R.strings.system_messages.personalMissions.freeAwardListReturn(), count=retAwardListCount)
            result.append(text)
        if newAwardListCount > 0:
            text = backport.text(R.strings.system_messages.personalMissions.freeAwardListGain(), count=newAwardListCount)
            result.append(text)
        for vehIntCD in camouflageGivenFor:
            vehicle = self._itemsCache.items.getItemByCD(vehIntCD)
            text = backport.text(R.strings.system_messages.personalMissions.camouflageGiven(), vehicleName=vehicle.userName)
            result.append(text)

        for vehIntCD in camouflageUnlockedFor:
            vehicle = self._itemsCache.items.getItemByCD(vehIntCD)
            nationName = backport.text(R.strings.menu.nations.dyn(vehicle.nationName)())
            text = backport.text(R.strings.system_messages.personalMissions.camouflageUnlocked(), vehicleName=vehicle.userName, nation=nationName)
            result.append(text)

        if tankmenAward:
            result.append(backport.text(R.strings.system_messages.personalMissions.tankmenGain()))
        if result:
            if not rewards.get('tankmen', None):
                return [MessageData(getDefaultMessage(normal=EOL.join(result)), self._getGuiSettings(message, DEFAULT_MESSAGE))]
        return []

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        searchResult = re.search(cls.__PM_TOKEN_QUEST_PATTERNS, questID)
        return personal_missions.g_cache.isPersonalMission(questID) or searchResult

    def __getCamouflageGivenFor(self, quest):
        camouflageGivenFor = set()
        if quest.getID().endswith('camouflage'):
            for bonus in quest.getBonuses('customizations'):
                camouflage = findFirst(lambda c: c.get('custType') == 'camouflage' and c.get('vehTypeCompDescr'), bonus.getCustomizations())
                if camouflage:
                    camouflageGivenFor.add(camouflage.get('vehTypeCompDescr'))

        return camouflageGivenFor

    def __getCamouflageUnlockedFor(self, quest):
        camouflageUnlockedFor = set()
        regex = re.search(self.__REGEX_PATTERN_BADGE, quest.getID())
        if regex:
            operationID = int(regex.group(2))
            operations = self.__eventsCache.getPersonalMissions().getAllOperations()
            if operationID in operations:
                operation = operations[operationID]
                camouflageUnlockedFor.add(operation.getVehicleBonus().intCD)
        return camouflageUnlockedFor


class PersonalMissionsFormatter(PersonalMissionsTokenQuestsFormatter):
    _DEFAULT_TEMPLATE = 'personalMissions'

    def getPopUps(self, message):
        data = message.data or {}
        popUPs = set(data.get('popUpRecords', set()))
        otherQuestsPopUP = set()
        for achievesID, achievesCount in popUPs:
            achievesRecord = DB_ID_TO_RECORD[achievesID]
            for questID, questData in data.get('detailedRewards', {}).iteritems():
                records = [ (r.keys() if isinstance(r, dict) else [ rec[0] for rec in r ]) for r in questData.get('dossier', {}).values() ]
                for dossierRecord in chain.from_iterable(records):
                    if achievesRecord == dossierRecord and not self._isQuestOfThisGroup(questID):
                        otherQuestsPopUP.add((achievesID, achievesCount))

        return popUPs.difference(otherQuestsPopUP)

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return personal_missions.g_cache.isPersonalMission(questID)


class SeniorityAwardsFormatter(AsyncTokenQuestsSubFormatter):
    __MESSAGE_TEMPLATE = 'SeniorityAwardsQuest'
    __seniorityAwardCtrl = dependency.descriptor(ISeniorityAwardsController)

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
            messageData = self.__buildMessage(mergedRewards, message)
            if messageData is not None:
                messageDataList.append(messageData)
        if messageDataList:
            callback(messageDataList)
        else:
            callback([MessageData(None, None)])
        return

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        questPrefix = cls.__seniorityAwardCtrl.seniorityQuestPrefix
        return questID.startswith(questPrefix) if questPrefix else False

    def __buildMessage(self, rewards, message):
        data = message.data or {}
        questData = {}
        popUps = set()
        for dossierRecord in chain.from_iterable(rewards.get('dossier', {}).values()):
            if dossierRecord[0] in ACHIEVEMENT_BLOCK.ALL:
                achievementID = RECORD_DB_IDS.get(dossierRecord, None)
                popUps.update((popUp for popUp in data.get('popUpRecords', set()) if popUp[0] == achievementID))

        if popUps:
            questData['popUpRecords'] = popUps
        questData.update(rewards)
        fmt = self._achievesFormatter.formatQuestAchieves(questData, asBattleFormatter=False)
        if fmt is not None:
            templateParams = {'achieves': fmt}
            settings = self._getGuiSettings(message, self.__MESSAGE_TEMPLATE)
            formatted = g_settings.msgTemplates.format(self.__MESSAGE_TEMPLATE, templateParams)
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
        completedQuestIDs = self.getQuestOfThisGroup(data.get('completedQuestIDs', set()))
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
            if self.__battleMattersController.getFinalQuest().getID() == questID:
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
    __BATTLE_PASS_TOKEN_QUEST_PATTERN = 'battle_pass'

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
                if messageData is not None:
                    messageDataList.append(messageData)

        if messageDataList:
            callback(messageDataList)
        callback([MessageData(None, None)])
        return

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return cls.__BATTLE_PASS_TOKEN_QUEST_PATTERN in questID

    def __buildMessage(self, questID, message):
        data = message.data or {}
        questData = {}
        rewards = data.get('detailedRewards', {}).get(questID, {})
        questData.update(rewards)
        header = backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.header.voted())
        fmt = self._achievesFormatter.formatQuestAchieves(questData, asBattleFormatter=False)
        if fmt is not None:
            templateParams = {'text': fmt,
             'header': header}
            settings = self._getGuiSettings(message, self.__MESSAGE_TEMPLATE)
            formatted = g_settings.msgTemplates.format(self.__MESSAGE_TEMPLATE, templateParams)
            return MessageData(formatted, settings)
        else:
            return


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


class WotPlusDirectivesFormatter(AsyncTokenQuestsSubFormatter):
    __RENEWABLE_SUB_TOKEN_QUEST_PATTERN = 'wotplus:'
    __MESSAGE_TEMPLATE = 'WotPlusRenewMessage'

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        messageDataList = []
        if isSynced:
            data = message.data or {}
            completedQuestIDs = self.getQuestOfThisGroup(data.get('completedQuestIDs', set()))
            rewards = getRewardsForQuests(message, completedQuestIDs)
            fmt = self._achievesFormatter.formatQuestAchieves(rewards, asBattleFormatter=False, processCustomizations=True)
            if fmt is not None:
                templateParams = {'title': backport.text(R.strings.messenger.serviceChannelMessages.wotPlus.freeDirectives.received.title()),
                 'text': fmt}
                settings = self._getGuiSettings(message, self.__MESSAGE_TEMPLATE)
                formatted = g_settings.msgTemplates.format(self.__MESSAGE_TEMPLATE, templateParams)
                messageDataList.append(MessageData(formatted, settings))
        if messageDataList:
            callback(messageDataList)
        callback([MessageData(None, None)])
        return

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        tmp = cls.__RENEWABLE_SUB_TOKEN_QUEST_PATTERN in questID
        return tmp


class Comp7RewardsFormatter(SyncTokenQuestsSubFormatter):
    __PERIODIC_REWARD_MESSAGE_TEMPLATE = 'comp7PeriodicRewardMessage'
    __REGULAR_REWARD_MESSAGE_TEMPLATE = 'comp7RegularRewardMessage'
    __R_SYS_MESSAGES = R.strings.comp7.system_messages

    def format(self, message, *_):
        if message.data:
            messageData = []
            settings = self._getGuiSettings(message)
            completedIDs = self.getQuestOfThisGroup(message.data.get('completedQuestIDs', set()))
            for questID in completedIDs:
                questType = comp7_quest_helpers.getComp7QuestType(questID)
                if questType == Comp7QuestType.PERIODIC:
                    formatted = self.__formatPeriodicRewardMessage(message, questID)
                elif questType in (Comp7QuestType.RANKS, Comp7QuestType.WINS):
                    formatted = self.__formatRegularRewardMessage(message, questID)
                else:
                    formatted = None
                if formatted is not None:
                    messageData.append(MessageData(formatted, settings))

            if messageData:
                return messageData
        return [MessageData(None, None)]

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return comp7_quest_helpers.isComp7Quest(questID)

    def __formatPeriodicRewardMessage(self, message, questID):
        division = comp7_quest_helpers.parseComp7PeriodicQuestID(questID)
        rank = comp7_shared.getRankEnumValue(division)
        rewardsData = message.data.get('detailedRewards', {}).get(questID, {})
        if not rewardsData:
            return None
        else:
            formattedRewards = self._achievesFormatter.formatQuestAchieves(rewardsData, asBattleFormatter=False, processCustomizations=False, processTokens=False)
            formattedMessage = g_settings.msgTemplates.format(self.__PERIODIC_REWARD_MESSAGE_TEMPLATE, ctx={'title': backport.text(self.__R_SYS_MESSAGES.periodicReward.title()),
             'body': backport.text(self.__R_SYS_MESSAGES.periodicReward.body(), rank=backport.text(R.strings.comp7.rank.num(rank)()), rewards=formattedRewards)})
            return formattedMessage

    def __formatRegularRewardMessage(self, message, questID):
        rewardsData = message.data.get('detailedRewards', {}).get(questID, {})
        if not rewardsData:
            return None
        else:
            formattedRewards = self._achievesFormatter.formatQuestAchieves(rewardsData, asBattleFormatter=False, processCustomizations=True, processTokens=True)
            formattedMessage = g_settings.msgTemplates.format(self.__REGULAR_REWARD_MESSAGE_TEMPLATE, ctx={'title': backport.text(self.__R_SYS_MESSAGES.regularReward.title()),
             'body': backport.text(self.__R_SYS_MESSAGES.regularReward.body(), at=TimeFormatter.getLongDatetimeFormat(time_utils.makeLocalServerTime(message.sentTime)), rewards=formattedRewards)})
            return formattedMessage


class NewYearLevelUpRewardFormatter(AsyncTokenQuestsSubFormatter):
    _eventsCache = dependency.descriptor(IEventsCache)

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        if isSynced:
            messages = []
            data = message.data or {}
            questIDs = filter(self._isQuestOfThisGroup, data.get('completedQuestIDs', set()))
            levelSettings = self._getGuiSettings(message, 'InformationHeaderSysMessage', priorityLevel=NotificationPriorityLevel.LOW)
            rewardsSettings = self._getGuiSettings(message, self._getTemplateName(), priorityLevel=NotificationPriorityLevel.LOW)
            header = backport.text(R.strings.ny.notification.levelUp.congrats.header())
            questsMap = {int(questID.split(':')[-1]):questID for questID in questIDs}
            for level in sorted(questsMap.keys()):
                text = backport.text(R.strings.ny.notification.levelUp.congrats.body(), level=level)
                formatted = g_settings.msgTemplates.format('InformationHeaderSysMessage', ctx={'header': header,
                 'text': text})
                messages.append(MessageData(formatted, levelSettings))
                fmt = NewYearAchievesFormatter.formatQuestAchieves(data.get('detailedRewards', {}).get(questsMap[level], {}), asBattleFormatter=False, processTokens=False)
                if fmt is not None:
                    formatted = g_settings.msgTemplates.format(self._getTemplateName(), ctx={'text': fmt})
                    messages.append(MessageData(formatted, rewardsSettings))

            callback(messages)
        else:
            callback([MessageData(None, None)])
        return

    def _getTemplateName(self):
        pass

    @classmethod
    def _deleteColorAndFontAccentuation(cls, text):
        regex = re.compile("(color='#.*?'|<b>|</b>)")
        cleanText = re.sub(regex, '', text)
        return cleanText

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return questID.startswith(NY_LEVEL_PREFIX)


class NewYearCollectionRewardFormatter(AsyncTokenQuestsSubFormatter):
    _eventsCache = dependency.descriptor(IEventsCache)
    _TEMPLATE_NAME = 'newYearCollectionComplete'
    _STR_PATH = R.strings.ny.notification

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        messages = []
        if isSynced:
            data = message.data or {}
            detailedRewards = data.get('detailedRewards', {})
            questIDs = filter(self._isQuestOfThisGroup, data.get('completedQuestIDs', set()))
            for questID in questIDs:
                rewards = detailedRewards.get(questID, {})
                yearId, _, collectionKey, _ = questID.split(':')
                year = backport.text(R.strings.ny.systemMessage.dyn(yearId)())
                collectionName = self.__getCollectionName(yearId, collectionKey)
                rows = [backport.text(R.strings.ny.notification.collectionComplete(), setting=collectionName, year=year)]
                self._addFormattedRewards(rewards, rows)
                settings = self._getGuiSettings(message, self._TEMPLATE_NAME, messageSubtype=SCH_CLIENT_MSG_TYPE.NY_EVENT_BUTTON_MESSAGE)
                savedData = {'savedData': {'completedCollectionsQuests': [questID]}}
                formatted = g_settings.msgTemplates.format(self._TEMPLATE_NAME, ctx={'text': EOL.join(rows)}, data=savedData)
                messages.append(MessageData(formatted, settings))

            callback(messages)
        else:
            callback([MessageData(None, None)])
        return

    def _addFormattedRewards(self, data, rows):
        rewards = {}
        for customizationItem in data.get('customizations', []):
            custType = customizationItem['custType']
            guiItemType, item = getCustomizationItemData(customizationItem['id'], custType)
            itemCount = customizationItem['value']
            if itemCount > 1:
                count = backport.text(self._STR_PATH.collectionComplete.bonusCount(), count=itemCount)
                item = ' '.join((item, count))
            rewards.setdefault(guiItemType, []).append(item)

        for guiItemType, items in rewards.iteritems():
            custName = backport.text(self._STR_PATH.collectionComplete.dyn(guiItemType)())
            rows.append(' '.join((custName, ', '.join(items))))

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return not questID.startswith(NY_COLLECTION_MEGA_PREFIX) and questID.startswith(NY_COLLECTION_PREFIXES)

    @staticmethod
    def __getCollectionName(yearID, collectionID):
        collectionsRoot = R.strings.ny.notification.collectionComplete.name
        compoundKey = '_'.join((collectionID, yearID))
        rID = collectionsRoot.dyn(compoundKey) or collectionsRoot.dyn(collectionID)
        return backport.text(rID())


class NewYearCollectionMegaRewardFormatter(NewYearCollectionRewardFormatter):
    _eventsCache = dependency.descriptor(IEventsCache)
    _TEMPLATE_NAME = 'newYearCollectionMegaComplete'

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        formatted, settings = (None, None)
        if isSynced:
            data = message.data or {}
            questID = findFirst(self._isQuestOfThisGroup, data.get('completedQuestIDs', set()))
            yearId, _, _, _ = questID.split(':')
            collectionName = backport.text(self._STR_PATH.collectionMegaComplete(), year=backport.text(R.strings.ny.systemMessage.dyn(yearId)()))
            rows = [collectionName]
            rewards = data.get('detailedRewards', {}).get(questID)
            self._addFormattedRewards(rewards, rows)
            settings = self._getGuiSettings(message, self._TEMPLATE_NAME)
            formatted = g_settings.msgTemplates.format(self._TEMPLATE_NAME, ctx={'text': EOL.join(rows)})
        callback([MessageData(formatted, settings)])
        return None

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return questID.startswith(NY_COLLECTION_MEGA_PREFIX)


class NewYearOldCollectionRewardFormatter(AsyncTokenQuestsSubFormatter):
    _eventsCache = dependency.descriptor(IEventsCache)
    __TEMPLATE_NAME = 'newYearOldCollectionComplete'

    def __init__(self):
        super(NewYearOldCollectionRewardFormatter, self).__init__()
        self._achievesFormatter = NewYearCollectionFormatter()

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        messages = [MessageData(None, None)]
        if isSynced and message.data:
            data = message.data
            completedQuestIDs = self.getQuestOfThisGroup(data.get('completedQuestIDs', set()))
            rewards = getRewardsForQuests(message, completedQuestIDs)
            if rewards:
                fmt = self._achievesFormatter.formatAchieves(rewards)
                formatted = g_settings.msgTemplates.format(self.__TEMPLATE_NAME, ctx={'text': fmt})
                settings = self._getGuiSettings(message, self.__TEMPLATE_NAME)
                messages = [MessageData(formatted, settings)]
        callback(messages)
        return

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return questID.startswith(NY_OLD_COLLECTION_PREFIX)


class NewYearCelebrityMarathonRewardFormatter(AsyncTokenQuestsSubFormatter):

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        if isSynced:
            messages = BattleResultsFormatter().getCelebrityMarathonMessages(message)
            callback(messages)
        else:
            callback([MessageData(None, None)])
        return

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return questID.startswith(CELEBRITY_MARATHON_PREFIX)


class NewYearPiggyBankRewardFormatter(AsyncTokenQuestsSubFormatter):
    _eventsCache = dependency.descriptor(IEventsCache)
    _nyController = dependency.descriptor(INewYearController)

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        if not isSynced:
            callback([MessageData(None, None)])
            return
        else:
            templateName = 'InformationHeaderSysMessage'
            data = message.data or {}
            completedQuestIDs = data.get('completedQuestIDs', set())
            detailedRewards = data.get('detailedRewards', {})
            mergedRewards = defaultdict(list)
            for qID in completedQuestIDs:
                for bonus, value in detailedRewards.get(qID, {}).iteritems():
                    mergedRewards[bonus].extend(value)

            rewardsCount = sum([ len(rewards) for rewards in mergedRewards.values() ])
            titleBase = R.strings.system_messages.newYear.piggyBank
            title = backport.text(titleBase.rewards.title() if rewardsCount > 1 else titleBase.reward.title())
            text = self._achievesFormatter.formatQuestAchieves(mergedRewards, asBattleFormatter=False, processCustomizations=True)
            if self._nyController.isFinished():
                text = '<br/>'.join((backport.text(R.strings.system_messages.newYear.piggyBank.rewards.text()), text))
            formatted = g_settings.msgTemplates.format(templateName, ctx={'header': title,
             'text': text})
            settings = self._getGuiSettings(message, templateName, priorityLevel=NotificationPriorityLevel.LOW)
            callback([MessageData(formatted, settings)])
            return

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return questID.startswith(NY_PIGGY_BANK_MARATHON_PREFIX)


class NewYearCelebrityQuestRewardFormatter(AsyncTokenQuestsSubFormatter):
    _eventsCache = dependency.descriptor(IEventsCache)

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        if isSynced:
            messages = BattleResultsFormatter().getCelebrityQuestsMessages(message)
            callback(messages)
        else:
            callback([MessageData(None, None)])
        return

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return questID.startswith(CELEBRITY_QUESTS_PREFIX) and questID.endswith('bonus')
