# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/quests.py
from __future__ import absolute_import
import logging
import operator
from future.utils import listvalues
import typing
import BigWorld
from constants import EVENT_TYPE
from gui import SystemMessages
from gui.SystemMessages import SM_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events.pm_constants import DISCARDABLE_OPERATIONS_IDS, PM_SUIT_OP_PLUGIN_ERR_RESPONSE
from gui.shared.gui_items.processors import Processor, makeI18nError, makeI18nSuccess, makeSuccess, plugins
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from items import ITEM_TYPES, tankmen
from personal_missions import PM_BRANCH
from shared_utils import first
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from gui.server_events.event_items import PersonalMission
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

    def __init__(self, branch, personalMission, isOperationActivation=False):
        currentSelectedQuests = listvalues(self.eventsCache.getPersonalMissions().getSelectedQuestsForBranch(branch))
        operationID = personalMission.getOperationID()
        operation = self.eventsCache.getPersonalMissions().getOperationsForBranch(branch).get(operationID)
        if not operation.isStarted() and not operation.getCompletedQuests() and isOperationActivation:
            quests, oldQuest = self._removeFromSameChain(currentSelectedQuests, listvalues(operation.getInitialQuests()))
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


class PMOperationSelect(_PMRequest):
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, branch, operationID, missions=None, skipValidation=False, isFirstTimeEntrance=False):
        self.__pmCache = self.__eventsCache.getPersonalMissions()
        super(PMOperationSelect, self).__init__(missions if missions else self.__pmCache.getActualQuests(branch, operationID, withCompleted=False), branch)
        self.__operationID = operationID
        self.__isFirstTimeEntrance = isFirstTimeEntrance
        self.__branches = PM_BRANCH.WITHOUT_AWARD_LIST_BRANCHES if PM_BRANCH.TYPE_TO_NAME[branch] in PM_BRANCH.WITHOUT_AWARD_LIST_BRANCHES else PM_BRANCH.WITH_AWARD_LIST_BRANCHES
        self.__inProgressPMOperations = [ operation for operation in self.__pmCache.getStartedOperations(self.__branches) if not operation.isFullCompleted() ]
        activeCampaigns = self.__pmCache.getActiveCampaigns()
        self.__currentActivePMOperation = first((operation for operation in self.__pmCache.getActiveOperations(self.__branches) if operation.getBranchName() in activeCampaigns))
        self.addPlugins([plugins.PMLockedByOperation(operationID, branch, isEnabled=not skipValidation)])

    def _getMessagePrefix(self):
        pass

    def _request(self, callback):
        questIDs = self._getQuestsData(methodcaller=operator.methodcaller('getID'))
        _logger.debug('Make server request to select personal mission %s', ', '.join([ str(idn) for idn in questIDs ]))
        BigWorld.player().selectPersonalMissions(questIDs, self._branch, lambda code, errStr: self._response(code, callback, errStr=errStr))

    def _successHandler(self, code, ctx=None):
        priority = NotificationPriorityLevel.LOW if self.__isFirstTimeEntrance else NotificationPriorityLevel.MEDIUM
        operation = self.__pmCache.getAllOperations(self.__branches).get(self.__operationID)
        pmMessageSource = R.strings.system_messages.personalMissions
        if operation not in self.__inProgressPMOperations:
            text = backport.text(pmMessageSource.operationActivation.body())
            title = backport.text(pmMessageSource.operationActivation.title(), operationName=operation.getUserName())
            self._pushMessage(text, title, priority)
        else:
            text = backport.text(pmMessageSource.operationResumed.body())
            title = backport.text(pmMessageSource.operationResumed.title(), operationName=operation.getUserName())
            self._pushMessage(text, title, priority)
        if self.__currentActivePMOperation and self.__currentActivePMOperation.getID() != operation.getID() and not self.__currentActivePMOperation.isFullCompleted(isFinalRewardReceived=False):
            text = backport.text(pmMessageSource.operationPaused.body())
            title = backport.text(pmMessageSource.operationPaused.title(), operationName=self.__currentActivePMOperation.getUserName())
            messageType = SystemMessages.SM_TYPE.Pause
            self._pushMessage(text, title, priority, messageType)
            self.__currentActivePMOperation = operation
        return makeSuccess()

    def _errorHandler(self, code, errStr='', ctx=None):
        errorI18nKey = '{}/server_error'.format(self._getMessagePrefix())
        return makeI18nError(sysMsgKey=errorI18nKey, type=SM_TYPE.ErrorSimple)


class PMDiscard(_PMRequest):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, personalMission, branch):
        quests = [personalMission]
        super(PMDiscard, self).__init__(quests, branch)
        operationID = personalMission.getOperationID()
        isSuitableOperation = operationID in DISCARDABLE_OPERATIONS_IDS
        isSuitableBranch = personalMission.getPMType().isBranchWithAwardListQuests and PM_BRANCH.TYPE_TO_NAME[branch] in PM_BRANCH.MUTUAL_EXCLUSION_BRANCHES[PM_BRANCH.QUEST_GROUPS.GROUP_1]
        self.addPlugins([plugins.DiscardSuitableOperationValidator(isSuitableOperation, operationID),
         plugins.PMActiveCampaignValidator(personalMission),
         plugins.PMDiscardConfirmator(personalMission, isEnabled=isSuitableOperation and isSuitableBranch),
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

    def __init__(self, branch):
        self.__pmCache = self.__eventsCache.getPersonalMissions()
        self.__activeCampaigns = self.__pmCache.getActiveCampaigns()
        selectedQuestsInActiveBranch = set()
        for campaign in self.__activeCampaigns:
            selectedQuestsInActiveBranch.union(set(self.__pmCache.getSelectedQuestsForBranch(PM_BRANCH.NAME_TO_TYPE[campaign]).values()))

        super(PMActivateSeason, self).__init__(selectedQuestsInActiveBranch, branch)
        self.addPlugins([plugins.PMLockedByVehicle(branch, selectedQuestsInActiveBranch), plugins.PMActivateSameCampaignValidator(branch)])
        branchName = PM_BRANCH.TYPE_TO_NAME[branch]
        self._season = PM_BRANCH.convertNameToType(first([ branches for branches in PM_BRANCH.MUTUAL_EXCLUSION_BRANCHES.values() if branchName in branches ], default=()))

    def _request(self, callback):
        _logger.debug('Make server request to activate %s season', PM_BRANCH.TYPE_TO_NAME[self._season[0]])
        BigWorld.player().activatePersonalMissionsSeason(self._season, lambda code, errStr: self._response(code, callback, errStr=errStr))

    def _getMessagePrefix(self):
        pass

    def _successHandler(self, code, ctx=None):
        pass

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


class PMGetQuestRewards(Processor):

    def __init__(self, quest, branchName):
        super(PMGetQuestRewards, self).__init__()
        self.__quest = quest
        self.__branchName = branchName

    def _getMessagePrefix(self):
        return 'personalMissions/reward/%s' % self.__branchName

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
        isNotSupportedBranchActive = personalMission.getPMType().isBranchWithoutAwardListQuests or self.eventsCache.getPersonalMissions().isBranchWithoutAwardListActive()
        super(PMPawn, self).__init__((plugins.PMPawnConfirmator(personalMission, isEnabled=not isNotSupportedBranchActive),
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
