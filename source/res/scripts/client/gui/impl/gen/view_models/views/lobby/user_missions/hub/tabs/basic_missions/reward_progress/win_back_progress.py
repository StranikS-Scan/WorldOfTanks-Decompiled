# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/user_missions/hub/tabs/basic_missions/reward_progress/win_back_progress.py
from enum import Enum
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.user_missions.hub.tabs.basic_missions.reward_progress.quest_progress_model import QuestProgressModel
from gui.impl.gen.view_models.views.lobby.user_missions.hub.tabs.basic_missions.reward_progress.win_back_quest_model import WinBackQuestModel

class OffersState(Enum):
    AVAILABLE = 'available'
    DISABLED = 'disabled'
    NO_OFFERS = 'no_offers'


class WinBackProgress(QuestProgressModel):
    __slots__ = ('onTakeReward', 'onTakeAllRewards')

    def __init__(self, properties=8, commands=2):
        super(WinBackProgress, self).__init__(properties=properties, commands=commands)

    def getIsBattlePassActive(self):
        return self._getBool(4)

    def setIsBattlePassActive(self, value):
        self._setBool(4, value)

    def getTimeLeftToClaim(self):
        return self._getNumber(5)

    def setTimeLeftToClaim(self, value):
        self._setNumber(5, value)

    def getOffersState(self):
        return OffersState(self._getString(6))

    def setOffersState(self, value):
        self._setString(6, value.value)

    def getQuests(self):
        return self._getArray(7)

    def setQuests(self, value):
        self._setArray(7, value)

    @staticmethod
    def getQuestsType():
        return WinBackQuestModel

    def _initialize(self):
        super(WinBackProgress, self)._initialize()
        self._addBoolProperty('isBattlePassActive', False)
        self._addNumberProperty('timeLeftToClaim', 0)
        self._addStringProperty('offersState')
        self._addArrayProperty('quests', Array())
        self.onTakeReward = self._addCommand('onTakeReward')
        self.onTakeAllRewards = self._addCommand('onTakeAllRewards')
