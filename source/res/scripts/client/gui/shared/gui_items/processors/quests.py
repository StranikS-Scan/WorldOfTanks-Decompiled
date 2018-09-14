# Embedded file name: scripts/client/gui/shared/gui_items/processors/quests.py
import operator
import BigWorld
from debug_utils import LOG_DEBUG
from items import tankmen
from gui.shared.gui_items.processors import Processor, makeI18nError, makeI18nSuccess, plugins
from potapov_quests import PQ_BRANCH

class _PotapovQuestsSelect(Processor):

    def __init__(self, potapovQuestItems, events_cache, questBranch):
        self.__quests = potapovQuestItems
        self.__questBranch = questBranch
        deselectedQuests = set(events_cache.getSelectedQuests().values()).difference(set(potapovQuestItems))
        super(_PotapovQuestsSelect, self).__init__((plugins.PotapovQuestValidator(potapovQuestItems), self._getLockedByVehicleValidator()(deselectedQuests)))

    @staticmethod
    def _getLockedByVehicleValidator():
        raise NotImplemented

    def _getMessagePrefix(self):
        raise NotImplemented

    def _errorHandler(self, code, errStr = '', ctx = None):
        errorI18nKey = '%s/server_error' % self._getMessagePrefix()
        if len(errStr):
            errorI18nKey = '%s/%s' % (errorI18nKey, errStr)
        return makeI18nError(errorI18nKey, questNames=', '.join(self.__getQuestsNames()))

    def _successHandler(self, code, ctx = None):
        return makeI18nSuccess('%s/success' % self._getMessagePrefix(), questNames=', '.join(self.__getQuestsNames()))

    def _request(self, callback):
        questIDs = self.__getQuestsData(methodcaller=operator.methodcaller('getID'))
        LOG_DEBUG('Make server request to select potapov quests', questIDs)
        BigWorld.player().selectPotapovQuests(questIDs, self.__questBranch, lambda code, errStr: self._response(code, callback, errStr=errStr))

    def __getQuestsData(self, methodcaller):
        return [ methodcaller(q) for q in self.__quests ]

    def __getQuestsNames(self):
        return self.__getQuestsData(methodcaller=operator.methodcaller('getUserName'))


class PotapovQuestSelect(_PotapovQuestsSelect):

    def __init__(self, quest, events_cache, questsBranch):
        quests, oldQuest = self._removeFromSameChain(events_cache.getSelectedQuests().values(), quest)
        super(PotapovQuestSelect, self).__init__(quests, events_cache, questsBranch)
        self.addPlugins([plugins.PotapovQuestSlotsValidator(events_cache.questsProgress, removedCount=int(oldQuest is not None)), plugins.PotapovQuestSelectConfirmator(quest, oldQuest, isEnabled=oldQuest is not None)])
        return

    def _getMessagePrefix(self):
        return 'potapovQuests/select'

    def _removeFromSameChain(self, quests, newQuest):
        result = [newQuest]
        removedQuest = None
        for quest in quests:
            if quest.getChainID() != newQuest.getChainID():
                result.append(quest)
            else:
                removedQuest = quest

        return (result, removedQuest)


class RandomQuestSelect(PotapovQuestSelect):

    def __init__(self, quest, events_cache):
        super(RandomQuestSelect, self).__init__(quest, events_cache, PQ_BRANCH.REGULAR)

    @staticmethod
    def _getLockedByVehicleValidator():
        return plugins.RandomQuestsLockedByVehicle


class FalloutQuestSelect(PotapovQuestSelect):

    def __init__(self, quest, events_cache):
        super(FalloutQuestSelect, self).__init__(quest, events_cache, PQ_BRANCH.FALLOUT)

    @staticmethod
    def _getLockedByVehicleValidator():
        return plugins.FalloutQuestsLockedByVehicle


class _PotapovQuestRefuse(_PotapovQuestsSelect):

    def __init__(self, quest, events_cache, questBranch):
        selectedQuests = events_cache.getSelectedQuests()
        selectedQuests.pop(quest.getID(), None)
        super(_PotapovQuestRefuse, self).__init__(selectedQuests.values(), events_cache, questBranch)
        return

    def _getMessagePrefix(self):
        return 'potapovQuests/refuse'


class RandomQuestRefuse(_PotapovQuestRefuse):

    def __init__(self, quest, events_cache):
        super(RandomQuestRefuse, self).__init__(quest, events_cache, PQ_BRANCH.REGULAR)

    @staticmethod
    def _getLockedByVehicleValidator():
        return plugins.RandomQuestsLockedByVehicle


class FalloutQuestRefuse(_PotapovQuestRefuse):

    def __init__(self, quest, events_cache):
        super(FalloutQuestRefuse, self).__init__(quest, events_cache, PQ_BRANCH.FALLOUT)

    @staticmethod
    def _getLockedByVehicleValidator():
        return plugins.FalloutQuestsLockedByVehicle


class _PotapovQuestsGetReward(Processor):

    def __init__(self, potapovQuestItem, needTankman, nationID, inNationID, role):
        super(_PotapovQuestsGetReward, self).__init__((plugins.PotapovQuestValidator([potapovQuestItem]), plugins.PotapovQuestRewardValidator(potapovQuestItem)))
        self.__quest = potapovQuestItem
        self.__nationID = nationID
        self.__inNationID = inNationID
        self.__role = role
        self.__needTankman = needTankman

    def _getMessagePrefix(self):
        return 'potapovQuests/reward/regular'

    def _errorHandler(self, code, errStr = '', ctx = None):
        if len(errStr):
            return makeI18nError('%s/server_error/%s' % (self._getMessagePrefix(), errStr))
        return makeI18nError('%s/server_error' % self._getMessagePrefix())

    def _successHandler(self, code, ctx = None):
        return makeI18nSuccess('%s/success' % self._getMessagePrefix())

    def _request(self, callback):
        LOG_DEBUG('Make server request to get reward', self.__quest, self.__needTankman, self.__nationID, self.__inNationID, self.__role)
        BigWorld.player().getPotapovQuestReward(self.__quest.getID(), self.__quest.getQuestBranch(), self.__needTankman, self.__nationID, self.__inNationID, tankmen.SKILL_INDICES[self.__role], lambda code, errStr: self._response(code, callback, errStr=errStr))


class PotapovQuestsGetTankwomanReward(_PotapovQuestsGetReward):

    def __init__(self, potapovQuestItem, nationID, inNationID, role):
        super(PotapovQuestsGetTankwomanReward, self).__init__(potapovQuestItem, True, nationID, inNationID, role)

    def _getMessagePrefix(self):
        return 'potapovQuests/reward/tankwoman'


class PotapovQuestsGetRegularReward(_PotapovQuestsGetReward):

    def __init__(self, potapovQuestItem):
        super(PotapovQuestsGetRegularReward, self).__init__(potapovQuestItem, False, 0, 0, 'commander')
