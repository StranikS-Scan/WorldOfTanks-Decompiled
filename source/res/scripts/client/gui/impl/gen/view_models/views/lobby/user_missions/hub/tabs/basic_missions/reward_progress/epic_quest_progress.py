# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/user_missions/hub/tabs/basic_missions/reward_progress/epic_quest_progress.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.user_missions.hub.tabs.basic_missions.reward_progress.epic_quests_bonus_model import EpicQuestsBonusModel
from gui.impl.gen.view_models.views.lobby.user_missions.hub.tabs.basic_missions.reward_progress.quest_progress_model import QuestProgressModel

class EpicQuestProgress(QuestProgressModel):
    __slots__ = ('onTakeWinBackReward',)

    def __init__(self, properties=6, commands=1):
        super(EpicQuestProgress, self).__init__(properties=properties, commands=commands)

    def getBonuses(self):
        return self._getArray(4)

    def setBonuses(self, value):
        self._setArray(4, value)

    @staticmethod
    def getBonusesType():
        return EpicQuestsBonusModel

    def getWinBackTimeLeft(self):
        return self._getNumber(5)

    def setWinBackTimeLeft(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(EpicQuestProgress, self)._initialize()
        self._addArrayProperty('bonuses', Array())
        self._addNumberProperty('winBackTimeLeft', 0)
        self.onTakeWinBackReward = self._addCommand('onTakeWinBackReward')
