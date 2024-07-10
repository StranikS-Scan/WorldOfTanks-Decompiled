# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/server_events/event_items.py
from fun_random.gui.feature.fun_constants import FEP_PROGRESSION_TRIGGER_QUEST_ID, PROGRESSION_COUNTER_TEMPLATE, FEP_PROGRESSION_ALT_TRIGGER_QUEST_ID, FEP_PROGRESSION_UNLIMITED_TRIGGER_QUEST_ID, FEP_PROGRESSION_UNLIMITED_ALT_TRIGGER_QUEST_ID, PROGRESSION_UNLIMITED_COUNTER_TEMPLATE
from fun_random.gui.feature.util.fun_helpers import getProgressionNameByTrigger, getIdByTrigger, isFunProgressionTrigger, isFunProgressionUnlimitedTrigger
from fun_random.gui.feature.util.fun_mixins import FunProgressionWatcher
from fun_random.gui.feature.util.fun_wrappers import hasActiveProgression
from gui.server_events.event_items import Quest, IQuestBuilder

class FunProgressionTriggerQuest(Quest, FunProgressionWatcher):
    COUNTER_TEMPLATE = PROGRESSION_COUNTER_TEMPLATE
    MAIN_TRIGGER_QUEST_ID = FEP_PROGRESSION_TRIGGER_QUEST_ID
    ALT_TRIGGER_QUEST_ID = FEP_PROGRESSION_ALT_TRIGGER_QUEST_ID

    def __init__(self, qID, data, progress=None):
        super(FunProgressionTriggerQuest, self).__init__(qID, data, progress)
        self.__pName = getProgressionNameByTrigger(qID)
        self.__triggerId = getIdByTrigger(qID)
        self.__counterName = self.COUNTER_TEMPLATE.format(self.__pName)
        self.__altQuest = None
        return

    def isMain(self):
        return self.getID().startswith(self.MAIN_TRIGGER_QUEST_ID)

    def findAndSaveAltQuest(self, quests):
        if self.__altQuest is None:
            self.__altQuest = quests.get((self.ALT_TRIGGER_QUEST_ID + '_{}_{}').format(self.__pName, self.__triggerId))
        return

    def getAltQuest(self):
        return self.__altQuest

    @classmethod
    def showMissionAction(cls):
        return cls.showActiveProgressionPage

    @hasActiveProgression(defReturn=False)
    def isForActiveProgression(self):
        return self.__pName == self.getActiveProgression().config.name

    def isShowedPostBattle(self):
        return super(FunProgressionTriggerQuest, self).isShowedPostBattle() and self.isForActiveProgression()

    def getCurrentProgress(self):
        altQuest = self.getAltQuest()
        return self.getBonusCount() + altQuest.getBonusCount() if altQuest else self.getBonusCount()

    def getTotalProgress(self):
        return self.bonusCond.getBonusLimit()

    def getDetailedProgress(self):
        altQuest = self.getAltQuest()
        progress = {altQuest.getID(): altQuest.getBonusCount()} if altQuest else {}
        progress.update({self.getID(): self.getBonusCount()})
        return progress

    def getEarnedPoints(self):
        points = self.getBonusCounterNumber() * self.getBonusCount()
        altQuest = self.getAltQuest()
        return points + altQuest.getEarnedPoints() if altQuest else points

    def getBonusCounterNumber(self):
        bonuses = self.getBonuses('tokens')
        for bonus in bonuses:
            for tID, data in bonus.getTokens().iteritems():
                if tID == self.__counterName:
                    return data.count

    def getIconKey(self):
        if self.isForActiveProgression():
            for trigger in self.getActiveProgression().config.triggers:
                if trigger['id'] == self.__triggerId:
                    return trigger['condition']

    def isCompleted(self, progress=None):
        return self.getCurrentProgress() >= self.getTotalProgress() if self.getAltQuest() else super(FunProgressionTriggerQuest, self).isCompleted(progress)


class FunProgressionUnlimitedTriggerQuest(FunProgressionTriggerQuest):
    COUNTER_TEMPLATE = PROGRESSION_UNLIMITED_COUNTER_TEMPLATE
    MAIN_TRIGGER_QUEST_ID = FEP_PROGRESSION_UNLIMITED_TRIGGER_QUEST_ID
    ALT_TRIGGER_QUEST_ID = FEP_PROGRESSION_UNLIMITED_ALT_TRIGGER_QUEST_ID

    def getIconKey(self):
        return self.getActiveProgression().config.unlimitedTrigger['condition'] if self.isForActiveProgression() else ''


class FunProgressionTriggerQuestBuilder(IQuestBuilder):

    @classmethod
    def isSuitableQuest(cls, questType, qID):
        return isFunProgressionTrigger(qID)

    @classmethod
    def buildQuest(cls, questType, qID, data, progress=None, expiryTime=None):
        return FunProgressionTriggerQuest(qID, data, progress)


class FunProgressionUnlimitedTriggerQuestBuilder(IQuestBuilder):

    @classmethod
    def isSuitableQuest(cls, questType, qID):
        return isFunProgressionUnlimitedTrigger(qID)

    @classmethod
    def buildQuest(cls, questType, qID, data, progress=None, expiryTime=None):
        return FunProgressionUnlimitedTriggerQuest(qID, data, progress)
