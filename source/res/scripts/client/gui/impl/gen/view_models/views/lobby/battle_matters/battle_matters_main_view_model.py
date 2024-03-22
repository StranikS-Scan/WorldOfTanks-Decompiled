# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_matters/battle_matters_main_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.battle_matters.quest_progress_model import QuestProgressModel
from gui.impl.gen.view_models.views.lobby.battle_matters.quest_view_model import QuestViewModel

class BattleMattersMainViewModel(ViewModel):
    __slots__ = ('onShowView', 'onShowManual', 'onShowManualForQuest', 'onShowAnimForQuest', 'onShowMainReward', 'onSelectDelayedReward', 'onClose')
    ARG_QUEST_ID = 'questID'
    NAME_VEHICLE_REWARD = 'vehicle'
    NAME_TOKEN_REWARD = 'token'

    def __init__(self, properties=3, commands=7):
        super(BattleMattersMainViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def questProgress(self):
        return self._getViewModel(0)

    @staticmethod
    def getQuestProgressType():
        return QuestProgressModel

    def getIsRewardsViewOpen(self):
        return self._getBool(1)

    def setIsRewardsViewOpen(self, value):
        self._setBool(1, value)

    def getQuests(self):
        return self._getArray(2)

    def setQuests(self, value):
        self._setArray(2, value)

    @staticmethod
    def getQuestsType():
        return QuestViewModel

    def _initialize(self):
        super(BattleMattersMainViewModel, self)._initialize()
        self._addViewModelProperty('questProgress', QuestProgressModel())
        self._addBoolProperty('isRewardsViewOpen', False)
        self._addArrayProperty('quests', Array())
        self.onShowView = self._addCommand('onShowView')
        self.onShowManual = self._addCommand('onShowManual')
        self.onShowManualForQuest = self._addCommand('onShowManualForQuest')
        self.onShowAnimForQuest = self._addCommand('onShowAnimForQuest')
        self.onShowMainReward = self._addCommand('onShowMainReward')
        self.onSelectDelayedReward = self._addCommand('onSelectDelayedReward')
        self.onClose = self._addCommand('onClose')
