# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/quests.py
import logging
import operator
import BigWorld
from constants import EVENT_TYPE
from gui import SystemMessages
from gui.SystemMessages import SM_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events.finders import PM_CAMPAIGNS_IDS
from gui.server_events.pm_constants import DISCARDABLE_OPERATIONS_IDS, PM_SUIT_OP_PLUGIN_ERR_RESPONSE
from gui.shared.gui_items.processors import Processor, makeI18nError, makeI18nSuccess, plugins, makeSuccess
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from items import tankmen, ITEM_TYPES
from personal_missions import PM_BRANCH
from shared_utils import first
from skeletons.gui.server_events import IEventsCache
_logger = logging.getLogger(__name__)

class _PMRequest(Processor):

    def __init__(self, personalMissions, branch):
        self._branch = branch
        self._quests = personalMissions
        super(_PMRequest, self).__init__((plugins.PMValidator(personalMissions),))

    def _getMessagePrefix(self):
        raise NotImplementedError

    def _errorHandler(self, code, errStr='', ctx=None):
        errorI18nKey = '{}/server_error'.format(self._getMessagePrefix())
        if errStr:
            errorI18nKey = '{}/{}'.format(errorI18nKey, errStr)
        return makeI18nError(sysMsgKey=errorI18nKey, questNames=', '.join(self._getQuestsNames()))

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey='{}/success'.format(self._getMessagePrefix()), questNames=', '.join(self._getQuestsNames()))

    def _request(self, callback):
        questIDs = self._getQuestsData(methodcaller=operator.methodcaller('getID'))
        _logger.debug('Make server request to select personal mission, questIDs: %s', questIDs)
        BigWorld.player().selectPersonalMissions(questIDs, self._branch, lambda code, errStr: self._response(code, callback, errStr=errStr))

    def _getQuestsData(self, methodcaller):
        return [ methodcaller(q) for q in self._quests ]

    def _getQuestsNames(self):
        return self._getQuestsData(methodcaller=operator.methodcaller('getShortUserName'))

    @staticmethod
    def _pushMessage(text, title, priority, messageType=SystemMessages.SM_TYPE.PmActiveOperation):
        SystemMessages.pushMessage(text=text, type=messageType, priority=priority, messageData={'title': title})


class PMQuestSelect(_PMRequest):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, branch, personalMission):
        currentSelectedQuests = self.eventsCache.getPersonalMissions().getSelectedQuestsForBranch(branch).values()
        operationID = personalMission.getOperationID()
        operation = self.eventsCache.getPersonalMissions().getOperationsForBranch(branch).get(operationID)
        if not operation.isStarted():
            quests, oldQuest = self._removeFromSameChain(currentSelectedQuests, operation.getInitialQuests().values())
        else:
            quests, oldQuest = self._removeFromSameChain(currentSelectedQuests, [personalMission])
        super(PMQuestSelect, self).__init__(quests, branch)
        deselectedQuests = set(currentSelectedQuests).difference(set(quests))
        selectConfirmatorEnable = operation.isStarted() and oldQuest is not None and oldQuest != personalMission
        self.addPlugins([plugins.PMLockedByVehicle(self._branch, deselectedQuests),
         plugins.PMSlotsValidator(self.eventsCache.getPersonalMissions().getQuestsProgress(self._branch), removedCount=int(oldQuest is not None)),
         plugins.PMSelectConfirmator(personalMission, oldQuest, 'questsConfirmDialogShow', isEnabled=selectConfirmatorEnable and oldQuest.getOperationID() not in (5, 6, 7)),
         plugins.PMSelectConfirmator(personalMission, oldQuest, 'questsConfirmDialogShowPM2', isEnabled=selectConfirmatorEnable and oldQuest.getOperationID() == 6),
         plugins.PMProgressResetConfirmator(personalMission, oldQuest, isEnabled=selectConfirmatorEnable and oldQuest.getOperationID() in (5, 7))])
        return

    def _getMessagePrefix(self):
        pass

    def _removeFromSameChain(self, quests, newQuests):
        newQuestsChainIDs = [ newQuest.getChainID() for newQuest in newQuests ]
        result = newQuests
        removedQuest = None
        for quest in quests:
            if quest.getChainID() not in newQuestsChainIDs:
                result.append(quest)
            removedQuest = quest

        return (result, removedQuest)

    def _request(self, callback):
        questIDs = self._getQuestsData(methodcaller=operator.methodcaller('getID'))
        _logger.debug('Make server request to select personal mission %s', ', '.join([ str(idn) for idn in questIDs ]))
        BigWorld.player().selectPersonalMissions(questIDs, self._branch, lambda code, errStr: self._response(code, callback, errStr=errStr))

    def _errorHandler(self, code, errStr='', ctx=None):
        errorI18nKey = '{}/server_error'.format(self._getMessagePrefix())
        questNames = ', '.join(self._getQuestsNames())
        if errStr:
            errorI18nKey = '{}/{}'.format(errorI18nKey, errStr)
        return makeI18nError(sysMsgKey=errorI18nKey, questNames=questNames)


class PM3OperationSelect(_PMRequest):
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, branch, operationID, missions=None, skipValidation=False, isFirstTimeEntrance=False):
        if not missions:
            personalMissions = self.__eventsCache.getPersonalMissions().getActualQuests(branch, operationID, withCompleted=False)
        else:
            personalMissions = missions
        self.__operationID = operationID
        self.__isFirstTimeEntrance = isFirstTimeEntrance
        super(PM3OperationSelect, self).__init__(personalMissions, branch)
        self.__inProgressPM3Operations = [ operation for operation in self.__eventsCache.getPersonalMissions().getStartedOperations(PM_BRANCH.V2_BRANCHES) if not operation.isFullCompleted() ]
        self.__currentActivePM3Operation = first(self.__eventsCache.getPersonalMissions().getActiveOperations(PM_BRANCH.V2_BRANCHES))
        self.addPlugins([plugins.PMLockedByOperation(operationID, not skipValidation)])

    def _getMessagePrefix(self):
        pass

    def _request(self, callback):
        questIDs = self._getQuestsData(methodcaller=operator.methodcaller('getID'))
        _logger.debug('Make server request to select personal mission %s', ', '.join([ str(idn) for idn in questIDs ]))
        BigWorld.player().selectPersonalMissions(questIDs, self._branch, lambda code, errStr: self._response(code, callback, errStr=errStr))

    def _successHandler(self, code, ctx=None):
        priority = NotificationPriorityLevel.LOW if self.__isFirstTimeEntrance else NotificationPriorityLevel.MEDIUM
        operation = self.__eventsCache.getPersonalMissions().getAllOperations(PM_BRANCH.V2_BRANCHES).get(self.__operationID)
        pmMessageSource = R.strings.system_messages.personalMissions
        if operation not in self.__inProgressPM3Operations:
            text = backport.text(pmMessageSource.operationActivation.body())
            title = backport.text(pmMessageSource.operationActivation.title(), operationName=operation.getUserName())
            self._pushMessage(text, title, priority)
        else:
            text = backport.text(pmMessageSource.operationResumed.body())
            title = backport.text(pmMessageSource.operationResumed.title(), operationName=operation.getUserName())
            self._pushMessage(text, title, priority)
        if self.__currentActivePM3Operation and self.__currentActivePM3Operation.getID() != operation.getID():
            text = backport.text(pmMessageSource.operationPaused.body())
            title = backport.text(pmMessageSource.operationPaused.title(), operationName=self.__currentActivePM3Operation.getUserName())
            messageType = SystemMessages.SM_TYPE.Pause
            self._pushMessage(text, title, priority, messageType)
            self.__currentActivePM3Operation = operation
        return makeSuccess()

    def _errorHandler(self, code, errStr='', ctx=None):
        errorI18nKey = '{}/server_error'.format(self._getMessagePrefix())
        return makeI18nError(sysMsgKey=errorI18nKey, type=SM_TYPE.ErrorSimple)


class PMDiscard(_PMRequest):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, personalMission, branch):
        quests = [personalMission]
        super(PMDiscard, self).__init__(quests, branch)
        isSuitableOperation = personalMission.getOperationID() in DISCARDABLE_OPERATIONS_IDS
        namePM3 = PM_BRANCH.TYPE_TO_NAME[PM_BRANCH.PERSONAL_MISSION_3]
        isPM3Active = namePM3 in self.eventsCache.getPersonalMissions().getActiveCampaigns() or personalMission.getQuestBranch() == PM_BRANCH.PERSONAL_MISSION_3
        self.addPlugins([plugins.DiscardSuitableOperationValidator(isSuitableOperation, personalMission.getOperationID()),
         plugins.PMActiveCampaignValidator(personalMission),
         plugins.PMDiscardConfirmator(personalMission, isEnabled=isSuitableOperation and not isPM3Active),
         plugins.PMLockedByVehicle(branch, quests)])

    def _request(self, callback):
        questIDs = self._getQuestsData(methodcaller=operator.methodcaller('getID'))
        _logger.debug('Make server request to discard personal mission %s', str(questIDs[0]))
        BigWorld.player().resetPersonalMissions(questIDs, self._branch, lambda code, errStr: self._response(code, callback, errStr=errStr))

    def _successHandler(self, code, ctx=None):
        questName = self._getQuestsNames()[0]
        return makeI18nSuccess('{}/success'.format(self._getMessagePrefix()), quest=questName)

    def _getMessagePrefix(self):
        pass


class PMPause(_PMRequest):

    def __init__(self, personalMission, enable, branch):
        quests = [personalMission]
        self._enable = enable
        super(PMPause, self).__init__(quests, branch)
        self.addPlugins([plugins.PauseSuitableOperationValidator(personalMission), plugins.PMActiveCampaignValidator(personalMission)])

    def _request(self, callback):
        questIDs = self._getQuestsData(methodcaller=operator.methodcaller('getID'))
        _logger.debug('Make server request to pause personal mission %s', str(questIDs[0]))
        BigWorld.player().pausePersonalMissions(questIDs, self._branch, self._enable, lambda code, errStr: self._response(code, callback, errStr=errStr))

    def _successHandler(self, code, ctx=None):
        questName = self._getQuestsNames()[0]
        enable = 'pause' if self._enable else 'unpause'
        return makeI18nSuccess('{}/success_{}'.format(self._getMessagePrefix(), enable), quest=questName)

    def _getMessagePrefix(self):
        pass


class PMActivateSeason(_PMRequest):
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, events_cache, branch, isFirstTimeEntrance=False):
        self.__activeCampaigns = self.__eventsCache.getPersonalMissions().getActiveCampaigns()
        self.__campaignOnActivation = PM_BRANCH.TYPE_TO_NAME[branch]
        selectedQuestsInActiveBranch = set()
        for campaign in self.__activeCampaigns:
            selectedQuestsInActiveBranch.union(set(events_cache.getSelectedQuestsForBranch(PM_BRANCH.NAME_TO_TYPE[campaign]).values()))

        self.__isFirstTimeEntrance = isFirstTimeEntrance
        super(PMActivateSeason, self).__init__(selectedQuestsInActiveBranch, branch)
        self.addPlugins([plugins.PMLockedByVehicle(branch, selectedQuestsInActiveBranch), plugins.PMActivateSameCampaignValidator(branch)])
        self._season = PM_BRANCH.V1_BRANCHES if branch in PM_BRANCH.V1_BRANCHES else PM_BRANCH.V2_BRANCHES

    def _request(self, callback):
        _logger.debug('Make server request to activate %s season', PM_BRANCH.TYPE_TO_NAME[self._season[0]])
        BigWorld.player().activatePersonalMissionsSeason(self._season, lambda code, errStr: self._response(code, callback, errStr=errStr))

    def _getMessagePrefix(self):
        pass

    def _successHandler(self, code, ctx=None):
        priority = NotificationPriorityLevel.LOW if self.__isFirstTimeEntrance else NotificationPriorityLevel.MEDIUM
        pm3Branch = PM_BRANCH.PERSONAL_MISSION_3
        namePM3 = PM_BRANCH.TYPE_TO_NAME[pm3Branch]
        allCampaigns = self.__eventsCache.getPersonalMissions().getAllCampaigns(branches=PM_BRANCH.ALL)
        pm3Campaign = allCampaigns.get(PM_CAMPAIGNS_IDS[pm3Branch])
        regularBranchName = PM_BRANCH.TYPE_TO_NAME[PM_BRANCH.REGULAR]
        regularCampaign = allCampaigns.get(PM_CAMPAIGNS_IDS[PM_BRANCH.REGULAR])
        pm2Campaign = allCampaigns.get(PM_CAMPAIGNS_IDS[PM_BRANCH.PERSONAL_MISSION_2])
        pmMessageSource = R.strings.system_messages.personalMissions
        if regularBranchName in self.__activeCampaigns:
            text = backport.text(pmMessageSource.campaign12Paused.body())
            title = backport.text(pmMessageSource.campaign12Paused.title(), campaignName1=regularCampaign.getUserName(), campaignName2=pm2Campaign.getUserName())
            messageType = SystemMessages.SM_TYPE.Pause
            self._pushMessage(text, title, priority, messageType)
        if namePM3 in self.__activeCampaigns and not pm3Campaign.isFullCompleted():
            text = backport.text(pmMessageSource.campaign3Paused.body())
            title = backport.text(pmMessageSource.campaign3Paused.title(), campaignName=pm3Campaign.getUserName())
            messageType = SystemMessages.SM_TYPE.Pause
            self._pushMessage(text, title, priority, messageType)
        if self._branch in PM_BRANCH.V1_BRANCHES and any(allCampaigns):
            text = backport.text(pmMessageSource.campaign12Resumed.body())
            title = backport.text(pmMessageSource.campaign12Resumed.title(), campaignName1=regularCampaign.getUserName(), campaignName2=pm2Campaign.getUserName())
            self._pushMessage(text, title, priority)
        if self._branch in PM_BRANCH.V2_BRANCHES and pm3Campaign.isStarted():
            text = backport.text(pmMessageSource.campaign3Resumed.body())
            title = backport.text(pmMessageSource.campaign3Resumed.title(), campaignName=pm3Campaign.getUserName())
            self._pushMessage(text, title, priority)
        return makeSuccess()

    def _errorHandler(self, code, errStr='', ctx=None):
        errorI18nKey = '{}/server_error'.format(self._getMessagePrefix())
        return makeI18nError(sysMsgKey=errorI18nKey)


class _PMGetReward(Processor):

    def __init__(self, personalMission, needTankman, nationID, inNationID, role):
        plugs = [plugins.PMRewardValidator(personalMission)]
        if needTankman:
            plugs.insert(0, plugins.VehicleCrewLockedValidator(self.itemsCache.items.getItem(ITEM_TYPES.vehicle, nationID, inNationID)))
        super(_PMGetReward, self).__init__(tuple(plugs))
        self.__quest = personalMission
        self.__nationID = nationID
        self.__inNationID = inNationID
        self.__role = role
        self.__needTankman = needTankman

    def _getMessagePrefix(self):
        pass

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('{}/server_error/{}'.format(self._getMessagePrefix(), errStr), defaultSysMsgKey='{}/server_error'.format(self._getMessagePrefix()))

    def _request(self, callback):
        _logger.debug('Make server request to get reward: %s, %s, %s, %s, %s', self.__quest, self.__needTankman, self.__nationID, self.__inNationID, self.__role)
        BigWorld.player().getPersonalMissionReward(self.__quest.getID(), self.__quest.getQuestBranch(), self.__needTankman, self.__nationID, self.__inNationID, tankmen.SKILL_INDICES[self.__role], lambda code, errStr, tmanInvID: self._response(code, callback, errStr=errStr, ctx=tmanInvID))


class PMGetTankwomanReward(_PMGetReward):

    def __init__(self, personalMission, nationID, inNationID, role):
        super(PMGetTankwomanReward, self).__init__(personalMission, True, nationID, inNationID, role)

    def _getMessagePrefix(self):
        pass


class PMGetReward(_PMGetReward):

    def __init__(self, personalMission):
        super(PMGetReward, self).__init__(personalMission, False, 0, 0, 'commander')


class PM3GetQuestRewards(Processor):

    def __init__(self, quest):
        super(PM3GetQuestRewards, self).__init__()
        self.__quest = quest

    def _getMessagePrefix(self):
        pass

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('{}/server_error/{}'.format(self._getMessagePrefix(), errStr), defaultSysMsgKey='{}/server_error'.format(self._getMessagePrefix()))

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess('{}/success'.format(self._getMessagePrefix()))

    def _request(self, callback):
        _logger.debug('Make server request to get reward: %s', self.__quest)
        BigWorld.player().getPersonalMissionsQuestRewards(EVENT_TYPE.TOKEN_QUEST, self.__quest.getID(), lambda code, errStr, rewards=None: self._response(code, callback, errStr, rewards))
        return


class PMPawn(Processor):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, personalMission):
        namePM3 = PM_BRANCH.TYPE_TO_NAME[PM_BRANCH.PERSONAL_MISSION_3]
        isPM3Active = namePM3 in self.eventsCache.getPersonalMissions().getActiveCampaigns() or personalMission.getQuestBranch() == PM_BRANCH.PERSONAL_MISSION_3
        super(PMPawn, self).__init__((plugins.PMPawnConfirmator(personalMission, isEnabled=not isPM3Active),
         plugins.PMPawnValidator([personalMission]),
         plugins.PMFreeTokensValidator(personalMission),
         plugins.PMActiveCampaignValidator(personalMission)))
        self.__quest = personalMission

    def _getMessagePrefix(self):
        pass

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(PM_SUIT_OP_PLUGIN_ERR_RESPONSE) if errStr == PM_SUIT_OP_PLUGIN_ERR_RESPONSE else makeI18nError('{}/server_error/{}'.format(self._getMessagePrefix(), errStr), defaultSysMsgKey='{}/server_error'.format(self._getMessagePrefix()))

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess('{}/success'.format(self._getMessagePrefix()), questName=self.__quest.getShortUserName(), count=self.__quest.getPawnCost())

    def _request(self, callback):
        _logger.debug('Make server request to pawn quest: %s', self.__quest)
        BigWorld.player().pawnFreeAwardList(self.__quest.getType(), self.__quest.getID(), lambda code: self._response(code, callback))
