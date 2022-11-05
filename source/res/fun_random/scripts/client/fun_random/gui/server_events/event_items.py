# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/server_events/event_items.py
from fun_random.gui.feature.fun_constants import FEP_PROGRESSION_TRIGGER_QUEST_ID
from fun_random.gui.feature.util.fun_helpers import getProgressionNameByTrigger
from fun_random.gui.feature.util.fun_mixins import FunProgressionWatcher
from fun_random.gui.feature.util.fun_wrappers import hasActiveProgression
from fun_random.gui.Scaleform.daapi.view.lobby.server_events.events_helpers import FunProgressionQuestPostBattleInfo
from gui.server_events.event_items import Quest, IQuestBuilder

class FunProgressionTriggerQuest(Quest, FunProgressionWatcher):

    def __init__(self, qID, data, progress=None):
        super(FunProgressionTriggerQuest, self).__init__(qID, data, progress)
        self.__pName = getProgressionNameByTrigger(qID)

    @classmethod
    def postBattleInfo(cls):
        return FunProgressionQuestPostBattleInfo

    @classmethod
    def showMissionAction(cls):
        return cls.showActiveProgressionPage

    @hasActiveProgression(defReturn=False)
    def isCompleted(self, progress=None):
        return self.getBonusCount(progress=progress) in self.getActiveProgression().config.executors

    @hasActiveProgression(defReturn=False)
    def isForActiveProgression(self):
        return self.__pName == self.getActiveProgression().config.name

    def isShowedPostBattle(self):
        return super(FunProgressionTriggerQuest, self).isShowedPostBattle() and self.isForActiveProgression()

    def getBonusCount(self, groupByKey=None, progress=None):
        bonusCount = super(FunProgressionTriggerQuest, self).getBonusCount(groupByKey, progress)
        return bonusCount if self.isForActiveProgression() else 0


class FunProgressionTriggerQuestBuilder(IQuestBuilder):

    @classmethod
    def isSuitableQuest(cls, questType, qID):
        return qID.startswith(FEP_PROGRESSION_TRIGGER_QUEST_ID)

    @classmethod
    def buildQuest(cls, questType, qID, data, progress=None, expiryTime=None):
        return FunProgressionTriggerQuest(qID, data, progress)
