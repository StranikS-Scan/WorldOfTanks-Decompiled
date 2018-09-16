# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/quests.py
import operator
import BigWorld
from debug_utils import LOG_DEBUG
from gui.shared.gui_items.processors import Processor, makeI18nError, makeI18nSuccess, plugins
from helpers import i18n
from items import tankmen, ITEM_TYPES
from personal_missions import PM_BRANCH

class _PersonalMissionsSelect(Processor):

    def __init__(self, personalMissions, events_cache, questBranch):
        self.__quests = personalMissions
        self.__questBranch = questBranch
        deselectedQuests = set(events_cache.getSelectedQuests().values()).difference(set(personalMissions))
        super(_PersonalMissionsSelect, self).__init__((plugins.PersonalMissionValidator(personalMissions), self._getLockedByVehicleValidator(deselectedQuests)))

    @staticmethod
    def _getLockedByVehicleValidator(quests):
        raise NotImplementedError

    def _getMessagePrefix(self):
        raise NotImplementedError

    def _errorHandler(self, code, errStr='', ctx=None):
        errorI18nKey = '%s/server_error' % self._getMessagePrefix()
        if errStr:
            errorI18nKey = '%s/%s' % (errorI18nKey, errStr)
        return makeI18nError(errorI18nKey, questNames=', '.join(self._getQuestsNames()))

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess('%s/success' % self._getMessagePrefix(), questNames=', '.join(self._getQuestsNames()))

    def _request(self, callback):
        questIDs = self._getQuestsData(methodcaller=operator.methodcaller('getID'))
        LOG_DEBUG('Make server request to select personal mission', questIDs)
        BigWorld.player().selectPersonalMissions(questIDs, self.__questBranch, lambda code, errStr: self._response(code, callback, errStr=errStr))

    def _getQuestsData(self, methodcaller):
        return [ methodcaller(q) for q in self.__quests ]

    def _getQuestsNames(self):
        return self._getQuestsData(methodcaller=operator.methodcaller('getUserName'))


class PersonalMissionSelect(_PersonalMissionsSelect):

    def __init__(self, quest, events_cache, questsBranch):
        quests, oldQuest = self._removeFromSameChain(events_cache.getSelectedQuests().values(), quest)
        super(PersonalMissionSelect, self).__init__(quests, events_cache, questsBranch)
        self.addPlugins([plugins.PersonalMissionSlotsValidator(events_cache.questsProgress, removedCount=int(oldQuest is not None)), plugins.PersonalMissionSelectConfirmator(quest, oldQuest, isEnabled=oldQuest is not None and oldQuest != quest)])
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


class RandomQuestSelect(PersonalMissionSelect):

    def __init__(self, quest, events_cache):
        super(RandomQuestSelect, self).__init__(quest, events_cache, PM_BRANCH.REGULAR)

    @staticmethod
    def _getLockedByVehicleValidator(quests):
        return plugins.PersonalMissionsLockedByVehicle(quests)


class _PersonalMissionRefuse(_PersonalMissionsSelect):

    def __init__(self, quest, events_cache, questBranch):
        selectedQuests = events_cache.getSelectedQuests()
        selectedQuests.pop(quest.getID(), None)
        super(_PersonalMissionRefuse, self).__init__(selectedQuests.values(), events_cache, questBranch)
        return

    def _successHandler(self, code, ctx=None):
        questsNames = self._getQuestsNames()
        if questsNames:
            quests = i18n.makeString('#system_messages:%s/quests' % self._getMessagePrefix(), questNames=', '.join(questsNames))
        else:
            quests = i18n.makeString('#system_messages:%s/no_quests' % self._getMessagePrefix())
        return makeI18nSuccess('%s/success' % self._getMessagePrefix(), quests=quests)

    def _getMessagePrefix(self):
        pass


class RandomQuestRefuse(_PersonalMissionRefuse):

    def __init__(self, quest, events_cache):
        super(RandomQuestRefuse, self).__init__(quest, events_cache, PM_BRANCH.REGULAR)

    @staticmethod
    def _getLockedByVehicleValidator(quests):
        return plugins.PersonalMissionsLockedByVehicle(quests)


class _PersonalMissionsGetReward(Processor):

    def __init__(self, personalMission, needTankman, nationID, inNationID, role):
        plugs = [plugins.PersonalMissionRewardValidator(personalMission)]
        if needTankman:
            plugs.insert(0, plugins.VehicleCrewLockedValidator(self.itemsCache.items.getItem(ITEM_TYPES.vehicle, nationID, inNationID)))
        super(_PersonalMissionsGetReward, self).__init__(tuple(plugs))
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


class PersonalMissionsGetTankwomanReward(_PersonalMissionsGetReward):

    def __init__(self, personalMission, nationID, inNationID, role):
        super(PersonalMissionsGetTankwomanReward, self).__init__(personalMission, True, nationID, inNationID, role)

    def _getMessagePrefix(self):
        pass


class PersonalMissionsGetRegularReward(_PersonalMissionsGetReward):

    def __init__(self, personalMission):
        super(PersonalMissionsGetRegularReward, self).__init__(personalMission, False, 0, 0, 'commander')


class PersonalMissionPawn(Processor):

    def __init__(self, personalMission):
        plugs = (plugins.PersonalMissionPawnConfirmator(personalMission), plugins.PersonalMissionPawnValidator([personalMission]), plugins.PersonalMissionFreeTokensValidator(personalMission))
        super(PersonalMissionPawn, self).__init__(plugs)
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
