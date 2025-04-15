# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/daily/daily_quests_subview_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.daily.daily_quests_mark_seen_model import DailyQuestsMarkSeenModel
from gui.impl.gen.view_models.views.lobby.daily.daily_quests_premium_model import DailyQuestsPremiumModel
from gui.impl.gen.view_models.views.lobby.daily.daily_quests_regular_model import DailyQuestsRegularModel
from gui.impl.gen.view_models.views.lobby.daily.epic_quest_model import EpicQuestModel

class DailyQuestsSubviewModel(ViewModel):
    __slots__ = ('onClose', 'onReroll', 'onInfoToggle', 'onBuyPremiumBtnClick', 'onRerollEnabled')

    def __init__(self, properties=8, commands=5):
        super(DailyQuestsSubviewModel, self).__init__(properties=properties, commands=commands)

    @property
    def regular(self):
        return self._getViewModel(0)

    @staticmethod
    def getRegularType():
        return DailyQuestsRegularModel

    @property
    def premium(self):
        return self._getViewModel(1)

    @staticmethod
    def getPremiumType():
        return DailyQuestsPremiumModel

    @property
    def epic(self):
        return self._getViewModel(2)

    @staticmethod
    def getEpicType():
        return EpicQuestModel

    @property
    def unseenQuests(self):
        return self._getViewModel(3)

    @staticmethod
    def getUnseenQuestsType():
        return DailyQuestsMarkSeenModel

    def getCurrentTabIdx(self):
        return self._getNumber(4)

    def setCurrentTabIdx(self, value):
        self._setNumber(4, value)

    def getInfoVisible(self):
        return self._getBool(5)

    def setInfoVisible(self, value):
        self._setBool(5, value)

    def getIsBattlePassActive(self):
        return self._getBool(6)

    def setIsBattlePassActive(self, value):
        self._setBool(6, value)

    def getIsComp7Active(self):
        return self._getBool(7)

    def setIsComp7Active(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(DailyQuestsSubviewModel, self)._initialize()
        self._addViewModelProperty('regular', DailyQuestsRegularModel())
        self._addViewModelProperty('premium', DailyQuestsPremiumModel())
        self._addViewModelProperty('epic', EpicQuestModel())
        self._addViewModelProperty('unseenQuests', DailyQuestsMarkSeenModel())
        self._addNumberProperty('currentTabIdx', 0)
        self._addBoolProperty('infoVisible', False)
        self._addBoolProperty('isBattlePassActive', False)
        self._addBoolProperty('isComp7Active', False)
        self.onClose = self._addCommand('onClose')
        self.onReroll = self._addCommand('onReroll')
        self.onInfoToggle = self._addCommand('onInfoToggle')
        self.onBuyPremiumBtnClick = self._addCommand('onBuyPremiumBtnClick')
        self.onRerollEnabled = self._addCommand('onRerollEnabled')
