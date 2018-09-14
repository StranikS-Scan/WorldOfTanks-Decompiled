# Embedded file name: scripts/client/gui/shared/gui_items/processors/quests.py
import operator
import BigWorld
from debug_utils import LOG_DEBUG
from items import tankmen
from gui.server_events import g_eventsCache
from gui.shared.gui_items.processors import Processor, makeI18nError, makeI18nSuccess, plugins

class _PotapovQuestsSelect(Processor):

    def __init__(self, potapovQuestItems):
        self.__quests = potapovQuestItems
        deselectedQuests = set(g_eventsCache.potapov.getSelectedQuests().values()).difference(set(potapovQuestItems))
        super(_PotapovQuestsSelect, self).__init__((plugins.PotapovQuestValidator(potapovQuestItems), plugins.PotapovQuestsLockedByVehicle(deselectedQuests)))

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
        BigWorld.player().selectPotapovQuests(questIDs, lambda code, errStr: self._response(code, callback, errStr=errStr))

    def __getQuestsData(self, methodcaller):
        return [ methodcaller(q) for q in self.__quests ]

    def __getQuestsNames(self):
        return self.__getQuestsData(methodcaller=operator.methodcaller('getUserName'))


class PotapovQuestSelect(_PotapovQuestsSelect):

    def __init__(self, quest):
        quests, oldQuest = self._removeFromSameChain(g_eventsCache.potapov.getSelectedQuests().values(), quest)
        super(PotapovQuestSelect, self).__init__(quests)
        self.addPlugins([plugins.PotapovQuestSlotsValidator(), plugins.PotapovQuestSelectConfirmator(quest, oldQuest, isEnabled=oldQuest is not None)])
        return

    def _getMessagePrefix(self):
        return 'potapovQuests/select'

    def _removeFromSameChain(self, quests, newQuest):
        result = [newQuest]
        removedQuest = None
        for quest in quests:
            if quest.getChainID() != newQuest.getChainID() or quest.getTileID() != newQuest.getTileID():
                result.append(quest)
            else:
                removedQuest = quest

        return (result, removedQuest)


class PotapovQuestRefuse(_PotapovQuestsSelect):

    def __init__(self, quest):
        selectedQuests = g_eventsCache.potapov.getSelectedQuests()
        selectedQuests.pop(quest.getID(), None)
        super(PotapovQuestRefuse, self).__init__(selectedQuests.values())
        return

    def _getMessagePrefix(self):
        return 'potapovQuests/refuse'


class _PotapovQuestsGetReward(Processor):

    def __init__(self, potapovQuestItem, needTankman, nationID, innationID, role):
        super(_PotapovQuestsGetReward, self).__init__((plugins.PotapovQuestValidator([potapovQuestItem]), plugins.PotapovQuestRewardValidator(potapovQuestItem)))
        self.__quest = potapovQuestItem
        self.__nationID = nationID
        self.__innationID = innationID
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
        LOG_DEBUG('Make server request to get reward', self.__quest, self.__needTankman, self.__nationID, self.__innationID, self.__role)
        BigWorld.player().getPotapovQuestReward(self.__quest.getID(), self.__needTankman, self.__nationID, self.__innationID, tankmen.SKILL_INDICES[self.__role], lambda code, errStr: self._response(code, callback, errStr=errStr))


class PotapovQuestsGetTankwomanReward(_PotapovQuestsGetReward):

    def __init__(self, potapovQuestItem, nationID, innationID, role):
        super(PotapovQuestsGetTankwomanReward, self).__init__(potapovQuestItem, True, nationID, innationID, role)

    def _getMessagePrefix(self):
        return 'potapovQuests/reward/tankwoman'


class PotapovQuestsGetRegularReward(_PotapovQuestsGetReward):

    def __init__(self, potapovQuestItem):
        super(PotapovQuestsGetRegularReward, self).__init__(potapovQuestItem, False, 0, 0, 'commander')
