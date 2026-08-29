# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/formatters/personal_missions_formatters.py
import re
from itertools import chain
import constants
import personal_missions as pm
from gui.impl import backport
from gui.server_events.bonuses import PersonalMissionsPointsTokensBonus
from gui.server_events.event_items import PM3_ROLE_TO_ICON_NAME
from gui.server_events.finders import NO_AWARD_LIST_FINISHED_QUEST, NO_AWARD_LIST_HONOR_POSTFIX
from gui.server_events.personal_progress.formatters import PMCardConditionsFormatter
from messenger import g_settings
from personal_missions import PM_BRANCH
from adisp import adisp_async, adisp_process
from helpers import dependency, i18n, int2roman
from messenger.formatters.service_channel import PersonalMissionsQuestAchievesFormatter, PMCompletionFormatter, PMMedalsFormatter, WaitItemsSyncFormatter
from messenger.formatters.service_channel_helpers import DEFAULT_MESSAGE, EOL, MessageData, getDefaultMessage, getPMAdvancedOperationAndQuest, getPotapovQuestPopUps, getRewardsForQuests
from messenger.formatters.token_quest_subformatters import AsyncTokenQuestsSubFormatter, TokenQuestsSubFormatter
from gui.impl.gen import R
from shared_utils import findFirst, first
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache

class PMBasicTokenQuestsFormatter(AsyncTokenQuestsSubFormatter):
    _DEFAULT_TEMPLATE = 'tokenQuests'
    __eventsCache = dependency.descriptor(IEventsCache)
    __PERSONAL_MISSIONS_CUSTOM_TEMPLATE = 'personalMissionsCustom'
    __PM12_OPERATIONS_PATTERN = '|'.join(map(str, PM_BRANCH.BRANCH_TO_OPERATION_IDS[PM_BRANCH.PERSONAL_MISSION_2] + PM_BRANCH.BRANCH_TO_OPERATION_IDS[PM_BRANCH.REGULAR]))
    __PM_TOKEN_QUEST_PATTERNS = 'pt_final_s(\\d)_t({op})$|pt_final_s(\\d)_t({op})_camouflage|pt_final_s(\\d)_t({op})_badge|pt_s(\\d)_t(\\d)_c(\\d)_add_reward|pt_final_badge_s(\\d)'.format(op=__PM12_OPERATIONS_PATTERN)
    __REGEX_PATTERN_BADGE = 'pt_final_s(\\d)_t(\\d)_badge'
    __TOKENS_NAME = (constants.PERSONAL_MISSION_FREE_TOKEN_NAME, constants.PERSONAL_MISSION_2_FREE_TOKEN_NAME)

    def __init__(self):
        super(PMBasicTokenQuestsFormatter, self).__init__()
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
            pmQuestsIDs = set((qID for qID in completedQuestIDs if pm.g_cache.isPersonalMission(qID)))
            pmQuestsCache = self.__eventsCache.getPersonalMissions().getAllQuests(PM_BRANCH.ALL_NAMES)
            if not data.get('potapovQuestID') or data.get('potapovQuestID') in pmQuestsCache:
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
                        pmID = pm.g_cache.getPersonalMissionIDByUniqueID(qID)
                        mission = pmQuestsCache[pmID]
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
            pmType = pm.g_cache.questByUniqueQuestID(qID)
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
        return pm.g_cache.isPersonalMission(questID) or searchResult

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


class PersonalMissionsBasicFormatter(PMBasicTokenQuestsFormatter):
    _DEFAULT_TEMPLATE = 'personalMissions'
    __PM_PREFIX_PATTERN = '^({})'.format('|'.join(PM_BRANCH.WITH_AWARD_LIST_BRANCHES))

    def getPopUps(self, message):
        return getPotapovQuestPopUps(message, self._isQuestOfThisGroup)

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return pm.g_cache.isPersonalMission(questID) and re.search(cls.__PM_PREFIX_PATTERN, questID)


class PMAdvancedQuestFormatter(WaitItemsSyncFormatter):
    __TEMPLATE = 'PersonalMission3Quest'
    __TEMPLATE_AFFIRMATIVE = 'PersonalMission3Quest15'
    __PERSONAL_MISSIONS_ACHIEVES_CUSTOM_TEMPLATE = 'personalMissions3Custom'
    __MAX_AWARDS = 4
    __QUEST_GROUP = PM_BRANCH.WITHOUT_AWARD_LIST_BRANCHES
    __itemsCache = dependency.descriptor(IItemsCache)
    __eventsCache = dependency.descriptor(IEventsCache)
    __PM_PREFIX_PATTERN = '^({})'.format('|'.join(PM_BRANCH.WITHOUT_AWARD_LIST_BRANCHES))

    def __init__(self):
        super(PMAdvancedQuestFormatter, self).__init__()
        self._achievesFormatter = PMMedalsFormatter()

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        emptyMessageData = [MessageData(None, None)]
        isSynced = yield self._waitForSyncItems()
        if not isSynced:
            callback(emptyMessageData)
        data = message.data
        if not data:
            callback(emptyMessageData)
        questID = data.get('potapovQuestID', 0)
        quest = self.__eventsCache.getPersonalMissions().getAllQuests(self.__QUEST_GROUP).get(questID)
        if not quest:
            callback(emptyMessageData)
        questFormatter = PMCardConditionsFormatter(quest)
        allVehs = first([ config.get('progressData', {}).get('uniqueVehicles') for config in questFormatter.bodyFormat() if config.get('progressData', {}).get('uniqueVehicles') ], 1)
        if allVehs <= 0:
            callback(emptyMessageData)
        operationID = quest.getOperationID()
        chainID = quest.getChainID()
        vehCDs = data.get('battlesUniqueVehicles', {})
        operation, _ = getPMAdvancedOperationAndQuest(operationID, chainID, questID)
        messageDataList = self.__makeMessageData(message, vehCDs, allVehs, operation, quest)
        callback(messageDataList)
        return

    def __makeMessageData(self, message, vehCDs, allVehs, operation, quest):
        vehicles = []
        msg = []
        for vehCD in vehCDs:
            vehicle = self.__itemsCache.items.getItemByCD(vehCD)
            vehicles.append({'userName': vehicle.userName,
             'levelRoman': int2roman(vehicle.level),
             'level': vehicle.level,
             'type': vehicle.type,
             'isPrem': vehicle.isPremium})

        chainID = quest.getChainID()
        chainName = i18n.makeString(operation.getChainName(chainID))
        operationTitle = backport.text(R.strings.system_messages.personalMission.awardsNotification.operation(), operation=operation.getUserName())
        classifier = operation.getChainClassifier(chainID).classificationAttr
        category = PM3_ROLE_TO_ICON_NAME[classifier]
        vehicles.sort(key=lambda veh: veh.get('level'))
        completed = len(vehicles)
        statusWrapped = ''
        isCompleted = bool(not vehCDs)
        awards = []
        if isCompleted:
            awards = self.__packBonuses(quest.getBonuses(), operation.isCompleted())
        else:
            allVehsStr = backport.text(R.strings.system_messages.personalMission.awardsNotification.status.all(), all=allVehs)
            allVehsWrapped = g_settings.htmlTemplates.format('pm3Gray', ctx={'message': allVehsStr})
            status = backport.text(R.strings.system_messages.personalMission.awardsNotification.status(), completed=str(completed), all=allVehsWrapped)
            statusWrapped = g_settings.htmlTemplates.format('pm3Beige', ctx={'message': status})
        formatted = g_settings.msgTemplates.format(self.__TEMPLATE if not quest.isFinal() else self.__TEMPLATE_AFFIRMATIVE, ctx={'header': operationTitle}, data={'buttonsStates': {'submitGhost': self.__getButtonState(quest)},
         'savedData': {'operationID': quest.getOperationID(),
                       'questID': quest.getID(),
                       'chainID': chainID},
         'linkageData': {'mission': chainName,
                         'missionNumber': quest.getInternalID(),
                         'category': category,
                         'isCompleted': isCompleted,
                         'allVehs': allVehs,
                         'status': statusWrapped,
                         'vehicles': vehicles,
                         'awards': awards}})
        msg.append(MessageData(formatted, self._getGuiSettings(message, self.__TEMPLATE, messageType=message.type)))
        if isCompleted and message.data.get('popUpRecords'):
            medalNotification = self.__getMedalNotification(message, chainName, quest)
            if medalNotification:
                msg.append(medalNotification)
        return msg

    def __getMedalNotification(self, message, chainName, quest):
        data = message.data
        data['popUpRecords'] = getPotapovQuestPopUps(message, self._isQuestOfThisGroup)
        if not data['popUpRecords']:
            return
        else:
            fmt = self._achievesFormatter.formatPopUpRecords(data)
            if fmt is None:
                return
            templateParams = {}
            pmCache = self.__eventsCache.getPersonalMissions()
            campaignID = quest.getCampaignID()
            campaignName = pmCache.getAllCampaigns(self.__QUEST_GROUP)[campaignID].getUserName()
            templateParams['title'] = backport.text(R.strings.messenger.serviceChannelMessages.battleResults.notification.personalMissions.dyn('c_{}'.format(campaignID)).header())
            achieveStage = list(data['popUpRecords'])[0][-1]
            if achieveStage is not True:
                group3Branches = PM_BRANCH.MUTUAL_EXCLUSION_BRANCHES[PM_BRANCH.QUEST_GROUPS.GROUP_3]
                resID = R.strings.messenger.serviceChannelMessages.battleResults.notification.personalMissions.dyn('c_{}'.format(campaignID)).stage.dyn('c_{}'.format(str(achieveStage))).description()
                if quest.getPMType().branchName in group3Branches:
                    operationName = pmCache.getAllOperations(group3Branches)[quest.getOperationID()].getUserName()
                    text = backport.text(resID, categoryName=chainName, operationName=operationName, nameMedal=fmt)
                else:
                    text = backport.text(resID, categoryName=chainName, campaignName=campaignName, nameMedal=fmt)
            else:
                text = backport.text(R.strings.messenger.serviceChannelMessages.battleResults.notification.personalMissions.dyn('c_{}'.format(campaignID)).description(), campaignName=campaignName, nameMedal=fmt)
            templateParams['text'] = text
            settings = self._getGuiSettings(message, self.__PERSONAL_MISSIONS_ACHIEVES_CUSTOM_TEMPLATE)
            formattedAchieves = g_settings.msgTemplates.format(self.__PERSONAL_MISSIONS_ACHIEVES_CUSTOM_TEMPLATE, templateParams)
            return MessageData(formattedAchieves, settings)

    def __packBonuses(self, bonuses, isOperationCompleted):
        from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import CurtailingAwardsComposer
        from gui.impl.lobby.personal_missions_30.bonus_packers import getNotificationBonusOrder
        composer = CurtailingAwardsComposer(displayedAwardsCount=self.__MAX_AWARDS)
        if isOperationCompleted:
            bonuses = [ bonus for bonus in bonuses if not isinstance(bonus, PersonalMissionsPointsTokensBonus) ]
        awards = composer.getFormattedBonuses(sorted(bonuses, key=getNotificationBonusOrder))
        return awards

    def __getButtonState(self, quest):
        from notification.settings import NOTIFICATION_BUTTON_STATE
        from gui.impl.lobby.personal_missions_30.views_helpers import canOpenOperationPage
        if quest.isCompleted():
            isEnabled = canOpenOperationPage(quest.getOperationID())
            if isEnabled:
                return NOTIFICATION_BUTTON_STATE.DEFAULT
            return NOTIFICATION_BUTTON_STATE.VISIBLE
        return NOTIFICATION_BUTTON_STATE.HIDDEN

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return pm.g_cache.isPersonalMission(questID) and re.search(cls.__PM_PREFIX_PATTERN, questID)


class PMAdvancedCompletionFormatter(WaitItemsSyncFormatter, TokenQuestsSubFormatter):
    _PM_OPERATIONS_PATTERN = '|'.join(map(str, chain(*(PM_BRANCH.BRANCH_TO_OPERATION_IDS[PM_BRANCH.NAME_TO_TYPE[branchName]] for branchName in PM_BRANCH.WITHOUT_AWARD_LIST_BRANCHES))))
    _PM_COMPAING_PATTERN = '|'.join(map(str, PM_BRANCH.WITHOUT_AWARD_LIST_BRANCHES))
    _PM_TOKEN_QUEST_PATTERNS = 'pt_final_s(\\d)_t({op})_honor|({comp})_campaign_finished_honor|pt_final_s(\\d)_t({op})$'.format(op=_PM_OPERATIONS_PATTERN, comp=_PM_COMPAING_PATTERN)
    _OPERATION_COMPLETE_PATTERN = 'token:pt:s(\\d):t({op}):finished:base'.format(op=_PM_OPERATIONS_PATTERN)
    _PERSONAL_MISSIONS_HONOR_TEMPLATE = 'pmAdvancedCompletionHonor'
    _PERSONAL_MISSIONS_OPERATION_TEMPLATE = 'pmAdvancedOperationCompletion'
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        super(PMAdvancedCompletionFormatter, self).__init__()
        self._achievesFormatter = PMCompletionFormatter()

    @adisp_async
    @adisp_process
    def format(self, message, callback):
        isSynced = yield self._waitForSyncItems()
        messageDataList = []
        if isSynced:
            data = message.data or {}
            dataQuestIDs = data.get('completedQuestIDs', set())
            dataQuestIDs.update(data.get('rewardsGottenQuestIDs', set()))
            for token in data.get('tokens', {}):
                if re.search(self._OPERATION_COMPLETE_PATTERN, token):
                    bonuses = {}
                    operationID = int(token.split(':')[3][1:])
                    operation = self.__eventsCache.getPersonalMissions().getAllOperations(PM_BRANCH.WITHOUT_AWARD_LIST_BRANCHES)[operationID]
                    for bonus in operation.getRewardQuest().getBonuses():
                        if bonus.getName() != 'vehicles':
                            bonuses[bonus.getName()] = bonus.getValue()
                        bonusValue = bonus.getValue()
                        for vehInfo in bonusValue.values():
                            if bonus.isNonZeroCompensation(vehInfo):
                                if 'customCompensation' in vehInfo:
                                    vehInfo.pop('customCompensation')
                                elif 'compensatedNumber' in vehInfo:
                                    vehInfo.pop('compensatedNumber')

                        bonuses[bonus.getName()] = [bonusValue]

                    fmt = self._achievesFormatter.formatQuestAchieves(bonuses, asBattleFormatter=False, processCustomizations=True)
                    if fmt is not None:
                        operationName = operation.getUserName()
                        templateParams = {'achieves': fmt}
                        templateParams['title'] = backport.text(R.strings.system_messages.personalMission.operationComplete.title(), operationName=operationName)
                        templateParams['text'] = backport.text(R.strings.system_messages.personalMission.CompletionNotification.body())
                        settings = self._getGuiSettings(message, self._PERSONAL_MISSIONS_OPERATION_TEMPLATE)
                        formatted = g_settings.msgTemplates.format(self._PERSONAL_MISSIONS_OPERATION_TEMPLATE, templateParams)
                        messageDataList.append(MessageData(formatted, settings))

            completedQuestIDs = self.getQuestOfThisGroup(dataQuestIDs)
            for qID in completedQuestIDs:
                completedCampaignName = ''
                rewards = getRewardsForQuests(message, {qID})
                fmt = self._achievesFormatter.formatQuestAchieves(rewards, asBattleFormatter=False, processCustomizations=True)
                templateParams = {'achieves': fmt}
                if qID.endswith(NO_AWARD_LIST_HONOR_POSTFIX):
                    for branchName in PM_BRANCH.WITHOUT_AWARD_LIST_BRANCHES:
                        finishedQuestID = NO_AWARD_LIST_FINISHED_QUEST % PM_BRANCH.PM_CAMPAIGNS_IDS[PM_BRANCH.NAME_TO_TYPE[branchName]]
                        if qID == finishedQuestID:
                            completedCampaignName = branchName
                            campaignName = self.__getCampaignName(PM_BRANCH.NAME_TO_TYPE[branchName])
                            templateParams['title'] = backport.text(R.strings.system_messages.personalMission.campaignCompleteHonor.title(), campaignName=campaignName)
                            break

                    if completedCampaignName in PM_BRANCH.MUTUAL_EXCLUSION_BRANCHES[PM_BRANCH.QUEST_GROUPS.GROUP_3]:
                        continue
                    if not templateParams.get('title'):
                        operationID = int(qID.split('_')[-2][1:])
                        operationName = self.__getOperationName(operationID)
                        templateParams['title'] = backport.text(R.strings.system_messages.personalMission.operationCompleteHonor.title(), operationName=operationName)
                    templateParams['text'] = backport.text(R.strings.system_messages.personalMission.CompletionNotification.body())
                    settings = self._getGuiSettings(message, self._PERSONAL_MISSIONS_HONOR_TEMPLATE)
                    formatted = g_settings.msgTemplates.format(self._PERSONAL_MISSIONS_HONOR_TEMPLATE, templateParams)
                    messageDataList.append(MessageData(formatted, settings))

        if messageDataList:
            callback(messageDataList)
        else:
            callback([MessageData(None, None)])
        return

    @classmethod
    def _isQuestOfThisGroup(cls, questID):
        return re.search(cls._PM_TOKEN_QUEST_PATTERNS, questID)

    def __getOperationName(self, operationID):
        return self.__eventsCache.getPersonalMissions().getAllOperations(PM_BRANCH.WITHOUT_AWARD_LIST_BRANCHES)[operationID].getUserName()

    def __getCampaignName(self, branchID):
        return self.__eventsCache.getPersonalMissions().getCampaignsForBranch(branchID).get(PM_BRANCH.PM_CAMPAIGNS_IDS[branchID]).getUserName()
