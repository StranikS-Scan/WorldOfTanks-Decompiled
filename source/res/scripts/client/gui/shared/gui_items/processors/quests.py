# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/quests.py
import operator
import logging
import BigWorld
from debug_utils import LOG_DEBUG
from gui.shared.gui_items.processors import Processor, makeI18nError, makeI18nSuccess, plugins
from items import tankmen, ITEM_TYPES
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

class _PMRequest(Processor):

    def __init__(self, personalMissions, branch):
        self._branch = branch
        self.__quests = personalMissions
        super(_PMRequest, self).__init__((plugins.PMValidator(personalMissions),))

    def _getMessagePrefix(self):
        raise NotImplementedError

    def _errorHandler(self, code, errStr='', ctx=None):
        errorI18nKey = '%s/server_error' % self._getMessagePrefix()
        if errStr:
            errorI18nKey = '%s/%s' % (errorI18nKey, errStr)
        return makeI18nError(errorI18nKey, questNames=', '.join(self._getQuestsNames()))

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess('%s/success' % self._getMessagePrefix(), questNames=', '.join(self._getQuestsNames()))

    def _getQuestsData(self, methodcaller):
        return [ methodcaller(q) for q in self.__quests ]

    def _getQuestsNames(self):
        return self._getQuestsData(methodcaller=operator.methodcaller('getShortUserName'))


class PMQuestSelect(_PMRequest):

    def __init__(self, personalMission, events_cache, branch):
        quests, oldQuest = self._removeFromSameChain(events_cache.getSelectedQuestsForBranch(branch).values(), personalMission)
        super(PMQuestSelect, self).__init__(quests, branch)
        deselectedQuests = set(events_cache.getSelectedQuestsForBranch(self._branch).values()).difference(set(quests))
        selectConfirmatorEnable = oldQuest is not None and oldQuest != personalMission
        self.addPlugins([plugins.PMLockedByVehicle(self._branch, deselectedQuests),
         plugins.PMSlotsValidator(events_cache.getQuestsProgress(self._branch), removedCount=int(oldQuest is not None)),
         plugins.PMSelectConfirmator(personalMission, oldQuest, 'questsConfirmDialogShow', isEnabled=selectConfirmatorEnable and oldQuest.getOperationID() not in (5, 6, 7)),
         plugins.PMSelectConfirmator(personalMission, oldQuest, 'questsConfirmDialogShowPM2', isEnabled=selectConfirmatorEnable and oldQuest.getOperationID() == 6),
         plugins.PMProgressResetConfirmator(personalMission, oldQuest, isEnabled=selectConfirmatorEnable and oldQuest.getOperationID() in (5, 7))])
        return

    def _getMessagePrefix(self):
        pass

    def _removeFromSameChain(self, quests, newQuest):
        result = [newQuest]
        removedQuest = None
        for quest in quests:
            if quest.getChainID() != newQuest.getChainID():
                result.append(quest)
            removedQuest = quest

        return (result, removedQuest)

    def _request(self, callback):
        questIDs = self._getQuestsData(methodcaller=operator.methodcaller('getID'))
        _logger.debug('Make server request to select personal mission %s', ', '.join([ str(idn) for idn in questIDs ]))
        BigWorld.player().selectPersonalMissions(questIDs, self._branch, lambda code, errStr: self._response(code, callback, errStr=errStr))

    def _errorHandler(self, code, errStr='', ctx=None):
        errorI18nKey = '%s/server_error' % self._getMessagePrefix()
        questNames = ', '.join(self._getQuestsNames())
        if errStr:
            errorI18nKey = '%s/%s' % (errorI18nKey, errStr)
            if errStr == 'LOCKED_BY_VEHICLE_QUEST':
                questNames = ctx.get('questName', '')
        return makeI18nError(errorI18nKey, questNames=questNames)


class PMDiscard(_PMRequest):

    def __init__(self, personalMission, branch):
        quests = [personalMission]
        super(PMDiscard, self).__init__(quests, branch)
        self.addPlugins([plugins.PMDiscardConfirmator(personalMission), plugins.PMLockedByVehicle(branch, quests)])

    def _request(self, callback):
        questIDs = self._getQuestsData(methodcaller=operator.methodcaller('getID'))
        _logger.debug('Make server request to discard personal mission %s', str(questIDs[0]))
        BigWorld.player().resetPersonalMissions(questIDs, self._branch, lambda code, errStr: self._response(code, callback, errStr=errStr))

    def _successHandler(self, code, ctx=None):
        questName = self._getQuestsNames()[0]
        return makeI18nSuccess('%s/success' % self._getMessagePrefix(), quest=questName)

    def _getMessagePrefix(self):
        pass


class PMPause(_PMRequest):

    def __init__(self, personalMission, enable, branch):
        quests = [personalMission]
        self._enable = enable
        super(PMPause, self).__init__(quests, branch)

    def _request(self, callback):
        questIDs = self._getQuestsData(methodcaller=operator.methodcaller('getID'))
        _logger.debug('Make server request to pause personal mission %s', str(questIDs[0]))
        BigWorld.player().pausePersonalMissions(questIDs, self._branch, self._enable, lambda code, errStr: self._response(code, callback, errStr=errStr))

    def _successHandler(self, code, ctx=None):
        questName = self._getQuestsNames()[0]
        enable = 'pause' if self._enable else 'unpause'
        return makeI18nSuccess('%s/success_%s' % (self._getMessagePrefix(), enable), quest=questName)

    def _getMessagePrefix(self):
        pass


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
        return makeI18nError('%s/server_error/%s' % (self._getMessagePrefix(), errStr), defaultSysMsgKey='%s/server_error' % self._getMessagePrefix())

    def _request(self, callback):
        LOG_DEBUG('Make server request to get reward', self.__quest, self.__needTankman, self.__nationID, self.__inNationID, self.__role)
        BigWorld.player().getPersonalMissionReward(self.__quest.getID(), self.__quest.getQuestBranch(), self.__needTankman, self.__nationID, self.__inNationID, tankmen.SKILL_INDICES[self.__role], lambda code, errStr: self._response(code, callback, errStr=errStr))


class PMGetTankwomanReward(_PMGetReward):

    def __init__(self, personalMission, nationID, inNationID, role):
        super(PMGetTankwomanReward, self).__init__(personalMission, True, nationID, inNationID, role)

    def _getMessagePrefix(self):
        pass


class PMGetReward(_PMGetReward):

    def __init__(self, personalMission):
        super(PMGetReward, self).__init__(personalMission, False, 0, 0, 'commander')


class PMPawn(Processor):

    def __init__(self, personalMission):
        super(PMPawn, self).__init__((plugins.PMPawnConfirmator(personalMission), plugins.PMPawnValidator([personalMission]), plugins.PMFreeTokensValidator(personalMission)))
        self.__quest = personalMission

    def _getMessagePrefix(self):
        pass

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('%s/server_error/%s' % (self._getMessagePrefix(), errStr), defaultSysMsgKey='%s/server_error' % self._getMessagePrefix())

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess('%s/success' % self._getMessagePrefix(), questName=self.__quest.getShortUserName(), count=self.__quest.getPawnCost())

    def _request(self, callback):
        LOG_DEBUG('Make server request to pawn quest', self.__quest)
        BigWorld.player().pawnFreeAwardList(self.__quest.getType(), self.__quest.getID(), lambda code: self._response(code, callback))
